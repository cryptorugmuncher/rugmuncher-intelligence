#!/usr/bin/env python3
"""
Part 1: Deep Processing - Entity Extraction, Timeline Building, Relationship Mapping
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from supabase import create_client
from pathlib import Path
import re
import json
from datetime import datetime
from collections import defaultdict

SUPABASE_URL = "https://ufblzfxqwgaekrewncbi.supabase.co"
SERVICE_KEY = "sb_secret_Uye75Qavhe0ZXJCo4Uadiw_CCYWULKa"

supabase = create_client(SUPABASE_URL, SERVICE_KEY)

EVIDENCE_PATH = Path("/root/rmi/investigation/extracted/SOSANA-CRM-2024")
CASE_ID = "SOSANA-CRM-2024"

class EntityExtractor:
    """Extract entities from investigation files"""
    
    PATTERNS = {
        'ethereum_wallet': r'0x[a-fA-F0-9]{40}',
        'solana_wallet': r'[1-9A-HJ-NP-Za-km-z]{32,44}',
        'telegram_handle': r'@([a-zA-Z0-9_]{5,32})',
        'twitter_handle': r'@([a-zA-Z0-9_]{1,15})',
        'url': r'https?://[^\s<>"{}|\\^`\[\]]+',
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'token_symbol': r'\$([A-Z]{2,10})',
        'amount': r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(USD|USDC|USDT|SOL|ETH|CRM)',
        'date': r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        'percentage': r'(\d{1,3}(?:\.\d+)?)\s*%',
    }
    
    SUSPICIOUS_KEYWORDS = [
        'sosana', 'rug', 'scam', 'honeypot', 'fake', 'manipulation',
        'pump', 'dump', 'insider', 'sybil', 'bot', 'spam', 'fraud'
    ]
    
    def __init__(self):
        self.entities = defaultdict(lambda: defaultdict(set))
        
    def extract_from_file(self, file_path):
        """Extract all entities from a single file"""
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
                content_lower = content.lower()
        except:
            return {}
        
        file_entities = {
            'wallets': set(),
            'telegram': set(),
            'twitter': set(),
            'urls': set(),
            'emails': set(),
            'tokens': set(),
            'amounts': [],
            'dates': set(),
            'percentages': set(),
            'risk_keywords': [],
            'mentions_sosana': 'sosana' in content_lower,
            'mentions_crm': 'crm' in content_lower or '$crm' in content_lower,
        }
        
        # Extract wallets
        for match in re.finditer(self.PATTERNS['ethereum_wallet'], content):
            file_entities['wallets'].add(match.group().lower())
        
        # Extract Telegram handles
        for match in re.finditer(self.PATTERNS['telegram_handle'], content):
            handle = match.group(1)
            if handle.lower() not in ['sosanacrm', 'cryptorugmunch']:
                file_entities['telegram'].add(handle)
        
        # Extract Twitter handles
        for match in re.finditer(self.PATTERNS['twitter_handle'], content):
            file_entities['twitter'].add(match.group(1))
        
        # Extract URLs
        for match in re.finditer(self.PATTERNS['url'], content):
            url = match.group()
            if not url.endswith(('.png', '.jpg', '.gif')):
                file_entities['urls'].add(url[:500])
        
        # Extract emails
        for match in re.finditer(self.PATTERNS['email'], content):
            file_entities['emails'].add(match.group().lower())
        
        # Extract token symbols
        for match in re.finditer(self.PATTERNS['token_symbol'], content):
            file_entities['tokens'].add(match.group(1))
        
        # Extract amounts
        for match in re.finditer(self.PATTERNS['amount'], content):
            file_entities['amounts'].append({
                'value': match.group(1),
                'currency': match.group(2)
            })
        
        # Extract dates
        for match in re.finditer(self.PATTERNS['date'], content):
            file_entities['dates'].add(match.group())
        
        # Extract percentages
        for match in re.finditer(self.PATTERNS['percentage'], content):
            file_entities['percentages'].add(float(match.group(1)))
        
        # Risk keywords
        for keyword in self.SUSPICIOUS_KEYWORDS:
            if keyword in content_lower:
                file_entities['risk_keywords'].append(keyword)
        
        return file_entities


class TimelineBuilder:
    """Build investigation timeline from evidence"""
    
    def __init__(self):
        self.events = []
        
    def extract_date(self, text):
        """Extract date from text"""
        patterns = [
            r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})',
            r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    def add_event(self, date, event_type, description, source_file, entities=None):
        """Add event to timeline"""
        self.events.append({
            'date': date,
            'event_type': event_type,
            'description': description[:500],
            'source': source_file,
            'entities': entities or {}
        })


class DeepProcessor:
    """Main deep processing orchestrator"""
    
    def __init__(self):
        self.extractor = EntityExtractor()
        self.timeline = TimelineBuilder()
        self.processed_files = 0
        self.all_entities = {
            'wallets': defaultdict(int),
            'telegram': defaultdict(int),
            'urls': defaultdict(int),
            'emails': defaultdict(int),
            'tokens': defaultdict(int),
        }
        
    def process_all_evidence(self):
        """Process all evidence files"""
        print("=" * 70)
        print("🔍 PART 1: DEEP PROCESSING - ENTITY EXTRACTION & TIMELINE")
        print("=" * 70)
        
        # Get all files from evidence
        evidence_files = list(EVIDENCE_PATH.rglob("*"))
        text_files = [f for f in evidence_files if f.is_file() and 
                     f.suffix.lower() in ['.txt', '.md', '.html', '.csv', '.json']]
        
        print(f"\n📂 Found {len(text_files)} text files to process")
        
        # Process each file
        for i, file_path in enumerate(text_files):
            if i % 50 == 0:
                print(f"  Processing {i}/{len(text_files)}...")
            
            entities = self.extractor.extract_from_file(file_path)
            if not entities:
                continue
            
            self.processed_files += 1
            rel_path = str(file_path.relative_to(EVIDENCE_PATH))
            
            # Aggregate entities
            for wallet in entities.get('wallets', []):
                self.all_entities['wallets'][wallet] += 1
            for tg in entities.get('telegram', []):
                self.all_entities['telegram'][tg] += 1
            for url in entities.get('urls', []):
                self.all_entities['urls'][url] += 1
            for email in entities.get('emails', []):
                self.all_entities['emails'][email] += 1
            for token in entities.get('tokens', []):
                self.all_entities['tokens'][token] += 1
            
            # Add timeline events for high-risk files
            if entities.get('mentions_sosana') or len(entities.get('risk_keywords', [])) > 2:
                dates_list = list(entities.get('dates', set()))
                self.timeline.add_event(
                    date=dates_list[0] if dates_list else 'unknown',
                    event_type='suspicious_activity',
                    description=f"Evidence file: {rel_path}",
                    source_file=rel_path,
                    entities=entities
                )
        
        print(f"\n✅ Processed {self.processed_files} files")
        
    def save_to_database(self):
        """Save extracted entities to Supabase"""
        print("\n💾 Saving to database...")
        
        # Save entities
        entity_records = []
        
        # Save high-frequency wallets as entities
        for wallet, count in self.all_entities['wallets'].items():
            if count >= 2:  # Only wallets appearing multiple times
                entity_records.append({
                    'case_id': CASE_ID,
                    'entity_type': 'wallet',
                    'name': wallet,
                    'aliases': [],
                    'wallets': {'primary': wallet},
                    'metadata': {
                        'occurrences': count,
                        'source': 'deep_processing'
                    },
                    'risk_level': 'high' if count > 5 else 'medium'
                })
        
        # Save Telegram handles
        for handle, count in self.all_entities['telegram'].items():
            entity_records.append({
                'case_id': CASE_ID,
                'entity_type': 'telegram',
                'name': handle,
                'aliases': [],
                'metadata': {
                    'occurrences': count,
                    'source': 'deep_processing'
                },
                'risk_level': 'unknown'
            })
        
        # Batch insert entities
        if entity_records:
            batch_size = 50
            for i in range(0, len(entity_records), batch_size):
                batch = entity_records[i:i+batch_size]
                try:
                    supabase.table("investigation_entities").upsert(
                        batch, 
                        on_conflict="case_id,name,entity_type"
                    ).execute()
                except Exception as e:
                    print(f"  Error saving entities: {e}")
            
            print(f"  ✓ Saved {len(entity_records)} entities")
        
        # Save timeline events
        if self.timeline.events:
            timeline_records = []
            for event in self.timeline.events[:100]:  # Limit to 100 events
                timeline_records.append({
                    'case_id': CASE_ID,
                    'event_date': event['date'] if event['date'] != 'unknown' else None,
                    'event_type': event['event_type'],
                    'description': event['description'],
                    'related_entities': event['entities'],
                    'evidence_refs': {'source_file': event['source']}
                })
            
            try:
                supabase.table("investigation_timeline").insert(timeline_records).execute()
                print(f"  ✓ Saved {len(timeline_records)} timeline events")
            except Exception as e:
                print(f"  Error saving timeline: {e}")
    
    def generate_summary(self):
        """Generate processing summary"""
        print("\n" + "=" * 70)
        print("📊 PROCESSING SUMMARY")
        print("=" * 70)
        
        print(f"\n📁 Files Processed: {self.processed_files}")
        
        print(f"\n💎 Entities Extracted:")
        print(f"  • Wallets: {len(self.all_entities['wallets'])} unique")
        print(f"  • Telegram: {len(self.all_entities['telegram'])} unique")
        print(f"  • URLs: {len(self.all_entities['urls'])} unique")
        print(f"  • Emails: {len(self.all_entities['emails'])} unique")
        print(f"  • Tokens: {len(self.all_entities['tokens'])} unique")
        
        print(f"\n🏆 Top Wallets (by frequency):")
        top_wallets = sorted(self.all_entities['wallets'].items(), key=lambda x: -x[1])[:10]
        for wallet, count in top_wallets:
            print(f"  • {wallet[:20]}... ({count} occurrences)")
        
        print(f"\n📱 Top Telegram Handles:")
        top_tg = sorted(self.all_entities['telegram'].items(), key=lambda x: -x[1])[:5]
        for handle, count in top_tg:
            print(f"  • @{handle} ({count} occurrences)")
        
        print(f"\n🔗 Top Tokens Mentioned:")
        top_tokens = sorted(self.all_entities['tokens'].items(), key=lambda x: -x[1])[:5]
        for token, count in top_tokens:
            print(f"  • ${token} ({count} occurrences)")
        
        print(f"\n⏱️  Timeline Events: {len(self.timeline.events)}")
        
        # Save summary to file
        summary = {
            'processed_files': self.processed_files,
            'entities': {
                'wallets': dict(self.all_entities['wallets']),
                'telegram': dict(self.all_entities['telegram']),
                'tokens': dict(self.all_entities['tokens']),
            },
            'timeline_events': len(self.timeline.events)
        }
        
        summary_path = Path("/root/rmi/data/deep_processing_summary.json")
        summary_path.parent.mkdir(exist_ok=True)
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n📝 Summary saved: {summary_path}")
        
        return summary


def main():
    processor = DeepProcessor()
    processor.process_all_evidence()
    processor.save_to_database()
    processor.generate_summary()
    
    print("\n" + "=" * 70)
    print("✅ PART 1 COMPLETE - Deep Processing Finished")
    print("=" * 70)
    print("\nNext: Part 2 (OCR on visual evidence)")


if __name__ == "__main__":
    main()
