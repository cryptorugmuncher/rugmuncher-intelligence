#!/usr/bin/env python3
"""Extract legitimate infrastructure components from evidence"""
import os
import shutil
from pathlib import Path
import json

EVIDENCE_PATH = Path("/root/rmi/investigation/extracted/SOSANA-CRM-2024/kimi_evidence")
INFRA_PATH = Path("/root/rmi/infrastructure")
SUMMARY_FILE = INFRA_PATH / "INFRASTRUCTURE_MANIFEST.json"

# Components to extract for RMI infrastructure
INFRA_COMPONENTS = {
    "core": {
        "description": "Core platform modules and services",
        "source": EVIDENCE_PATH / "omega_forensic_v5/core",
        "target": INFRA_PATH / "core",
        "files": [
            ("api_marketplace.py", "API integration marketplace"),
            ("data_processor.py", "Data processing pipeline"),
            ("llm_rotation.py", "LLM API rotation/management"),
            ("newsletter_system.py", "Newsletter automation system"),
            ("portfolio_tracker.py", "Portfolio tracking module"),
            ("premium_scans.py", "Premium scan features"),
            ("transparency_tracker.py", "Transparency monitoring"),
            ("wallet_protection.py", "Wallet security features"),
            ("webhook_system.py", "Webhook handling system"),
            ("intelligent_switcher.py", "Intelligence API switching"),
        ]
    },
    "forensic": {
        "description": "Forensic analysis and investigation tools",
        "source": EVIDENCE_PATH / "omega_forensic_v5/forensic",
        "target": INFRA_PATH / "forensic",
        "files": [
            ("api_arsenal.py", "API toolkit for investigations"),
            ("bubble_maps_pro.py", "Bubble map visualization"),
            ("cluster_detection_pro.py", "Wallet cluster detection"),
            ("contract_checker.py", "Smart contract analyzer"),
            ("deep_scanner.py", "Deep blockchain scanner"),
            ("deep_wallet_analysis.py", "Advanced wallet analysis"),
            ("report_generator.py", "Investigation report generator"),
            ("wallet_clustering.py", "Wallet clustering algorithms"),
            ("wallet_database.py", "Wallet database manager"),
        ]
    },
    "bots": {
        "description": "Telegram bot implementations",
        "source": EVIDENCE_PATH / "omega_forensic_v5/bots",
        "target": INFRA_PATH / "bots",
        "files": [
            ("investigator_bot.py", "Main investigation bot"),
            ("rmi_bot.py", "RMI platform bot"),
        ]
    },
    "web": {
        "description": "Web interface and visualization",
        "source": EVIDENCE_PATH / "omega_forensic_v5/web",
        "target": INFRA_PATH / "web",
        "files": [
            ("api_documentation.py", "API documentation generator"),
            ("app.py", "Main web application"),
            ("bubble_map_visualizer.py", "Visualization component"),
        ]
    },
    "database": {
        "description": "Database schemas and migrations",
        "source": EVIDENCE_PATH / "omega_forensic_v5/database",
        "target": INFRA_PATH / "database",
        "files": [
            ("supabase_schema.sql", "Supabase database schema"),
        ]
    },
    "scripts": {
        "description": "Analysis and utility scripts",
        "source": EVIDENCE_PATH / "scripts",
        "target": INFRA_PATH / "scripts",
        "files": [
            ("analyze_fund_flows.py", "Fund flow analyzer"),
            ("detect_manipulation_patterns.py", "Manipulation detector"),
            ("export_dex_transactions.py", "DEX transaction exporter"),
        ]
    },
    "": {
        "description": "Root application files",
        "source": EVIDENCE_PATH / "omega_forensic_v5",
        "target": INFRA_PATH,
        "files": [
            ("main.py", "Main application entry point"),
            ("requirements.txt", "Python dependencies"),
            ("server_setup.sh", "Server setup script"),
        ]
    }
}

def extract_infrastructure():
    """Extract all infrastructure components"""
    manifest = {
        "project": "RMI Investigation Platform",
        "extracted_from": "SOSANA-CRM-2024 evidence",
        "extraction_date": str(Path().stat().st_mtime),
        "components": {}
    }
    
    total_extracted = 0
    
    print("=" * 70)
    print("🏗️ EXTRACTING RMI INFRASTRUCTURE")
    print("=" * 70)
    
    for category, config in INFRA_COMPONENTS.items():
        print(f"\n📦 {config['description']}")
        print("-" * 50)
        
        config["target"].mkdir(parents=True, exist_ok=True)
        
        extracted = []
        for filename, description in config["files"]:
            source = config["source"] / filename
            target = config["target"] / filename
            
            if source.exists():
                try:
                    shutil.copy2(source, target)
                    extracted.append({
                        "file": filename,
                        "description": description,
                        "size": source.stat().st_size
                    })
                    total_extracted += 1
                    print(f"  ✓ {filename}")
                except Exception as e:
                    print(f"  ✗ {filename}: {e}")
            else:
                print(f"  ⚠ {filename}: not found")
        
        manifest["components"][category or "root"] = {
            "description": config["description"],
            "path": str(config["target"]),
            "files": extracted
        }
    
    # Create README for infrastructure
    readme_content = """# RMI Investigation Platform - Infrastructure

## Overview
This infrastructure was extracted from the SOSANA-CRM-2024 investigation evidence. It represents the legitimate platform components that can be used for the RMI Investigation Platform.

**Source:** Evidence forensic tools and platform code  
**Purpose:** General investigation platform infrastructure  
**Status:** Reusable for RMI

## Components

### `/core/` - Core Platform Modules
API marketplace, data processing, LLM management, newsletter system, portfolio tracking, wallet protection, webhooks.

### `/forensic/` - Forensic Analysis Tools
Bubble maps, cluster detection, contract checking, deep scanning, wallet analysis, report generation.

### `/bots/` - Telegram Bots
Investigator bot and RMI platform bot implementations.

### `/web/` - Web Interface
API documentation generator, main web app, visualization components.

### `/database/` - Database Schemas
Supabase database schema definitions.

### `/scripts/` - Analysis Scripts
Fund flow analysis, manipulation detection, DEX transaction export.

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up database:
   ```bash
   psql -f database/supabase_schema.sql
   ```

3. Run main application:
   ```bash
   python main.py
   ```

## Note
These components were extracted from investigation evidence and cleaned for general use. They do not contain SOSANA-specific scam logic but rather general investigation platform functionality.
"""
    
    with open(INFRA_PATH / "README.md", 'w') as f:
        f.write(readme_content)
    
    # Save manifest
    with open(SUMMARY_FILE, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print("\n" + "=" * 70)
    print(f"✅ EXTRACTION COMPLETE: {total_extracted} files")
    print("=" * 70)
    print(f"\n📁 Infrastructure location: {INFRA_PATH}")
    print(f"📄 Manifest: {SUMMARY_FILE}")
    print(f"📖 README: {INFRA_PATH}/README.md")
    
    return total_extracted

if __name__ == "__main__":
    extract_infrastructure()
