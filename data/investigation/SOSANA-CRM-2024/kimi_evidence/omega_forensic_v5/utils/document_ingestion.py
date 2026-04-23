"""
Omega Forensic V5 - Document Ingestion
========================================
Universal document ingestion for forensic evidence.
Handles TXT, JSON, ZIP files with automatic organization.
"""

import os
import json
import zipfile
import shutil
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DocumentIngestion")

class DocumentIngestionManager:
    """
    Universal document ingestion manager.
    Drop files and they get automatically organized.
    """
    
    def __init__(self, base_dir: str = "./evidence"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.dirs = {
            "telegram": self.base_dir / "telegram",
            "transactions": self.base_dir / "transactions",
            "chats": self.base_dir / "chats",
            "json": self.base_dir / "json",
            "raw": self.base_dir / "raw",
            "processed": self.base_dir / "processed",
        }
        
        for dir_path in self.dirs.values():
            dir_path.mkdir(exist_ok=True)
        
        self.ingestion_log = []
        
        logger.info(f"📁 Document ingestion manager initialized at {base_dir}")
    
    def ingest_file(self, file_path: str, auto_organize: bool = True) -> Dict[str, Any]:
        """
        Ingest a single file.
        
        Args:
            file_path: Path to file
            auto_organize: Whether to auto-organize by type
        
        Returns:
            Ingestion result
        """
        path = Path(file_path)
        
        if not path.exists():
            return {"success": False, "error": "File not found"}
        
        logger.info(f"📥 Ingesting: {path.name}")
        
        # Detect file type
        file_type = self._detect_file_type(path)
        
        if auto_organize:
            # Copy to appropriate directory
            dest_dir = self.dirs.get(file_type, self.dirs["raw"])
            dest_path = dest_dir / path.name
            
            # Handle duplicates
            counter = 1
            while dest_path.exists():
                stem = path.stem
                suffix = path.suffix
                dest_path = dest_dir / f"{stem}_{counter:03d}{suffix}"
                counter += 1
            
            shutil.copy2(path, dest_path)
            
            result = {
                "success": True,
                "original_path": str(path),
                "stored_path": str(dest_path),
                "file_type": file_type,
                "size_bytes": path.stat().st_size
            }
        else:
            # Just store in raw
            dest_path = self.dirs["raw"] / path.name
            shutil.copy2(path, dest_path)
            
            result = {
                "success": True,
                "original_path": str(path),
                "stored_path": str(dest_path),
                "file_type": "raw",
                "size_bytes": path.stat().st_size
            }
        
        # Log ingestion
        self.ingestion_log.append({
            "timestamp": datetime.now().isoformat(),
            "file": path.name,
            "type": file_type,
            "result": result["success"]
        })
        
        logger.info(f"  ✓ Stored in {file_type}/")
        
        return result
    
    def ingest_directory(
        self, 
        directory: str, 
        pattern: str = "*",
        recursive: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Ingest all files in a directory.
        
        Args:
            directory: Directory to scan
            pattern: File pattern to match
            recursive: Whether to scan recursively
        
        Returns:
            List of ingestion results
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            logger.error(f"Directory not found: {directory}")
            return []
        
        logger.info(f"📁 Ingesting directory: {directory}")
        
        results = []
        
        if recursive:
            files = list(dir_path.rglob(pattern))
        else:
            files = list(dir_path.glob(pattern))
        
        for file_path in files:
            if file_path.is_file():
                try:
                    result = self.ingest_file(str(file_path))
                    results.append(result)
                except Exception as e:
                    logger.error(f"  ✗ Error ingesting {file_path}: {e}")
                    results.append({
                        "success": False,
                        "file": str(file_path),
                        "error": str(e)
                    })
        
        logger.info(f"  ✓ Ingested {len([r for r in results if r.get('success')])} files")
        
        return results
    
    def ingest_zip(self, zip_path: str, extract: bool = True) -> Dict[str, Any]:
        """
        Ingest a ZIP archive.
        
        Args:
            zip_path: Path to ZIP file
            extract: Whether to extract contents
        
        Returns:
            Ingestion result
        """
        path = Path(zip_path)
        
        if not path.exists():
            return {"success": False, "error": "ZIP not found"}
        
        logger.info(f"📦 Ingesting ZIP: {path.name}")
        
        # Store ZIP
        dest_path = self.dirs["raw"] / path.name
        shutil.copy2(path, dest_path)
        
        extracted_files = []
        
        if extract:
            # Extract to temp directory
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Ingest extracted files
                extracted_results = self.ingest_directory(temp_dir)
                extracted_files = [r for r in extracted_results if r.get('success')]
        
        result = {
            "success": True,
            "zip_path": str(dest_path),
            "extracted_files": len(extracted_files)
        }
        
        logger.info(f"  ✓ ZIP ingested, {len(extracted_files)} files extracted")
        
        return result
    
    def _detect_file_type(self, path: Path) -> str:
        """Detect the type of file."""
        extension = path.suffix.lower()
        name = path.name.lower()
        
        # Check content for HTML
        if extension == '.html':
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1000)
                    if 'telegram' in content.lower() or 'message' in content.lower():
                        return "telegram"
            except:
                pass
            return "raw"
        
        # JSON files
        if extension == '.json':
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Check structure
                    if isinstance(data, dict):
                        keys = [k.lower() for k in data.keys()]
                        if any(k in keys for k in ['transactions', 'signatures']):
                            return "transactions"
                        if any(k in keys for k in ['messages', 'chats']):
                            return "telegram"
            except:
                pass
            return "json"
        
        # CSV files
        if extension == '.csv':
            return "transactions"
        
        # TXT files
        if extension == '.txt':
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1000).lower()
                    if any(x in content for x in ['wallet', 'transaction', 'signature']):
                        return "transactions"
                    if any(x in content for x in ['chat', 'message', 'said:']):
                        return "chats"
            except:
                pass
            return "raw"
        
        return "raw"
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        stats = {
            "total_ingested": len(self.ingestion_log),
            "by_directory": {},
            "recent_ingestions": self.ingestion_log[-10:]
        }
        
        for dir_name, dir_path in self.dirs.items():
            if dir_path.exists():
                file_count = len(list(dir_path.iterdir()))
                total_size = sum(f.stat().st_size for f in dir_path.iterdir() if f.is_file())
                stats["by_directory"][dir_name] = {
                    "files": file_count,
                    "size_bytes": total_size
                }
        
        return stats
    
    def export_manifest(self) -> str:
        """Export ingestion manifest as JSON."""
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "base_directory": str(self.base_dir),
            "ingestion_log": self.ingestion_log,
            "statistics": self.get_statistics()
        }
        
        manifest_path = self.base_dir / "ingestion_manifest.json"
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return str(manifest_path)

# === QUICK ACCESS FUNCTIONS ===
def ingest_file(file_path: str, base_dir: str = "./evidence") -> Dict:
    """Quick function to ingest a file."""
    manager = DocumentIngestionManager(base_dir)
    return manager.ingest_file(file_path)

def ingest_directory(directory: str, base_dir: str = "./evidence") -> List[Dict]:
    """Quick function to ingest a directory."""
    manager = DocumentIngestionManager(base_dir)
    return manager.ingest_directory(directory)

if __name__ == "__main__":
    # Test document ingestion
    print("=" * 70)
    print("OMEGA FORENSIC V5 - DOCUMENT INGESTION")
    print("=" * 70)
    
    manager = DocumentIngestionManager()
    
    print("\n📁 Directory Structure:")
    for name, path in manager.dirs.items():
        print(f"  {name}/")
    
    print("\n📊 Statistics:")
    stats = manager.get_statistics()
    print(f"  Total Ingested: {stats['total_ingested']}")
    
    print("\n" + "=" * 70)
