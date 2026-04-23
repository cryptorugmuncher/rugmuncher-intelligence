"""
Omega Forensic V5 - Data Processor
===================================
Universal document ingestion and processing.
Handles TXT, JSON, ZIP files with automatic classification.
"""

import os
import json
import zipfile
import shutil
from typing import Dict, List, Optional, Any, BinaryIO
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataProcessor")

@dataclass
class ProcessedDocument:
    """Result of processing a document."""
    source_path: str
    document_type: str  # telegram, transaction, chat, unknown
    content: Any
    metadata: Dict = field(default_factory=dict)
    extracted_entities: List[Dict] = field(default_factory=list)
    processing_timestamp: datetime = None
    
    def __post_init__(self):
        if self.processing_timestamp is None:
            self.processing_timestamp = datetime.now()

class UniversalDocumentProcessor:
    """
    Universal document processor for forensic evidence.
    Handles multiple formats with automatic classification.
    """
    
    SUPPORTED_FORMATS = ['.txt', '.json', '.zip', '.html', '.csv']
    
    def __init__(self, output_dir: str = "./processed_evidence"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.processed_count = 0
        self.classification_stats = {
            "telegram": 0,
            "transaction": 0,
            "chat": 0,
            "unknown": 0
        }
    
    def process_file(self, file_path: str) -> ProcessedDocument:
        """
        Process a single file.
        
        Args:
            file_path: Path to the file
        
        Returns:
            ProcessedDocument with extracted content
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = path.suffix.lower()
        
        if extension not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {extension}")
        
        logger.info(f"📄 Processing: {file_path}")
        
        # Route to appropriate processor
        if extension == '.txt':
            return self._process_txt(file_path)
        elif extension == '.json':
            return self._process_json(file_path)
        elif extension == '.zip':
            return self._process_zip(file_path)
        elif extension == '.html':
            return self._process_html(file_path)
        elif extension == '.csv':
            return self._process_csv(file_path)
        else:
            return self._process_unknown(file_path)
    
    def _process_txt(self, file_path: str) -> ProcessedDocument:
        """Process text file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Classify content
        doc_type = self._classify_text_content(content)
        
        # Extract entities
        entities = self._extract_entities_from_text(content)
        
        self.processed_count += 1
        self.classification_stats[doc_type] += 1
        
        return ProcessedDocument(
            source_path=file_path,
            document_type=doc_type,
            content=content,
            metadata={
                "file_size": len(content),
                "line_count": content.count('\n') + 1
            },
            extracted_entities=entities
        )
    
    def _process_json(self, file_path: str) -> ProcessedDocument:
        """Process JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Classify JSON structure
        doc_type = self._classify_json_content(content)
        
        # Extract entities
        entities = self._extract_entities_from_json(content)
        
        self.processed_count += 1
        self.classification_stats[doc_type] += 1
        
        return ProcessedDocument(
            source_path=file_path,
            document_type=doc_type,
            content=content,
            metadata={
                "structure": type(content).__name__,
                "keys": list(content.keys()) if isinstance(content, dict) else []
            },
            extracted_entities=entities
        )
    
    def _process_zip(self, file_path: str) -> ProcessedDocument:
        """Process ZIP archive - extract and process contents."""
        extracted_files = []
        all_entities = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                
                # Process each file in archive
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        try:
                            processed = self.process_file(full_path)
                            extracted_files.append(processed)
                            all_entities.extend(processed.extracted_entities)
                        except Exception as e:
                            logger.warning(f"  Could not process {file}: {e}")
        
        self.processed_count += 1
        self.classification_stats["unknown"] += 1
        
        return ProcessedDocument(
            source_path=file_path,
            document_type="archive",
            content={
                "extracted_files": len(extracted_files),
                "files": [f.source_path for f in extracted_files]
            },
            metadata={
                "archive_type": "zip",
                "extracted_count": len(extracted_files)
            },
            extracted_entities=all_entities
        )
    
    def _process_html(self, file_path: str) -> ProcessedDocument:
        """Process HTML file (typically Telegram exports)."""
        from html.parser import HTMLParser
        
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self.in_script = False
            
            def handle_starttag(self, tag, attrs):
                if tag in ['script', 'style']:
                    self.in_script = True
            
            def handle_endtag(self, tag):
                if tag in ['script', 'style']:
                    self.in_script = False
            
            def handle_data(self, data):
                if not self.in_script:
                    self.text.append(data)
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        # Extract text
        extractor = TextExtractor()
        extractor.feed(html_content)
        text_content = ' '.join(extractor.text)
        
        # Classify as Telegram if it matches patterns
        doc_type = "telegram" if "Telegram" in html_content or "message" in html_content.lower() else "unknown"
        
        # Extract entities
        entities = self._extract_entities_from_text(text_content)
        
        self.processed_count += 1
        self.classification_stats[doc_type] += 1
        
        return ProcessedDocument(
            source_path=file_path,
            document_type=doc_type,
            content=text_content,
            metadata={
                "html_size": len(html_content),
                "text_size": len(text_content)
            },
            extracted_entities=entities
        )
    
    def _process_csv(self, file_path: str) -> ProcessedDocument:
        """Process CSV file (typically transaction data)."""
        import csv
        
        rows = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        
        # Extract wallet addresses from CSV
        entities = []
        for row in rows:
            for key, value in row.items():
                if isinstance(value, str) and len(value) == 44 and value[0].isalnum():
                    # Potential Solana address
                    entities.append({
                        "type": "wallet_address",
                        "value": value,
                        "source": "csv_transaction"
                    })
        
        self.processed_count += 1
        self.classification_stats["transaction"] += 1
        
        return ProcessedDocument(
            source_path=file_path,
            document_type="transaction",
            content=rows,
            metadata={
                "row_count": len(rows),
                "columns": list(rows[0].keys()) if rows else []
            },
            extracted_entities=entities
        )
    
    def _process_unknown(self, file_path: str) -> ProcessedDocument:
        """Process unknown file type."""
        self.processed_count += 1
        self.classification_stats["unknown"] += 1
        
        return ProcessedDocument(
            source_path=file_path,
            document_type="unknown",
            content=None,
            metadata={"error": "Unsupported file type"}
        )
    
    def _classify_text_content(self, content: str) -> str:
        """Classify text content type."""
        content_lower = content.lower()
        
        # Check for Telegram patterns
        if any(x in content for x in ['telegram', '@', 'message', 'chat']):
            return "telegram"
        
        # Check for transaction patterns
        if any(x in content_lower for x in ['transaction', 'signature', 'wallet', 'solana']):
            return "transaction"
        
        # Check for chat patterns
        if any(x in content_lower for x in ['said:', 'user:', 'chat log']):
            return "chat"
        
        return "unknown"
    
    def _classify_json_content(self, content: Any) -> str:
        """Classify JSON content type."""
        if isinstance(content, dict):
            keys = [k.lower() for k in content.keys()]
            
            if any(k in keys for k in ['transactions', 'signatures', 'wallets']):
                return "transaction"
            
            if any(k in keys for k in ['messages', 'chats', 'users']):
                return "telegram"
        
        if isinstance(content, list) and len(content) > 0:
            first = content[0]
            if isinstance(first, dict):
                keys = [k.lower() for k in first.keys()]
                
                if any(k in keys for k in ['signature', 'from', 'to']):
                    return "transaction"
        
        return "unknown"
    
    def _extract_entities_from_text(self, text: str) -> List[Dict]:
        """Extract entities (wallets, tokens, etc.) from text."""
        entities = []
        
        # Extract Solana addresses (44 chars, base58)
        import re
        wallet_pattern = r'[A-HJ-NP-Za-km-z1-9]{32,44}'
        wallets = set(re.findall(wallet_pattern, text))
        
        for wallet in wallets:
            if len(wallet) == 44:  # Full Solana address
                entities.append({
                    "type": "wallet_address",
                    "value": wallet,
                    "source": "text_extraction"
                })
        
        # Extract token symbols
        token_pattern = r'\$([A-Z]{2,10})'
        tokens = set(re.findall(token_pattern, text))
        
        for token in tokens:
            entities.append({
                "type": "token_symbol",
                "value": token,
                "source": "text_extraction"
            })
        
        return entities
    
    def _extract_entities_from_json(self, content: Any) -> List[Dict]:
        """Recursively extract entities from JSON."""
        entities = []
        
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, str):
                    # Check for wallet address
                    if len(value) == 44 and value[0].isalnum():
                        entities.append({
                            "type": "wallet_address",
                            "value": value,
                            "source": f"json_field:{key}"
                        })
                elif isinstance(value, (dict, list)):
                    entities.extend(self._extract_entities_from_json(value))
        
        elif isinstance(content, list):
            for item in content:
                entities.extend(self._extract_entities_from_json(item))
        
        return entities
    
    def batch_process(self, directory: str, pattern: str = "*") -> List[ProcessedDocument]:
        """
        Process all matching files in a directory.
        
        Args:
            directory: Directory to scan
            pattern: File pattern to match
        
        Returns:
            List of processed documents
        """
        logger.info(f"📁 Batch processing: {directory}/{pattern}")
        
        dir_path = Path(directory)
        files = list(dir_path.glob(pattern))
        
        processed = []
        for file_path in files:
            if file_path.is_file():
                try:
                    doc = self.process_file(str(file_path))
                    processed.append(doc)
                except Exception as e:
                    logger.error(f"  ✗ Error processing {file_path}: {e}")
        
        logger.info(f"  ✓ Processed {len(processed)} files")
        return processed
    
    def get_statistics(self) -> Dict:
        """Get processing statistics."""
        return {
            "total_processed": self.processed_count,
            "by_type": self.classification_stats,
            "supported_formats": self.SUPPORTED_FORMATS
        }

# === SYNC WRAPPER ===
def process_document(file_path: str) -> ProcessedDocument:
    """Quick function to process a document."""
    processor = UniversalDocumentProcessor()
    return processor.process_file(file_path)

def batch_process_directory(directory: str, pattern: str = "*") -> List[ProcessedDocument]:
    """Quick function to batch process a directory."""
    processor = UniversalDocumentProcessor()
    return processor.batch_process(directory, pattern)

if __name__ == "__main__":
    # Test the processor
    print("=" * 70)
    print("OMEGA FORENSIC V5 - DATA PROCESSOR")
    print("=" * 70)
    
    processor = UniversalDocumentProcessor()
    
    # Test with sample data
    print("\n📊 Supported Formats:")
    for fmt in processor.SUPPORTED_FORMATS:
        print(f"  • {fmt}")
    
    print("\n📁 Statistics:")
    stats = processor.get_statistics()
    print(f"  Total Processed: {stats['total_processed']}")
    print(f"  By Type: {stats['by_type']}")
    
    print("\n" + "=" * 70)
