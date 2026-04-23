"""
================================================================================
TELEGRAM HTML EXPORT PARSER
Evidence Fortress v4.0

Parses Telegram Desktop HTML exports for intelligence extraction.

Usage:
    python scripts/telegram_parser.py --input messages.html --output intel.json
================================================================================
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing BeautifulSoup...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "beautifulsoup4"])
    from bs4 import BeautifulSoup


class TelegramHTMLParser:
    """Parse Telegram Desktop HTML exports."""
    
    # Patterns for intelligence extraction
    SOLANA_ADDRESS_PATTERN = re.compile(r'[1-9A-HJ-NP-Za-km-z]{32,44}')
    EVM_ADDRESS_PATTERN = re.compile(r'0x[a-fA-F0-9]{40}')
    TELEGRAM_HANDLE_PATTERN = re.compile(r'@(\w{3,32})')
    URL_PATTERN = re.compile(r'https?://[^\s<>"\']+')
    
    # Keywords for operational analysis
    OPERATIONAL_KEYWORDS = [
        'token', 'wallet', 'launch', 'pump', 'rug', 'whale', 'dev',
        'marketing', 'liquidity', 'group', 'dm', 'treasury', 'deploy',
        'mint', 'sell', 'buy', 'dump', 'cex', 'dex', 'kyc'
    ]
    
    def __init__(self):
        self.all_addresses = set()
        self.all_handles = set()
        self.all_urls = set()
        self.participants = set()
        self.keyword_mentions = defaultdict(list)
        self.messages = []
    
    def parse_file(self, file_path: str) -> Dict:
        """Parse a single Telegram HTML export file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Extract chat title
        chat_title = ""
        title_elem = soup.find('div', class_='text bold')
        if title_elem:
            chat_title = title_elem.get_text(strip=True)
        
        # Extract messages
        messages = []
        message_divs = soup.find_all('div', class_=lambda x: x and 'message' in x and 'default' in x)
        
        current_sender = "Unknown"
        for msg_div in message_divs:
            # Check if this is a new message or joined continuation
            if 'joined' not in msg_div.get('class', []):
                from_name_elem = msg_div.find('div', class_='from_name')
                if from_name_elem:
                    current_sender = from_name_elem.get_text(strip=True)
            
            # Get timestamp
            date_elem = msg_div.find('div', class_='pull_right date details')
            timestamp = date_elem.get('title', '') if date_elem else ""
            
            # Get message text
            text_elem = msg_div.find('div', class_='text')
            text = text_elem.get_text(strip=True) if text_elem else ""
            
            # Extract photos
            photo_elem = msg_div.find('a', class_='photo_wrap')
            has_photo = photo_elem is not None
            
            # Extract files
            file_elem = msg_div.find('div', class_='media_wrap_name')
            file_name = file_elem.get_text(strip=True) if file_elem else None
            
            if text or has_photo or file_name:
                msg_data = {
                    'sender': current_sender,
                    'timestamp': timestamp,
                    'text': text,
                    'has_photo': has_photo,
                    'file_name': file_name
                }
                messages.append(msg_data)
                
                # Extract intelligence from text
                self._extract_intelligence(text, msg_data)
        
        return {
            'chat_title': chat_title,
            'file_path': file_path,
            'message_count': len(messages),
            'messages': messages,
            'participants': list(set(m['sender'] for m in messages))
        }
    
    def _extract_intelligence(self, text: str, msg_context: Dict):
        """Extract intelligence from message text."""
        # Extract addresses
        sol_addresses = self.SOLANA_ADDRESS_PATTERN.findall(text)
        evm_addresses = self.EVM_ADDRESS_PATTERN.findall(text)
        
        # Filter false positives
        false_positives = {'https', 'http', 'www', 'com', 'html', 'json', 'onclick'}
        sol_addresses = [a for a in sol_addresses if a not in false_positives and len(a) >= 32]
        
        self.all_addresses.update(sol_addresses)
        self.all_addresses.update(evm_addresses)
        
        # Extract Telegram handles
        handles = self.TELEGRAM_HANDLE_PATTERN.findall(text)
        self.all_handles.update(handles)
        
        # Extract URLs
        urls = self.URL_PATTERN.findall(text)
        self.all_urls.update(urls)
        
        # Track participants
        self.participants.add(msg_context['sender'])
        
        # Track keywords
        text_lower = text.lower()
        for keyword in self.OPERATIONAL_KEYWORDS:
            if keyword in text_lower:
                self.keyword_mentions[keyword].append({
                    'sender': msg_context['sender'],
                    'timestamp': msg_context['timestamp'],
                    'text': text[:200] + "..." if len(text) > 200 else text
                })
    
    def parse_multiple(self, file_paths: List[str]) -> Dict:
        """Parse multiple Telegram HTML files."""
        all_chats = []
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                try:
                    chat_data = self.parse_file(file_path)
                    all_chats.append(chat_data)
                    print(f"✓ Parsed: {os.path.basename(file_path)} - {chat_data['chat_title']} ({chat_data['message_count']} messages)")
                except Exception as e:
                    print(f"✗ Error parsing {file_path}: {e}")
            else:
                print(f"✗ File not found: {file_path}")
        
        return {
            'chats': all_chats,
            'summary': self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict:
        """Generate intelligence summary."""
        return {
            'total_addresses': len(self.all_addresses),
            'total_handles': len(self.all_handles),
            'total_urls': len(self.all_urls),
            'total_participants': len(self.participants),
            'participants': sorted(list(self.participants)),
            'addresses': sorted(list(self.all_addresses)),
            'handles': sorted(list(self.all_handles)),
            'keyword_mentions': {
                k: len(v) for k, v in sorted(self.keyword_mentions.items(), key=lambda x: -len(x[1]))
            },
            'top_keywords': self._get_top_keyword_examples()
        }
    
    def _get_top_keyword_examples(self, max_per_keyword: int = 3) -> Dict:
        """Get example messages for top keywords."""
        examples = {}
        for keyword, mentions in sorted(self.keyword_mentions.items(), key=lambda x: -len(x[1])):
            examples[keyword] = mentions[:max_per_keyword]
        return examples
    
    def export_to_json(self, output_path: str, data: Dict):
        """Export parsed data to JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Exported to: {output_path}")


def find_wallet_clusters(addresses: List[str]) -> Dict:
    """Identify potential wallet clusters from addresses."""
    clusters = defaultdict(list)
    
    # Group by first characters (potential vanity/pattern wallets)
    for addr in addresses:
        prefix = addr[:6]
        clusters[prefix].append(addr)
    
    # Only return clusters with multiple addresses
    return {k: v for k, v in clusters.items() if len(v) > 1}


def main():
    parser = argparse.ArgumentParser(description='Parse Telegram HTML exports')
    parser.add_argument('--input', '-i', nargs='+', required=True, help='Input HTML file(s)')
    parser.add_argument('--output', '-o', default='telegram_intel.json', help='Output JSON file')
    
    args = parser.parse_args()
    
    print("="*70)
    print("TELEGRAM HTML EXPORT PARSER")
    print("="*70)
    
    # Parse files
    tg_parser = TelegramHTMLParser()
    result = tg_parser.parse_multiple(args.input)
    
    # Generate summary
    summary = result['summary']
    
    print("\n" + "="*70)
    print("INTELLIGENCE SUMMARY")
    print("="*70)
    print(f"Participants: {summary['total_participants']}")
    print(f"Wallet Addresses: {summary['total_addresses']}")
    print(f"Telegram Handles: {summary['total_handles']}")
    print(f"URLs: {summary['total_urls']}")
    
    print("\n" + "="*70)
    print("PARTICIPANTS")
    print("="*70)
    for p in summary['participants']:
        print(f"  • {p}")
    
    print("\n" + "="*70)
    print("TOP KEYWORDS")
    print("="*70)
    for keyword, count in list(summary['keyword_mentions'].items())[:10]:
        print(f"  {keyword}: {count} mentions")
    
    # Find wallet clusters
    clusters = find_wallet_clusters(summary['addresses'])
    if clusters:
        print("\n" + "="*70)
        print("POTENTIAL WALLET CLUSTERS")
        print("="*70)
        for prefix, addrs in list(clusters.items())[:5]:
            print(f"  Prefix '{prefix}...': {len(addrs)} addresses")
    
    # Export
    tg_parser.export_to_json(args.output, result)


if __name__ == '__main__':
    main()
