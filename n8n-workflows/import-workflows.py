#!/usr/bin/env python3
"""
RMI n8n Workflow Bulk Import - Python Script
Uses n8n API to import all workflows automatically
"""

import json
import sys
import os
from pathlib import Path

try:
    import requests
except ImportError:
    print("Installing requests library...")
    os.system("pip3 install requests -q")
    import requests

N8N_HOST = "http://167.86.116.51:5678"
WORKFLOWS_DIR = Path("/root/rmi/n8n-workflows")

WORKFLOWS = [
    ("rmi_investigation_webhook.json", "Investigation Webhook Handler"),
    ("rmi_scam_alert_flow.json", "RMI Scam Alert Flow"),
    ("rmi_daily_intelligence.json", "Daily Intelligence Report"),
    ("scam-alert-workflow-fixed.json", "Scam Alert System"),
    ("badge-unlock-workflow-fixed.json", "Badge Unlock Notifications"),
    ("high-risk-alert.json", "High Risk Alert"),
    ("whale-alert.json", "Whale Alert"),
]

def check_n8n_health():
    """Check if n8n is running"""
    try:
        response = requests.get(f"{N8N_HOST}/healthz", timeout=5)
        return response.status_code == 200
    except:
        return False

def import_workflow(api_key, filepath, name):
    """Import a single workflow via API"""
    try:
        with open(filepath, 'r') as f:
            workflow_data = json.load(f)

        # n8n API endpoint for creating workflow
        url = f"{N8N_HOST}/api/v1/workflows"
        headers = {
            "Content-Type": "application/json",
            "X-N8N-API-KEY": api_key
        }

        # The workflow data structure (tags removed - n8n API doesn't accept them)
        payload = {
            "name": workflow_data.get("name", name),
            "nodes": workflow_data.get("nodes", []),
            "connections": workflow_data.get("connections", {}),
            "settings": workflow_data.get("settings", {}),
            "staticData": workflow_data.get("staticData")
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            return True, "Imported successfully"
        elif response.status_code == 409 or "already exists" in response.text.lower():
            return True, "Already exists"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"

    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("🐲 RMI n8n Workflow Bulk Import (Python)")
    print("=" * 60)
    print()

    # Check n8n health
    print("🔍 Checking n8n...")
    if not check_n8n_health():
        print(f"❌ n8n is not running at {N8N_HOST}")
        sys.exit(1)
    print("✅ n8n is running")
    print()

    # Get API key
    api_key = os.environ.get("N8N_API_KEY", "")

    if not api_key or api_key == "n8n_api_generate_in_ui_after_start":
        if len(sys.argv) > 1:
            api_key = sys.argv[1]
        else:
            print("❌ N8N_API_KEY required")
            print()
            print("Get your API key:")
            print("  1. Open http://167.86.116.51:5678")
            print("  2. Click your profile (top right)")
            print("  3. Settings → API → Create API Key")
            print()
            print("Usage:")
            print(f"  python3 {sys.argv[0]} n8n_api_xxxxxxxx")
            print()
            print("Or set environment variable:")
            print("  export N8N_API_KEY=n8n_api_xxxxxxxx")
            print()
            sys.exit(1)

    # Import workflows
    print(f"📦 Importing {len(WORKFLOWS)} workflows...")
    print()

    imported = 0
    failed = 0

    for file, name in WORKFLOWS:
        filepath = WORKFLOWS_DIR / file

        if not filepath.exists():
            print(f"⚠️  Skipping {name} - file not found")
            failed += 1
            continue

        print(f"⬆️  Importing: {name}")
        success, message = import_workflow(api_key, filepath, name)

        if success:
            print(f"   ✅ {message}")
            imported += 1
        else:
            print(f"   ❌ {message}")
            failed += 1

    print()
    print("=" * 60)
    print("📊 Import Summary")
    print("=" * 60)
    print(f"  ✅ Imported: {imported}")
    print(f"  ❌ Failed: {failed}")
    print()

    if failed == 0:
        print("🎉 All workflows imported!")
        print()
        print("Next steps:")
        print(f"  1. Go to {N8N_HOST}/workflows")
        print("  2. Activate each workflow (toggle switch)")
        print("  3. Configure credentials in Settings → Credentials")
    else:
        print("⚠️  Some workflows failed. Check errors above.")

    print()

if __name__ == "__main__":
    main()
