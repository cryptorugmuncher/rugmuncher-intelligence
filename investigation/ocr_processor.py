#!/usr/bin/env python3
"""
Part 2: OCR Processing - Extract text from visual evidence
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from supabase import create_client
from pathlib import Path
import pytesseract
from PIL import Image
import json
import re
from datetime import datetime

SUPABASE_URL = "https://ufblzfxqwgaekrewncbi.supabase.co"
SERVICE_KEY = "sb_secret_Uye75Qavhe0ZXJCo4Uadiw_CCYWULKa"

supabase = create_client(SUPABASE_URL, SERVICE_KEY)

EVIDENCE_PATH = Path("/root/dumps/investigation-20260409/mixed")
CASE_ID = "SOSANA-CRM-2024"

class VisualOCRProcessor:
    """Process visual evidence with OCR"""
    
    def __init__(self):
        self.processed_count = 0
        self.failed_count = 0
        self.extracted_texts = []
        self.new_entities = {
            'wallets': set(),
            'telegram': set(),
            'urls': set(),
        }
        
    def find_visual_files(self):
        """Find all image files in evidence"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff'}
        
        visual_files = []
        for ext in image_extensions:
            for f in EVIDENCE_PATH.rglob(f"*{ext}"):
                # Skip thumbnails and extension icons
                if '_thumb' not in f.name and 'icon' not in f.name.lower():
                    visual_files.append(f)
            for f in EVIDENCE_PATH.rglob(f"*{ext.upper()}"):
                if '_thumb' not in f.name and 'icon' not in f.name.lower():
                    visual_files.append(f)
        
        return visual_files
    
    def process_image(self, image_path):
        """Process single image with OCR"""
        try:
            # Open image
            img = Image.open(image_path)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Perform OCR
            text = pytesseract.image_to_string(img)
            
            return {
                'success': True,
                'text': text,
                'path': str(image_path),
                'size': img.size
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'path': str(image_path)
            }
    
    def extract_entities_from_text(self, text):
        """Extract entities from OCR text"""
        entities = {
            'wallets': set(),
            'telegram': set(),
            'urls': set(),
        }
        
        # Ethereum wallets
        eth_pattern = r'0x[a-fA-F0-9]{40}'
        for match in re.finditer(eth_pattern, text):
            entities['wallets'].add(match.group().lower())
        
        # Telegram handles
        tg_pattern = r'@([a-zA-Z0-9_]{5,32})'
        for match in re.finditer(tg_pattern, text):
            entities['telegram'].add(match.group(1))
        
        # URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        for match in re.finditer(url_pattern, text):
            entities['urls'].add(match.group()[:500])
        
        return entities
    
    def process_all_visuals(self):
        """Process all visual evidence"""
        print("=" * 70)
        print("📸 PART 2: OCR PROCESSING - Visual Evidence")
        print("=" * 70)
        
        # Find all visual files
        visual_files = self.find_visual_files()
        print(f"\n📂 Found {len(visual_files)} visual files")
        
        if not visual_files:
            print("⚠️ No visual files found")
            return
        
        # Process each image
        results = []
        for i, img_path in enumerate(visual_files):
            if i % 10 == 0:
                print(f"  Processing {i}/{len(visual_files)}...")
            
            result = self.process_image(img_path)
            
            if result['success']:
                self.processed_count += 1
                
                # Extract entities from OCR text
                if result['text'].strip():
                    entities = self.extract_entities_from_text(result['text'])
                    
                    # Aggregate entities
                    self.new_entities['wallets'].update(entities['wallets'])
                    self.new_entities['telegram'].update(entities['telegram'])
                    self.new_entities['urls'].update(entities['urls'])
                    
                    # Store result
                    results.append({
                        'file': str(img_path.name),
                        'full_path': str(img_path),
                        'text': result['text'][:2000],  # Limit text length
                        'wallets_found': len(entities['wallets']),
                        'telegram_found': len(entities['telegram']),
                        'urls_found': len(entities['urls'])
                    })
            else:
                self.failed_count += 1
                print(f"  ⚠️ Failed: {img_path.name} - {result.get('error', 'Unknown')}")
        
        print(f"\n✅ Processed: {self.processed_count}")
        print(f"❌ Failed: {self.failed_count}")
        
        return results
    
    def save_results(self, results):
        """Save OCR results to database"""
        print("\n💾 Saving OCR results to database...")
        
        # Update evidence records with OCR text
        updated = 0
        for result in results:
            try:
                # Find the evidence record by file path
                file_name = Path(result['file']).name
                
                supabase.table("investigation_evidence").update({
                    'metadata': {
                        'ocr_text': result['text'],
                        'ocr_extracted_wallets': result['wallets_found'],
                        'ocr_extracted_telegram': result['telegram_found'],
                        'ocr_extracted_urls': result['urls_found'],
                        'ocr_processed_at': str(datetime.now())
                    }
                }).eq('file_name', file_name).eq('case_id', CASE_ID).execute()
                
                updated += 1
            except Exception as e:
                pass  # Silent fail for individual updates
        
        print(f"  ✓ Updated {updated} evidence records with OCR data")
        
        # Save new entities to database
        new_wallet_records = []
        for wallet in self.new_entities['wallets']:
            new_wallet_records.append({
                'case_id': CASE_ID,
                'address': wallet,
                'chain': 'ethereum',
                'source': 'ocr_visual_evidence',
                'metadata': {'source': 'ocr_processing'}
            })
        
        if new_wallet_records:
            try:
                supabase.table("investigation_wallets").upsert(
                    new_wallet_records,
                    on_conflict="case_id,address"
                ).execute()
                print(f"  ✓ Added {len(new_wallet_records)} new wallets from OCR")
            except Exception as e:
                print(f"  ⚠️ Error saving wallets: {e}")
        
        # Save new Telegram handles as entities
        new_tg_records = []
        for handle in self.new_entities['telegram']:
            new_tg_records.append({
                'case_id': CASE_ID,
                'entity_type': 'telegram',
                'name': handle,
                'aliases': [],
                'metadata': {'source': 'ocr_visual_evidence'},
                'risk_level': 'unknown'
            })
        
        if new_tg_records:
            try:
                supabase.table("investigation_entities").upsert(
                    new_tg_records,
                    on_conflict="case_id,entity_type,name"
                ).execute()
                print(f"  ✓ Added {len(new_tg_records)} new Telegram handles from OCR")
            except Exception as e:
                print(f"  ⚠️ Error saving Telegram handles: {e}")
    
    def generate_summary(self, results):
        """Generate OCR processing summary"""
        print("\n" + "=" * 70)
        print("📊 OCR PROCESSING SUMMARY")
        print("=" * 70)
        
        # Count total text extracted
        total_chars = sum(len(r['text']) for r in results)
        total_words = sum(len(r['text'].split()) for r in results)
        
        print(f"\n📸 Visual Files Processed: {self.processed_count}")
        print(f"❌ Failed: {self.failed_count}")
        print(f"📝 Total Text Extracted: {total_chars:,} characters, {total_words:,} words")
        
        print(f"\n💎 New Entities from OCR:")
        print(f"  • Wallets: {len(self.new_entities['wallets'])}")
        print(f"  • Telegram: {len(self.new_entities['telegram'])}")
        print(f"  • URLs: {len(self.new_entities['urls'])}")
        
        # Show top OCR results by content
        print(f"\n🏆 Top OCR Results (by text length):")
        top_results = sorted(results, key=lambda x: len(x['text']), reverse=True)[:5]
        for i, r in enumerate(top_results, 1):
            print(f"  {i}. {r['file'][:50]}...")
            print(f"     Text: {len(r['text'])} chars | Wallets: {r['wallets_found']} | TG: {r['telegram_found']}")
        
        # Show files with most wallets
        print(f"\n🔍 Files with Most Wallets:")
        wallet_results = sorted(results, key=lambda x: x['wallets_found'], reverse=True)[:5]
        for i, r in enumerate(wallet_results, 1):
            if r['wallets_found'] > 0:
                print(f"  {i}. {r['file'][:50]}... - {r['wallets_found']} wallets")
        
        # Save summary
        summary = {
            'processed': self.processed_count,
            'failed': self.failed_count,
            'total_chars': total_chars,
            'total_words': total_words,
            'new_entities': {
                'wallets': list(self.new_entities['wallets']),
                'telegram': list(self.new_entities['telegram']),
                'urls': list(self.new_entities['urls'])
            },
            'top_results': top_results
        }
        
        summary_path = Path("/root/rmi/data/ocr_processing_summary.json")
        summary_path.parent.mkdir(exist_ok=True)
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n📝 Summary saved: {summary_path}")
        
        return summary


def main():
    processor = VisualOCRProcessor()
    results = processor.process_all_visuals()
    
    if results:
        processor.save_results(results)
        processor.generate_summary(results)
    
    print("\n" + "=" * 70)
    print("✅ PART 2 COMPLETE - OCR Processing Finished")
    print("=" * 70)
    print("\n🚀 NEXT: Part 3 - Wallet Transaction Tracing (158 addresses)")


if __name__ == "__main__":
    main()
