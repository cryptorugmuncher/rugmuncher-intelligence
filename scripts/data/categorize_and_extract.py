#!/usr/bin/env python3
"""Categorize and extract ZIPs: Infrastructure vs Investigation"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from supabase import create_client
from pathlib import Path
import zipfile
import shutil
import json

SUPABASE_URL = "https://ufblzfxqwgaekrewncbi.supabase.co"
SERVICE_KEY = "sb_secret_Uye75Qavhe0ZXJCo4Uadiw_CCYWULKa"

supabase = create_client(SUPABASE_URL, SERVICE_KEY)

DUMPS_PATH = Path("/root/dumps/investigation-20260409/mixed")
RMI_PATH = Path("/root/rmi")

# Categorization rules
ZIP_CATEGORIES = {
    "20260409_080014_d09b115f_docs-rag-example.zip": {
        "type": "infrastructure",
        "category": "rag_documentation",
        "target_dir": RMI_PATH / "docs/rag-system",
        "description": "RAG documentation system with ChromaDB"
    },
    "20260409_080017_3fc541bb_assets.zip": {
        "type": "infrastructure", 
        "category": "platform_assets",
        "target_dir": RMI_PATH / "assets/whitepapers",
        "description": "Whitepapers, pitch decks, diagrams"
    },
    "20260409_075410_395d1b0b_Kimi_Agent_Evidence_LLM_System_1.zip": {
        "type": "investigation",
        "category": "evidence_package",
        "case_id": "SOSANA-CRM-2024",
        "description": "Kimi Evidence LLM System - SOSANA investigation"
    },
    "20260409_075426_d19004d5_Kimi_Agent_Evidence_LLM_System_1.zip": {
        "type": "investigation",
        "category": "evidence_package",
        "case_id": "SOSANA-CRM-2024",
        "description": "Kimi Evidence LLM System - Duplicate"
    },
    "20260409_075709_f6ed4fbf_Kimi_Agent_Evidence_LLM_System_1.zip": {
        "type": "investigation",
        "category": "evidence_package", 
        "case_id": "SOSANA-CRM-2024",
        "description": "Kimi Evidence LLM System - Duplicate"
    }
}

def extract_zip(zip_path, target_dir):
    """Extract ZIP to target directory"""
    target_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(target_dir)
    return target_dir

def process_infrastructure_zip(zip_name, zip_path, config):
    """Extract infrastructure ZIP to RMI build folder"""
    print(f"\n🏗️  Infrastructure: {zip_name}")
    print(f"   Category: {config['category']}")
    print(f"   Target: {config['target_dir']}")
    
    # Extract
    extract_dir = config['target_dir']
    extract_zip(zip_path, extract_dir)
    
    # Count files
    files = list(extract_dir.rglob("*"))
    file_count = len([f for f in files if f.is_file()])
    
    print(f"   ✅ Extracted {file_count} files")
    
    # Update Supabase evidence as infrastructure
    try:
        supabase.table("investigation_evidence").update({
            "category": "infrastructure",
            "metadata": {
                "type": "infrastructure",
                "infra_category": config['category'],
                "extracted_to": str(extract_dir),
                "file_count": file_count
            }
        }).eq("file_name", zip_name).execute()
    except Exception as e:
        print(f"   ⚠️ DB update: {e}")
    
    return {"type": "infrastructure", "files": file_count, "path": str(extract_dir)}

def process_investigation_zip(zip_name, zip_path, config):
    """Process investigation ZIP - extract and categorize evidence"""
    print(f"\n🔍 Investigation: {zip_name}")
    print(f"   Case: {config['case_id']}")
    
    # Extract to investigation evidence folder
    extract_dir = RMI_PATH / f"investigation/extracted/{config['case_id']}/{zip_name[:-4]}"
    extract_zip(zip_path, extract_dir)
    
    # Categorize contents
    categorized = {
        "reports": [],
        "wallets": [],
        "telegram": [],
        "scripts": [],
        "database": [],
        "other": []
    }
    
    for f in extract_dir.rglob("*"):
        if f.is_file():
            suffix = f.suffix.lower()
            rel_path = str(f.relative_to(extract_dir))
            
            if suffix == '.csv' or 'wallet' in rel_path.lower():
                categorized["wallets"].append(rel_path)
            elif suffix in ['.txt'] and ('telegram' in rel_path.lower() or 'chat' in rel_path.lower()):
                categorized["telegram"].append(rel_path)
            elif suffix in ['.md', '.html']:
                categorized["reports"].append(rel_path)
            elif suffix in ['.py', '.js', '.sql']:
                categorized["scripts"].append(rel_path)
            elif suffix in ['.json', '.sqlite', '.db']:
                categorized["database"].append(rel_path)
            else:
                categorized["other"].append(rel_path)
    
    # Summary
    total_files = sum(len(v) for v in categorized.values())
    print(f"   ✅ Extracted {total_files} files:")
    for cat, files in categorized.items():
        if files:
            print(f"      • {cat}: {len(files)}")
    
    # Update Supabase
    try:
        supabase.table("investigation_evidence").update({
            "category": "evidence_extracted",
            "metadata": {
                "type": "investigation",
                "case_id": config['case_id'],
                "extracted_to": str(extract_dir),
                "contents": {k: len(v) for k, v in categorized.items()},
                "is_duplicate": "duplicate" in config['description'].lower()
            }
        }).eq("file_name", zip_name).execute()
    except Exception as e:
        print(f"   ⚠️ DB update: {e}")
    
    return {
        "type": "investigation", 
        "case_id": config['case_id'],
        "files": total_files,
        "path": str(extract_dir),
        "contents": categorized
    }

def main():
    print("=" * 70)
    print("📦 ZIP CATEGORIZATION & EXTRACTION")
    print("   Infrastructure → RMI Build Folders")
    print("   Investigation → Evidence Database")
    print("=" * 70)
    
    results = {
        "infrastructure": [],
        "investigation": []
    }
    
    for zip_name, config in ZIP_CATEGORIES.items():
        zip_path = DUMPS_PATH / zip_name
        
        if not zip_path.exists():
            print(f"\n⚠️  Missing: {zip_name}")
            continue
        
        if config["type"] == "infrastructure":
            result = process_infrastructure_zip(zip_name, zip_path, config)
            results["infrastructure"].append(result)
        else:
            result = process_investigation_zip(zip_name, zip_path, config)
            results["investigation"].append(result)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 EXTRACTION SUMMARY")
    print("=" * 70)
    
    print(f"\n🏗️  Infrastructure Extracted:")
    for r in results["infrastructure"]:
        print(f"   • {r['files']} files → {r['path']}")
    
    print(f"\n🔍 Investigation Extracted:")
    for r in results["investigation"]:
        print(f"   • Case {r['case_id']}: {r['files']} files")
        for cat, count in r['contents'].items():
            if count:
                print(f"      - {cat}: {len(r['contents'][cat])}")
    
    print("\n✅ Categorization complete!")
    
    # Save summary
    summary_path = RMI_PATH / "data/extraction_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📝 Summary saved: {summary_path}")

if __name__ == "__main__":
    main()
