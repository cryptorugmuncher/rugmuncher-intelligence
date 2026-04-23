#!/usr/bin/env python3
"""Export investigation data from dumps to Supabase"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from supabase import create_client
from pathlib import Path
import re
import json

SUPABASE_URL = "https://ufblzfxqwgaekrewncbi.supabase.co"
SERVICE_KEY = "sb_secret_Uye75Qavhe0ZXJCo4Uadiw_CCYWULKa"

supabase = create_client(SUPABASE_URL, SERVICE_KEY)

DUMPS_PATH = Path("/root/dumps/investigation-20260409/mixed")

def scan_files():
    """Scan all files in dumps folder"""
    files = {
        "csv": [],
        "json": [],
        "html": [],
        "txt": [],
        "images": [],
        "zip": [],
        "other": []
    }
    
    for f in DUMPS_PATH.rglob("*"):
        if f.is_file():
            suffix = f.suffix.lower()
            if suffix == '.csv':
                files["csv"].append(f)
            elif suffix == '.json' and not f.name.endswith('.json.json'):
                files["json"].append(f)
            elif suffix == '.html':
                files["html"].append(f)
            elif suffix == '.txt':
                files["txt"].append(f)
            elif suffix in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                files["images"].append(f)
            elif suffix == '.zip':
                files["zip"].append(f)
            else:
                files["other"].append(f)
    
    return files

def extract_wallets_from_files(files):
    """Extract ethereum addresses from all files"""
    eth_pattern = r'0x[a-fA-F0-9]{40}'
    wallets = {}
    
    all_files = files["csv"] + files["json"] + files["html"] + files["txt"]
    
    for file_path in all_files:
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
                found = set(re.findall(eth_pattern, content))
                for addr in found:
                    addr_lower = addr.lower()
                    if addr_lower not in wallets:
                        wallets[addr_lower] = {"sources": [], "count": 0}
                    wallets[addr_lower]["count"] += 1
                    source = str(file_path.relative_to(DUMPS_PATH))[:100]
                    if source not in wallets[addr_lower]["sources"]:
                        wallets[addr_lower]["sources"].append(source)
        except Exception as e:
            pass
    
    return wallets

def export_wallets(wallets):
    """Export wallets to Supabase"""
    print(f"\n💰 Exporting {len(wallets)} wallets...")
    
    wallet_list = list(wallets.items())
    batch_size = 100
    total = 0
    
    for i in range(0, len(wallet_list), batch_size):
        batch = wallet_list[i:i+batch_size]
        records = []
        
        for addr, data in batch:
            records.append({
                "case_id": "SOSANA-CRM-2024",
                "address": addr,
                "chain": "ethereum",
                "source": ", ".join(data["sources"][:2]),
                "metadata": {
                    "occurrences": data["count"],
                    "all_sources": data["sources"]
                }
            })
        
        try:
            result = supabase.table("investigation_wallets").upsert(
                records, 
                on_conflict="case_id,address"
            ).execute()
            total += len(batch)
            print(f"  ✅ Batch {i//batch_size + 1}: {len(batch)} wallets")
        except Exception as e:
            print(f"  ❌ Batch failed: {e}")
    
    return total

def export_evidence(files):
    """Export evidence files to Supabase"""
    print(f"\n📁 Exporting evidence files...")
    
    categories = [
        ("csv", "wallet_data"),
        ("json", "report"),
        ("html", "report"),
        ("txt", "report"),
        ("images", "visual"),
        ("zip", "archive"),
        ("other", "other")
    ]
    
    total = 0
    
    for key, category in categories:
        file_list = files.get(key, [])
        print(f"\n  📂 {category} ({key}): {len(file_list)} files")
        
        for file_path in file_list:
            try:
                record = {
                    "case_id": "SOSANA-CRM-2024",
                    "file_path": str(file_path),
                    "file_name": file_path.name[:200],
                    "file_type": file_path.suffix.lstrip('.')[:50],
                    "category": category,
                    "source": "dumps_mixed",
                    "file_size": file_path.stat().st_size
                }
                
                result = supabase.table("investigation_evidence").insert(record).execute()
                total += 1
                
            except Exception as e:
                if "duplicate" not in str(e).lower():
                    pass  # Ignore duplicates
    
    print(f"✅ Total evidence imported: {total}")
    return total

def main():
    print("=" * 60)
    print("🚀 RMI Investigation Data Export")
    print("=" * 60)
    
    # Scan files
    print("\n📂 Scanning files...")
    files = scan_files()
    total_files = sum(len(v) for v in files.values())
    print(f"  Found {total_files} files")
    for k, v in files.items():
        print(f"    {k}: {len(v)}")
    
    # Extract wallets
    print("\n🔍 Extracting wallet addresses...")
    wallets = extract_wallets_from_files(files)
    print(f"  Found {len(wallets)} unique ethereum addresses")
    
    # Export
    wallets_imported = export_wallets(wallets)
    evidence_imported = export_evidence(files)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 EXPORT COMPLETE")
    print("=" * 60)
    print(f"✅ Wallets: {wallets_imported}")
    print(f"✅ Evidence: {evidence_imported}")
    print(f"🔗 Case: SOSANA-CRM-2024")
    print("=" * 60)

if __name__ == "__main__":
    main()
