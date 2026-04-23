#!/usr/bin/env python3
"""
CRM Investigation - OCR Evidence Processor
=========================================

Processes screenshots and images to extract searchable text evidence.
Uses Tesseract OCR with image preprocessing for optimal results.

Output: SQLite database with extracted text, searchable by keyword.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import re

# Try to import pytesseract, but provide fallback
try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Warning: Tesseract/PIL not available. Install with: pip install pytesseract pillow opencv-python")


class OCREvidenceProcessor:
    """
    Extracts text from screenshot evidence for searchable analysis.
    """
    
    def __init__(self, 
                 evidence_dir: str = "/root/crm_investigation/evidence/photos_screenshots",
                 db_path: str = "/root/crm_investigation/evidence/ocr_evidence.db"):
        self.evidence_dir = Path(evidence_dir)
        self.db_path = db_path
        self.init_database()
        self.wallet_pattern = re.compile(r'[A-Za-z0-9]{32,44}')  # Solana wallet pattern
        self.date_pattern = re.compile(r'\d{2}[/-]\d{2}[/-]\d{4}')
        self.time_pattern = re.compile(r'\d{2}:\d{2}:\d{2}')
        
    def init_database(self):
        """Initialize SQLite database for OCR results"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS ocr_extractions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE,
                filepath TEXT,
                extracted_text TEXT,
                wallets_found TEXT,  -- JSON array
                dates_found TEXT,    -- JSON array
                times_found TEXT,    -- JSON array
                keywords_found TEXT, -- JSON object
                extraction_confidence REAL,
                processed_at TEXT,
                status TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS ocr_keywords (
                keyword TEXT,
                filename TEXT,
                context TEXT,
                PRIMARY KEY (keyword, filename)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def preprocess_image(self, image_path: Path) -> Optional['np.ndarray']:
        """Preprocess image for better OCR results"""
        if not TESSERACT_AVAILABLE:
            return None
            
        try:
            # Read image
            img = cv2.imread(str(image_path))
            if img is None:
                return None
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Threshold
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return thresh
        except Exception as e:
            print(f"Error preprocessing {image_path}: {e}")
            return None
    
    def extract_text(self, image_path: Path) -> Dict:
        """Extract text from image using OCR"""
        result = {
            "filename": image_path.name,
            "filepath": str(image_path),
            "extracted_text": "",
            "wallets": [],
            "dates": [],
            "times": [],
            "keywords": {},
            "confidence": 0.0,
            "status": "pending"
        }
        
        if not TESSERACT_AVAILABLE:
            result["status"] = "tesseract_not_available"
            return result
        
        try:
            # Try direct OCR first
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            
            # If low confidence, try preprocessing
            if len(text.strip()) < 50:
                processed = self.preprocess_image(image_path)
                if processed is not None:
                    text = pytesseract.image_to_string(processed)
            
            result["extracted_text"] = text
            result["confidence"] = min(len(text) / 1000, 1.0)  # Simple confidence metric
            
            # Extract entities
            result["wallets"] = self.wallet_pattern.findall(text)
            result["dates"] = self.date_pattern.findall(text)
            result["times"] = self.time_pattern.findall(text)
            
            # Look for keywords
            keywords = self._extract_keywords(text)
            result["keywords"] = keywords
            
            result["status"] = "success"
            
        except Exception as e:
            result["status"] = f"error: {str(e)}"
        
        return result
    
    def _extract_keywords(self, text: str) -> Dict:
        """Extract investigation-relevant keywords"""
        text_lower = text.lower()
        keywords = {}
        
        keyword_categories = {
            "tokens": ["crm", "shift", "sosana", "shift ai", "pbtc", "epik"],
            "actions": ["buy", "sell", "transfer", "transaction", "dump", "pump"],
            "roles": ["winner", "contest", "vote", "community", "team"],
            "suspicious": ["admin", "insider", "fake", "scam", "rug"],
            "wallets": ["wallet", "address", "holder", "balance"],
            "urgency": ["now", "quick", "hurry", "soon", "asap"]
        }
        
        for category, words in keyword_categories.items():
            found = [w for w in words if w in text_lower]
            if found:
                keywords[category] = found
        
        return keywords
    
    def process_all_images(self) -> Dict:
        """Process all screenshot images"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        images = [f for f in self.evidence_dir.iterdir() 
                if f.suffix.lower() in image_extensions]
        
        results = {
            "total_images": len(images),
            "processed": 0,
            "failed": 0,
            "wallets_found": 0,
            "database_path": self.db_path
        }
        
        print(f"Processing {len(images)} images from {self.evidence_dir}")
        
        for i, image_path in enumerate(images, 1):
            print(f"  [{i}/{len(images)}] Processing {image_path.name}...", end=" ")
            
            extraction = self.extract_text(image_path)
            
            if extraction["status"] == "success":
                results["processed"] += 1
                results["wallets_found"] += len(extraction["wallets"])
                print(f"✓ (found {len(extraction['wallets'])} wallets)")
            else:
                results["failed"] += 1
                print(f"✗ ({extraction['status']})")
            
            # Save to database
            self._save_extraction(extraction)
        
        return results
    
    def _save_extraction(self, extraction: Dict):
        """Save extraction results to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT OR REPLACE INTO ocr_extractions
            (filename, filepath, extracted_text, wallets_found, dates_found, 
             times_found, keywords_found, extraction_confidence, processed_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            extraction["filename"],
            extraction["filepath"],
            extraction["extracted_text"],
            json.dumps(extraction["wallets"]),
            json.dumps(extraction["dates"]),
            json.dumps(extraction["times"]),
            json.dumps(extraction["keywords"]),
            extraction["confidence"],
            datetime.now().isoformat(),
            extraction["status"]
        ))
        
        # Save keyword contexts
        for category, keywords in extraction["keywords"].items():
            for keyword in keywords:
                # Find context around keyword
                text = extraction["extracted_text"].lower()
                idx = text.find(keyword)
                if idx >= 0:
                    start = max(0, idx - 50)
                    end = min(len(text), idx + 50)
                    context = extraction["extracted_text"][start:end]
                    
                    c.execute('''
                        INSERT OR REPLACE INTO ocr_keywords
                        (keyword, filename, context)
                        VALUES (?, ?, ?)
                    ''', (keyword, extraction["filename"], context))
        
        conn.commit()
        conn.close()
    
    def search_keyword(self, keyword: str) -> List[Dict]:
        """Search for keyword in extracted text"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT filename, filepath, extracted_text, wallets_found, status
            FROM ocr_extractions
            WHERE extracted_text LIKE ?
        ''', (f'%{keyword}%',))
        
        results = []
        for row in c.fetchall():
            results.append({
                "filename": row[0],
                "filepath": row[1],
                "text_preview": row[2][:200] if row[2] else "",
                "wallets": json.loads(row[3]) if row[3] else [],
                "status": row[4]
            })
        
        conn.close()
        return results
    
    def get_statistics(self) -> Dict:
        """Get OCR processing statistics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT COUNT(*) FROM ocr_extractions WHERE status = "success"')
        success_count = c.fetchone()[0]
        
        c.execute('SELECT COUNT(*) FROM ocr_extractions')
        total_count = c.fetchone()[0]
        
        c.execute('SELECT COUNT(DISTINCT keyword) FROM ocr_keywords')
        unique_keywords = c.fetchone()[0]
        
        conn.close()
        
        return {
            "total_images": total_count,
            "successfully_processed": success_count,
            "unique_keywords_found": unique_keywords,
            "success_rate": f"{success_count/max(total_count,1)*100:.1f}%"
        }
    
    def generate_report(self) -> str:
        """Generate OCR processing report"""
        stats = self.get_statistics()
        
        report = f"""
OCR EVIDENCE PROCESSING REPORT
==============================
Generated: {datetime.now().isoformat()}
Database: {self.db_path}
Evidence Directory: {self.evidence_dir}

SUMMARY
-------
Total Images: {stats['total_images']}
Successfully Processed: {stats['successfully_processed']}
Success Rate: {stats['success_rate']}
Unique Keywords Found: {stats['unique_keywords_found']}

STATUS
------
Tesseract Available: {TESSERACT_AVAILABLE}
"""
        
        if not TESSERACT_AVAILABLE:
            report += """
NOTE: Tesseract OCR not available. To enable full OCR processing:
  1. Install Tesseract: sudo apt-get install tesseract-ocr
  2. Install Python packages: pip install pytesseract pillow opencv-python
  3. Re-run this processor

FALLBACK: Manual transcription of key images recommended for critical evidence.
"""
        
        return report


# ==================== CLI ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="CRM Investigation OCR Processor")
    parser.add_argument("--process", action="store_true", help="Process all images")
    parser.add_argument("--search", type=str, help="Search for keyword")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--report", action="store_true", help="Generate report")
    
    args = parser.parse_args()
    
    processor = OCREvidenceProcessor()
    
    if args.report or not any([args.process, args.search, args.stats]):
        print(processor.generate_report())
    
    if args.stats:
        stats = processor.get_statistics()
        print(json.dumps(stats, indent=2))
    
    if args.process:
        results = processor.process_all_images()
        print("\nProcessing Complete:")
        print(json.dumps(results, indent=2))
    
    if args.search:
        results = processor.search_keyword(args.search)
        print(f"\nSearch results for '{args.search}':")
        print(f"Found in {len(results)} images:")
        for r in results[:10]:  # Limit to 10
            print(f"  - {r['filename']}: {r['text_preview'][:80]}...")
