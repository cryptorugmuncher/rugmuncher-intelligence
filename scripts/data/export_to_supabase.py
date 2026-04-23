#!/usr/bin/env python3
"""Export all investigation data to Supabase"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from supabase import create_client
import json
import os
from pathlib import Path

SUPABASE_URL = "https://ufblzfxqwgaekrewncbi.supabase.co"
SERVICE_KEY = "sb_secret_Uye75Qavhe0ZXJCo4Uadiw_CCYWULKa"

supabase = create_client(SUPABASE_URL, SERVICE_KEY)

def load_extracted_data():
    """Load wallets and evidence from extracted files"""
    wallets = []
    evidence = []
    
    # Load categorized report if exists
    report_path = Path("investigation/processor/categorized_report.json")
    if report_path.exists():
        with open(report_path) as f:
            report = json.load(f)
    else:
        # Generate from dumps folder
        report = {
            "telegram_chats": [],
            "wallet_data": [],
            "visual_evidence": [],
            "forensic_reports": []
        }
        dumps_path = Path("/root/dumps")
        for f in dumps_path.iterdir():
            if f.is_file():
                name = f.name.lower()
                if 'telegram' in name or 'chat' in name:
                    report["telegram_chats"].append(str(f))
                elif 'wallet' in name or '.csv' in name:
                    report["wallet_data"].append(str(f))
                elif any(ext in name for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    report["visual_evidence"].append(str(f))
                elif any(ext in name for ext in ['.html', '.txt', '.json', '.md']):
                    report["forensic_reports"].append(str(f))
    
    return report

def extract_wallets_from_files(report):
    """Extract all wallet addresses from files"""
    import re
    wallets = set()
    wallet_sources = {}
    
    ethereum_pattern = r'0x[a-fA-F0-9]{40}'
    
    # Check wallet_data files
    for file_path in report.get("wallet_data", []):
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
                found = re.findall(ethereum_pattern, content)
                for addr in found:
                    wallets.add(addr.lower())
                    if addr.lower() not in wallet_sources:
                        wallet_sources[addr.lower()] = []
                    wallet_sources[addr.lower()].append(os.path.basename(file_path))
        except Exception as e:
            print(f"  ⚠️ Error reading {file_path}: {e}")
    
    # Also check forensic reports
    for file_path in report.get("forensic_reports", []):
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
                found = re.findall(ethereum_pattern, content)
                for addr in found:
                    wallets.add(addr.lower())
                    if addr.lower() not in wallet_sources:
                        wallet_sources[addr.lower()] = []
                    wallet_sources[addr.lower()].append(os.path.basename(file_path))
        except:
            pass
    
    return list(wallets), wallet_sources

def export_wallets(wallets, wallet_sources):
    """Export wallets to Supabase in batches"""
    print(f"\n💰 Exporting {len(wallets)} wallets...")
    
    batch_size = 100
    total_imported = 0
    
    for i in range(0, len(wallets), batch_size):
        batch = wallets[i:i+batch_size]
        records = []
        
        for addr in batch:
            records.append({
                "case_id": "SOSANA-CRM-2024",
                "address": addr,
                "chain": "ethereum",
                "source": ", ".join(wallet_sources.get(addr, [])[:3]),  # First 3 sources
                "metadata": {"sources": wallet_sources.get(addr, [])}
            })
        
        try:
            result = supabase.table("investigation_wallets").upsert(records, on_conflict="case_id,address").execute()
            total_imported += len(records)
            print(f"  ✅ Batch {i//batch_size + 1}: {len(records)} wallets")
        except Exception as e:
            print(f"  ❌ Batch {i//batch_size + 1} failed: {e}")
    
    print(f"✅ Total wallets imported: {total_imported}")
    return total_imported

def export_evidence(report):
    """Export evidence files to Supabase"""
    print(f"\n📁 Exporting evidence files...")
    
    categories = {
        "telegram_chats": "telegram",
        "wallet_data": "wallet_data",
        "visual_evidence": "visual",
        "forensic_reports": "report"
    }
    
    total_imported = 0
    
    for key, category in categories.items():
        files = report.get(key, [])
        print(f"\n  📂 {category}: {len(files)} files")
        
        for file_path in files:
            try:
                fpath = Path(file_path)
                record = {
                    "case_id": "SOSANA-CRM-2024",
                    "file_path": str(file_path),
                    "file_name": fpath.name,
                    "file_type": fpath.suffix.lstrip('.'),
                    "category": category,
                    "source": "dumps_analysis",
                    "file_size": fpath.stat().st_size if fpath.exists() else 0
                }
                
                result = supabase.table("investigation_evidence").insert(record).execute()
                total_imported += 1
                
            except Exception as e:
                print(f"    ⚠️ Failed to import {file_path}: {e}")
    
    print(f"✅ Total evidence imported: {total_imported}")
    return total_imported

def main():
    print("=" * 60)
    print("🚀 RMI Investigation Data Export to Supabase")
    print("=" * 60)
    
    # Verify connection
    print("\n🔌 Testing connection...")
    try:
        result = supabase.table("investigation_cases").select("*").execute()
        print(f"✅ Connected! Found {len(result.data)} cases")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Load data
    print("\n📂 Loading investigation data...")
    report = load_extracted_data()
    print(f"  Telegram chats: {len(report.get('telegram_chats', []))}")
    print(f"  Wallet data: {len(report.get('wallet_data', []))}")
    print(f"  Visual evidence: {len(report.get('visual_evidence', []))}")
    print(f"  Forensic reports: {len(report.get('forensic_reports', []))}")
    
    # Extract wallets
    print("\n🔍 Extracting wallet addresses...")
    wallets, wallet_sources = extract_wallets_from_files(report)
    print(f"  Found {len(wallets)} unique wallet addresses")
    
    # Export
    wallets_imported = export_wallets(wallets, wallet_sources)
    evidence_imported = export_evidence(report)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 EXPORT SUMMARY")
    print("=" * 60)
    print(f"✅ Wallets imported: {wallets_imported}")
    print(f"✅ Evidence files imported: {evidence_imported}")
    print(f"🔗 Case ID: SOSANA-CRM-2024")
    print("=" * 60)

if __name__ == "__main__":
    main()
