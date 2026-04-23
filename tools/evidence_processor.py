#!/usr/bin/env python3
"""
🔍 RMI Evidence Processing Pipeline
==================================
Automated extraction and processing of investigation evidence:
- ZIP archive extraction with categorization
- OCR processing for screenshots/images
- Wallet address extraction from all sources
- Supabase integration for evidence storage

Author: RMI System
Version: 1.0.0
"""

import os
import re
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

# Try to import OCR libraries
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️  Tesseract not available. Install with: apt-get install tesseract-ocr")


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

@dataclass
class EvidenceConfig:
    """Configuration for evidence processing"""
    # Directories
    dumps_dir: str = "/root/dumps/investigation-20260409/mixed"
    extracted_dir: str = "/root/rmi/tools/extracted"
    ocr_output_dir: str = "/root/rmi/tools/ocr_output"
    
    # Processing settings
    max_zip_size_mb: int = 500
    max_workers: int = 4
    ocr_confidence_threshold: float = 0.6
    
    # Wallet patterns by chain
    wallet_patterns = {
        'solana': r'[1-9A-HJ-NP-Za-km-z]{32,44}',
        'ethereum': r'0x[a-fA-F0-9]{40}',
        'bsc': r'0x[a-fA-F0-9]{40}',
        'base': r'0x[a-fA-F0-9]{40}',
        'bitcoin': r'(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}'
    }


# ═══════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════

@dataclass
class ExtractedFile:
    """Represents a single extracted file"""
    filename: str
    original_archive: str
    category: str  # 'critical', 'useful', 'suspicious', 'useless'
    file_type: str
    file_hash: str
    size_bytes: int
    wallets_found: List[str]
    extracted_at: str
    file_path: str


@dataclass
class OCResult:
    """OCR extraction result"""
    image_path: str
    extracted_text: str
    confidence: float
    wallets_found: List[Dict[str, Any]]  # {address, chain, context}
    processed_at: str


@dataclass
class ProcessingSummary:
    """Summary of evidence processing"""
    total_archives: int
    total_files_extracted: int
    total_images_processed: int
    total_wallets_found: int
    wallets_by_chain: Dict[str, int]
    categories: Dict[str, int]
    errors: List[str]
    processing_time_seconds: float


# ═══════════════════════════════════════════════════════════
# EVIDENCE EXTRACTOR
# ═══════════════════════════════════════════════════════════

class EvidenceExtractor:
    """
    Extract and categorize evidence from ZIP archives
    """
    
    # File type categories
    CATEGORIES = {
        'critical': ['.pdf', '.doc', '.docx', '.txt', '.md'],  # Documents with evidence
        'useful': ['.csv', '.xls', '.xlsx', '.json', '.sql'],  # Structured data
        'suspicious': ['.exe', '.dll', '.so', '.sh', '.bat'],  # Executables
        'media': ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov'],  # Media
        'code': ['.py', '.js', '.ts', '.sol', '.rs', '.go'],  # Source code
        'config': ['.env', '.conf', '.config', '.yaml', '.yml', '.xml'],  # Configs
        'archive': ['.zip', '.tar', '.gz', '.rar'],  # Nested archives
        'useless': ['.tmp', '.log', '.cache', '.DS_Store']  # System files
    }
    
    def __init__(self, config: EvidenceConfig = None):
        self.config = config or EvidenceConfig()
        self.extracted_files: List[ExtractedFile] = []
        self.errors: List[str] = []
        
        # Create output directories
        os.makedirs(self.config.extracted_dir, exist_ok=True)
        for cat in self.CATEGORIES.keys():
            os.makedirs(os.path.join(self.config.extracted_dir, cat), exist_ok=True)
    
    def _get_category(self, filename: str) -> str:
        """Determine file category based on extension"""
        ext = Path(filename).suffix.lower()
        
        for category, extensions in self.CATEGORIES.items():
            if ext in extensions:
                return category
        
        return 'useful'  # Default category
    
    def _calculate_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _extract_wallets(self, file_path: str, file_type: str) -> List[str]:
        """Extract wallet addresses from file content"""
        wallets = []
        
        # Try to read as text
        try:
            if file_type in ['.txt', '.md', '.csv', '.json', '.py', '.js', '.sol', '.env', '.conf', '.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for chain, pattern in self.config.wallet_patterns.items():
                    matches = re.findall(pattern, content)
                    wallets.extend(matches)
        except Exception as e:
            pass  # Binary or unreadable file
        
        return list(set(wallets))  # Remove duplicates
    
    def _extract_archive(self, zip_path: str, extract_to: str) -> List[str]:
        """Extract a single ZIP archive"""
        extracted_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check total size before extraction
                total_size = sum(zinfo.file_size for zinfo in zip_ref.filelist)
                if total_size > self.config.max_zip_size_mb * 1024 * 1024:
                    self.errors.append(f"ZIP too large: {zip_path}")
                    return []
                
                # Extract all files
                zip_ref.extractall(extract_to)
                
                # Process each extracted file
                for root, dirs, files in os.walk(extract_to):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, extract_to)
                        
                        category = self._get_category(file)
                        file_type = Path(file).suffix.lower()
                        file_hash = self._calculate_hash(full_path)
                        size_bytes = os.path.getsize(full_path)
                        wallets = self._extract_wallets(full_path, file_type)
                        
                        # Move to categorized folder
                        dest_dir = os.path.join(self.config.extracted_dir, category)
                        dest_path = os.path.join(dest_dir, f"{file_hash[:16]}_{file}")
                        
                        # Handle duplicates
                        counter = 1
                        while os.path.exists(dest_path):
                            dest_path = os.path.join(dest_dir, f"{file_hash[:16]}_{counter}_{file}")
                            counter += 1
                        
                        os.rename(full_path, dest_path)
                        
                        extracted_file = ExtractedFile(
                            filename=file,
                            original_archive=os.path.basename(zip_path),
                            category=category,
                            file_type=file_type,
                            file_hash=file_hash,
                            size_bytes=size_bytes,
                            wallets_found=wallets,
                            extracted_at=datetime.utcnow().isoformat(),
                            file_path=dest_path
                        )
                        
                        self.extracted_files.append(extracted_file)
                        extracted_files.append(dest_path)
                
                # Cleanup empty extraction folder
                if os.path.exists(extract_to):
                    import shutil
                    shutil.rmtree(extract_to, ignore_errors=True)
                    
        except zipfile.BadZipFile:
            self.errors.append(f"Bad ZIP file: {zip_path}")
        except Exception as e:
            self.errors.append(f"Error extracting {zip_path}: {str(e)}")
        
        return extracted_files
    
    def process_archives(self, archive_paths: List[str] = None) -> ProcessingSummary:
        """
        Process all ZIP archives in the dumps directory
        
        Args:
            archive_paths: Optional list of specific ZIP files to process
        
        Returns:
            ProcessingSummary with results
        """
        import time
        start_time = time.time()
        
        # Find all ZIP files if not specified
        if archive_paths is None:
            dumps_path = Path(self.config.dumps_dir)
            archive_paths = list(dumps_path.glob("*.zip"))
            archive_paths = [str(p) for p in archive_paths]
        
        print(f"📦 Found {len(archive_paths)} ZIP archives to process")
        
        # Process each archive
        for i, zip_path in enumerate(archive_paths, 1):
            print(f"   [{i}/{len(archive_paths)}] Extracting: {os.path.basename(zip_path)}")
            
            extract_to = os.path.join(self.config.extracted_dir, "temp", f"extract_{i}")
            os.makedirs(extract_to, exist_ok=True)
            
            self._extract_archive(zip_path, extract_to)
        
        # Calculate statistics
        categories = {}
        for ef in self.extracted_files:
            categories[ef.category] = categories.get(ef.category, 0) + 1
        
        all_wallets = []
        for ef in self.extracted_files:
            all_wallets.extend(ef.wallets_found)
        all_wallets = list(set(all_wallets))
        
        # Count by chain
        wallets_by_chain = {}
        for wallet in all_wallets:
            if wallet.startswith('0x'):
                wallets_by_chain['evm'] = wallets_by_chain.get('evm', 0) + 1
            elif len(wallet) == 44 or len(wallet) == 43:
                wallets_by_chain['solana'] = wallets_by_chain.get('solana', 0) + 1
            else:
                wallets_by_chain['other'] = wallets_by_chain.get('other', 0) + 1
        
        elapsed = time.time() - start_time
        
        summary = ProcessingSummary(
            total_archives=len(archive_paths),
            total_files_extracted=len(self.extracted_files),
            total_images_processed=0,  # Will be updated by OCR processor
            total_wallets_found=len(all_wallets),
            wallets_by_chain=wallets_by_chain,
            categories=categories,
            errors=self.errors,
            processing_time_seconds=round(elapsed, 2)
        )
        
        return summary
    
    def export_manifest(self, output_path: str = None) -> str:
        """Export extraction manifest to JSON"""
        if output_path is None:
            output_path = os.path.join(self.config.extracted_dir, "extraction_manifest.json")
        
        manifest = {
            "exported_at": datetime.utcnow().isoformat(),
            "total_files": len(self.extracted_files),
            "files": [asdict(f) for f in self.extracted_files]
        }
        
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return output_path


# ═══════════════════════════════════════════════════════════
# OCR PROCESSOR
# ═══════════════════════════════════════════════════════════

class OCRProcessor:
    """
    OCR processing for screenshots and images
    Extracts text and wallet addresses from visual evidence
    """
    
    def __init__(self, config: EvidenceConfig = None):
        self.config = config or EvidenceConfig()
        self.results: List[OCResult] = []
        self.errors: List[str] = []
        
        os.makedirs(self.config.ocr_output_dir, exist_ok=True)
        
        if not TESSERACT_AVAILABLE:
            print("⚠️  OCR will not be available without Tesseract")
    
    def _extract_wallets_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract wallets from OCR text with context"""
        wallets = []
        
        for chain, pattern in self.config.wallet_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                # Get surrounding context (50 chars before/after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].replace('\n', ' ')
                
                wallets.append({
                    'address': match.group(),
                    'chain': chain,
                    'context': context,
                    'position': match.start()
                })
        
        return wallets
    
    def process_image(self, image_path: str) -> Optional[OCResult]:
        """Process a single image with OCR"""
        if not TESSERACT_AVAILABLE:
            return None
        
        try:
            # Open and preprocess image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode not in ['RGB', 'L']:
                image = image.convert('RGB')
            
            # Run OCR
            text = pytesseract.image_to_string(image)
            
            # Get confidence data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data['conf'] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract wallets
            wallets = self._extract_wallets_from_text(text)
            
            result = OCResult(
                image_path=image_path,
                extracted_text=text,
                confidence=round(avg_confidence / 100, 2),  # Normalize to 0-1
                wallets_found=wallets,
                processed_at=datetime.utcnow().isoformat()
            )
            
            return result
            
        except Exception as e:
            self.errors.append(f"OCR failed for {image_path}: {str(e)}")
            return None
    
    def process_images(self, image_paths: List[str] = None) -> List[OCResult]:
        """
        Process multiple images with OCR
        
        Args:
            image_paths: Optional list of specific images to process
        
        Returns:
            List of OCResult objects
        """
        if not TESSERACT_AVAILABLE:
            print("❌ Tesseract not available. Cannot process images.")
            return []
        
        # Find all images if not specified
        if image_paths is None:
            dumps_path = Path(self.config.dumps_dir)
            image_paths = list(dumps_path.glob("*.jpg")) + list(dumps_path.glob("*.jpeg")) + list(dumps_path.glob("*.png"))
            image_paths = [str(p) for p in image_paths]
        
        print(f"🖼️  Found {len(image_paths)} images to process with OCR")
        
        # Process images in parallel
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            results = list(executor.map(self.process_image, image_paths))
        
        # Filter out None results
        self.results = [r for r in results if r is not None]
        
        print(f"✅ Successfully processed {len(self.results)} images")
        print(f"   Found {sum(len(r.wallets_found) for r in self.results)} wallet mentions")
        
        return self.results
    
    def export_results(self, output_path: str = None) -> str:
        """Export OCR results to JSON"""
        if output_path is None:
            output_path = os.path.join(self.config.ocr_output_dir, "ocr_results.json")
        
        data = {
            "processed_at": datetime.utcnow().isoformat(),
            "total_images": len(self.results),
            "total_wallets_found": sum(len(r.wallets_found) for r in self.results),
            "results": [asdict(r) for r in self.results],
            "errors": self.errors
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return output_path


# ═══════════════════════════════════════════════════════════
# UNIFIED PROCESSOR
# ═══════════════════════════════════════════════════════════

class EvidencePipeline:
    """
    Unified evidence processing pipeline
    Combines extraction + OCR + wallet discovery
    """
    
    def __init__(self, config: EvidenceConfig = None):
        self.config = config or EvidenceConfig()
        self.extractor = EvidenceExtractor(self.config)
        self.ocr = OCRProcessor(self.config)
    
    def run_full_pipeline(self, 
                         zip_files: List[str] = None,
                         image_files: List[str] = None) -> Dict[str, Any]:
        """
        Run complete evidence processing pipeline
        
        Returns:
            Complete processing results
        """
        print("\n" + "="*70)
        print("🔍 RMI EVIDENCE PROCESSING PIPELINE")
        print("="*70)
        
        results = {
            "pipeline_start": datetime.utcnow().isoformat(),
            "extraction": None,
            "ocr": None,
            "all_wallets": [],
            "pipeline_end": None
        }
        
        # Step 1: Extract archives
        print("\n📦 STEP 1: Extracting ZIP Archives")
        print("-"*70)
        extraction_summary = self.extractor.process_archives(zip_files)
        results["extraction"] = asdict(extraction_summary)
        
        # Export extraction manifest
        manifest_path = self.extractor.export_manifest()
        print(f"\n   📄 Manifest saved: {manifest_path}")
        
        # Collect wallets from extraction
        for ef in self.extractor.extracted_files:
            results["all_wallets"].extend(ef.wallets_found)
        
        # Step 2: Process images with OCR
        print("\n🖼️  STEP 2: OCR Image Processing")
        print("-"*70)
        ocr_results = self.ocr.process_images(image_files)
        results["ocr"] = {
            "total_images": len(ocr_results),
            "total_wallets": sum(len(r.wallets_found) for r in ocr_results)
        }
        
        # Export OCR results
        ocr_path = self.ocr.export_results()
        print(f"\n   📄 OCR results saved: {ocr_path}")
        
        # Collect wallets from OCR
        for r in ocr_results:
            for w in r.wallets_found:
                results["all_wallets"].append(w['address'])
        
        # Deduplicate wallets
        results["all_wallets"] = list(set(results["all_wallets"]))
        results["pipeline_end"] = datetime.utcnow().isoformat()
        
        # Print summary
        print("\n" + "="*70)
        print("📊 PIPELINE SUMMARY")
        print("="*70)
        print(f"   Archives processed: {extraction_summary.total_archives}")
        print(f"   Files extracted: {extraction_summary.total_files_extracted}")
        print(f"   Images OCR'd: {len(ocr_results)}")
        print(f"   Unique wallets found: {len(results['all_wallets'])}")
        print(f"   Processing time: {extraction_summary.processing_time_seconds}s")
        
        if extraction_summary.errors:
            print(f"\n⚠️  Errors: {len(extraction_summary.errors)}")
        
        # Save final results
        final_path = os.path.join(self.config.extracted_dir, "pipeline_results.json")
        with open(final_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Final results: {final_path}")
        
        return results
    
    def get_wallets_for_tracing(self, min_mentions: int = 1) -> List[Dict[str, Any]]:
        """
        Get consolidated list of wallets with mention counts
        Ready for wallet tracing pipeline
        """
        wallet_data = {}
        
        # Count from extracted files
        for ef in self.extractor.extracted_files:
            for wallet in ef.wallets_found:
                if wallet not in wallet_data:
                    wallet_data[wallet] = {
                        'address': wallet,
                        'mentions': 0,
                        'sources': [],
                        'chains': []
                    }
                wallet_data[wallet]['mentions'] += 1
                wallet_data[wallet]['sources'].append(ef.original_archive)
        
        # Count from OCR results
        for ocresult in self.ocr.results:
            for w in ocresult.wallets_found:
                addr = w['address']
                if addr not in wallet_data:
                    wallet_data[addr] = {
                        'address': addr,
                        'mentions': 0,
                        'sources': [],
                        'chains': [w['chain']]
                    }
                wallet_data[addr]['mentions'] += 1
                if w['chain'] not in wallet_data[addr]['chains']:
                    wallet_data[addr]['chains'].append(w['chain'])
        
        # Filter by minimum mentions and sort
        filtered = [w for w in wallet_data.values() if w['mentions'] >= min_mentions]
        sorted_wallets = sorted(filtered, key=lambda x: x['mentions'], reverse=True)
        
        return sorted_wallets


# ═══════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="RMI Evidence Processing Pipeline")
    parser.add_argument("--extract", action="store_true", help="Extract ZIP archives")
    parser.add_argument("--ocr", action="store_true", help="Process images with OCR")
    parser.add_argument("--full", action="store_true", help="Run full pipeline")
    parser.add_argument("--wallets", action="store_true", help="Export wallet list for tracing")
    parser.add_argument("--dumps-dir", default="/root/dumps/investigation-20260409/mixed", 
                       help="Directory containing evidence files")
    
    args = parser.parse_args()
    
    config = EvidenceConfig(dumps_dir=args.dumps_dir)
    pipeline = EvidencePipeline(config)
    
    if args.full or (not args.extract and not args.ocr and not args.wallets):
        # Run full pipeline
        results = pipeline.run_full_pipeline()
        
        # Export top wallets
        top_wallets = pipeline.get_wallets_for_tracing(min_mentions=1)
        wallet_path = os.path.join(config.extracted_dir, "wallets_for_tracing.json")
        with open(wallet_path, 'w') as f:
            json.dump(top_wallets, f, indent=2)
        print(f"\n💼 Top {len(top_wallets)} wallets exported: {wallet_path}")
        
    elif args.extract:
        summary = pipeline.extractor.process_archives()
        print(f"\n✅ Extracted {summary.total_files_extracted} files from {summary.total_archives} archives")
        
    elif args.ocr:
        results = pipeline.ocr.process_images()
        print(f"\n✅ Processed {len(results)} images")
        
    elif args.wallets:
        # Load existing results and export wallets
        results_path = os.path.join(config.extracted_dir, "pipeline_results.json")
        if os.path.exists(results_path):
            with open(results_path) as f:
                _ = json.load(f)  # Ensure extraction loaded
            
            top_wallets = pipeline.get_wallets_for_tracing(min_mentions=1)
            wallet_path = os.path.join(config.extracted_dir, "wallets_for_tracing.json")
            with open(wallet_path, 'w') as f:
                json.dump(top_wallets, f, indent=2)
            print(f"\n💼 Exported {len(top_wallets)} wallets: {wallet_path}")
        else:
            print("❌ No pipeline results found. Run --full first.")
