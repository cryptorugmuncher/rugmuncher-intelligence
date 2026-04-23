#!/usr/bin/env python3
"""
Fee Collector Monitoring Setup
==============================
Set up real-time monitoring for the GVC9Zvh3 fee collector wallet.
Uses Helius webhooks to alert on any outgoing transactions.

Usage:
    python setup_fee_collector_monitoring.py --api-key YOUR_KEY --webhook-url YOUR_URL
    python setup_fee_collector_monitoring.py --test  # Test the webhook
"""

import argparse
import json
import requests
import sys
from datetime import datetime

# Fee collector to monitor
FEE_COLLECTOR = "GVC9Zvh3"

# Known bridge contracts for detection
BRIDGE_CONTRACTS = [
    "wormDTUJ6AWPNvk59vGQbDvGJmqbDTdgWgAqcLBCgUb",  # Wormhole
    "BrdgN2RPzEMjSngpWPRr6zRvobgsADWXZLg7R9LLMQe",  # Allbridge
    # Add more as identified
]

# Known CEX hot wallets (populate from database)
CEX_WALLETS = []


class FeeCollectorMonitor:
    """Monitor the fee collector wallet for outgoing transactions."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.helius.xyz/v0"
    
    def create_webhook(self, webhook_url: str) -> Dict:
        """
        Create a Helius webhook for fee collector monitoring.
        
        Args:
            webhook_url: Your server URL to receive webhook events
            
        Returns:
            Webhook configuration response
        """
        url = f"{self.base_url}/webhooks"
        
        payload = {
            "webhookURL": webhook_url,
            "accountAddresses": [FEE_COLLECTOR],
            "transactionTypes": [
                "TRANSFER",
                "SWAP",
                "UNKNOWN"  # Catch bridge transactions
            ],
            "webhookType": "enhanced",
            "authHeader": "Authorization"  # Optional: add your own auth
        }
        
        try:
            response = requests.post(
                url,
                params={"api-key": self.api_key},
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating webhook: {e}")
            return {"error": str(e)}
    
    def list_webhooks(self) -> List[Dict]:
        """List all existing webhooks."""
        url = f"{self.base_url}/webhooks"
        
        try:
            response = requests.get(
                url,
                params={"api-key": self.api_key},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error listing webhooks: {e}")
            return []
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook by ID."""
        url = f"{self.base_url}/webhooks/{webhook_id}"
        
        try:
            response = requests.delete(
                url,
                params={"api-key": self.api_key},
                timeout=30
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting webhook: {e}")
            return False
    
    def get_current_balance(self) -> Dict:
        """Get current SOL balance of fee collector."""
        url = f"{self.base_url}/addresses/{FEE_COLLECTOR}/balances"
        
        try:
            response = requests.get(
                url,
                params={"api-key": self.api_key},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            native_balance = data.get("nativeBalance", 0) / 1e9  # Convert lamports to SOL
            tokens = data.get("tokens", [])
            
            # Look for CRM token
            crm_balance = 0
            for token in tokens:
                if "CRM" in token.get("mint", ""):  # Update with actual CRM mint
                    crm_balance = token.get("amount", 0)
            
            return {
                "sol_balance": native_balance,
                "sol_value_usd": native_balance * 128,  # Approximate SOL price
                "crm_balance": crm_balance,
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.RequestException as e:
            print(f"Error getting balance: {e}")
            return {"error": str(e)}
    
    def analyze_recent_transactions(self, hours: int = 24) -> Dict:
        """Analyze recent transactions for suspicious patterns."""
        url = f"{self.base_url}/addresses/{FEE_COLLECTOR}/transactions"
        
        try:
            response = requests.get(
                url,
                params={
                    "api-key": self.api_key,
                    "limit": 50
                },
                timeout=30
            )
            response.raise_for_status()
            transactions = response.json()
            
            analysis = {
                "total_transactions": len(transactions),
                "outgoing_transfers": [],
                "incoming_transfers": [],
                "suspicious_activity": [],
                "bridge_interactions": [],
                "cex_interactions": []
            }
            
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            
            for tx in transactions:
                timestamp = tx.get("timestamp", 0)
                if timestamp < cutoff_time:
                    continue
                
                tx_hash = tx.get("signature", "UNKNOWN")
                
                # Check for native transfers
                if "nativeTransfers" in tx:
                    for transfer in tx["nativeTransfers"]:
                        if transfer.get("fromUserAccount") == FEE_COLLECTOR:
                            # Outgoing transfer
                            amount = transfer.get("amount", 0) / 1e9
                            to_address = transfer.get("toUserAccount", "UNKNOWN")
                            
                            transfer_info = {
                                "tx_hash": tx_hash,
                                "timestamp": timestamp,
                                "amount_sol": amount,
                                "to": to_address,
                                "date": datetime.fromtimestamp(timestamp).isoformat()
                            }
                            
                            analysis["outgoing_transfers"].append(transfer_info)
                            
                            # Check if recipient is a bridge
                            if any(bridge in to_address for bridge in BRIDGE_CONTRACTS):
                                transfer_info["alert_type"] = "BRIDGE_INTERACTION"
                                analysis["bridge_interactions"].append(transfer_info)
                                analysis["suspicious_activity"].append(transfer_info)
                            
                            # Check if recipient is a CEX
                            if any(cex in to_address for cex in CEX_WALLETS):
                                transfer_info["alert_type"] = "CEX_DEPOSIT"
                                analysis["cex_interactions"].append(transfer_info)
                                analysis["suspicious_activity"].append(transfer_info)
                            
                            # Large transfer alert
                            if amount > 10:  # > 10 SOL
                                transfer_info["alert_type"] = "LARGE_TRANSFER"
                                analysis["suspicious_activity"].append(transfer_info)
                        
                        elif transfer.get("toUserAccount") == FEE_COLLECTOR:
                            # Incoming transfer
                            amount = transfer.get("amount", 0) / 1e9
                            from_address = transfer.get("fromUserAccount", "UNKNOWN")
                            
                            analysis["incoming_transfers"].append({
                                "tx_hash": tx_hash,
                                "timestamp": timestamp,
                                "amount_sol": amount,
                                "from": from_address,
                                "date": datetime.fromtimestamp(timestamp).isoformat()
                            })
            
            return analysis
            
        except requests.exceptions.RequestException as e:
            print(f"Error analyzing transactions: {e}")
            return {"error": str(e)}


def generate_webhook_handler_template():
    """Generate a webhook handler server template."""
    template = '''#!/usr/bin/env python3
"""
Webhook Handler for Fee Collector Monitoring
============================================
Receive and process Helius webhook events for GVC9Zvh3

Usage:
    python webhook_handler.py
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

FEE_COLLECTOR = "GVC9Zvh3"
ALERT_THRESHOLD_SOL = 1.0  # Alert on transfers > 1 SOL

# Bridge contracts for detection
BRIDGE_CONTRACTS = [
    "wormDTUJ6AWPNvk59vGQbDvGJmqbDTdgWgAqcLBCgUb",
    "BrdgN2RPzEMjSngpWPRr6zRvobgsADWXZLg7R9LLMQe",
]

# CEX wallets (populate from database)
CEX_WALLETS = []


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle incoming webhook events."""
    data = request.json
    
    # Log all events
    timestamp = datetime.now().isoformat()
    print(f"\\n[{timestamp}] Received webhook event")
    
    # Process each transaction
    for tx in data:
        process_transaction(tx)
    
    return jsonify({"status": "ok"}), 200


def process_transaction(tx):
    """Process a single transaction."""
    tx_hash = tx.get("signature", "UNKNOWN")
    timestamp = tx.get("timestamp", 0)
    date_str = datetime.fromtimestamp(timestamp).isoformat() if timestamp else "UNKNOWN"
    
    print(f"\\nTransaction: {tx_hash}")
    print(f"Time: {date_str}")
    
    # Check for native transfers
    if "nativeTransfers" in tx:
        for transfer in tx["nativeTransfers"]:
            if transfer.get("fromUserAccount") == FEE_COLLECTOR:
                amount = transfer.get("amount", 0) / 1e9
                to_address = transfer.get("toUserAccount", "UNKNOWN")
                
                print(f"  OUTGOING: {amount:.4f} SOL to {to_address}")
                
                # Check for alerts
                if amount >= ALERT_THRESHOLD_SOL:
                    alert = f"🚨 LARGE TRANSFER: {amount:.4f} SOL from fee collector!"
                    print(f"  ALERT: {alert}")
                    save_alert(alert, tx)
                
                if any(bridge in to_address for bridge in BRIDGE_CONTRACTS):
                    alert = f"🚨 BRIDGE INTERACTION: Fee collector bridging {amount:.4f} SOL!"
                    print(f"  ALERT: {alert}")
                    save_alert(alert, tx)
                
                if any(cex in to_address for cex in CEX_WALLETS):
                    alert = f"🚨 CEX DEPOSIT: Fee collector deposited {amount:.4f} SOL to exchange!"
                    print(f"  ALERT: {alert}")
                    save_alert(alert, tx)


def save_alert(alert_msg, tx_data):
    """Save alert to file for later review."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ALERT_{timestamp}.json"
    
    alert_data = {
        "timestamp": datetime.now().isoformat(),
        "alert": alert_msg,
        "transaction": tx_data
    }
    
    with open(filename, "w") as f:
        json.dump(alert_data, f, indent=2)
    
    print(f"  Saved alert to: {filename}")


if __name__ == '__main__':
    print("Starting webhook handler...")
    print("Listening on http://0.0.0.0:5000/webhook")
    print("\\nConfigure Helius webhook to point to your server URL")
    app.run(host='0.0.0.0', port=5000)
'''
    
    with open("webhook_handler.py", "w") as f:
        f.write(template)
    
    print("Generated webhook_handler.py")
    print("Install Flask: pip install flask")
    print("Run: python webhook_handler.py")


def main():
    parser = argparse.ArgumentParser(
        description="Set up monitoring for the fee collector wallet"
    )
    parser.add_argument(
        "--api-key",
        required=True,
        help="Helius API key"
    )
    parser.add_argument(
        "--webhook-url",
        help="Your server URL to receive webhook events"
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="Create a new webhook"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing webhooks"
    )
    parser.add_argument(
        "--delete",
        help="Delete webhook by ID"
    )
    parser.add_argument(
        "--balance",
        action="store_true",
        help="Get current balance"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze recent transactions"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Hours to analyze (default: 24)"
    )
    parser.add_argument(
        "--generate-handler",
        action="store_true",
        help="Generate webhook handler template"
    )
    
    args = parser.parse_args()
    
    monitor = FeeCollectorMonitor(args.api_key)
    
    if args.generate_handler:
        generate_webhook_handler_template()
        return
    
    if args.create:
        if not args.webhook_url:
            print("Error: --webhook-url required for --create")
            sys.exit(1)
        
        print(f"Creating webhook for {FEE_COLLECTOR}...")
        result = monitor.create_webhook(args.webhook_url)
        print(json.dumps(result, indent=2))
    
    elif args.list:
        print("Listing existing webhooks...")
        webhooks = monitor.list_webhooks()
        for webhook in webhooks:
            print(f"\\nWebhook ID: {webhook.get('webhookID', 'N/A')}")
            print(f"URL: {webhook.get('webhookURL', 'N/A')}")
            print(f"Addresses: {webhook.get('accountAddresses', [])}")
    
    elif args.delete:
        print(f"Deleting webhook {args.delete}...")
        if monitor.delete_webhook(args.delete):
            print("Deleted successfully")
        else:
            print("Failed to delete")
    
    elif args.balance:
        print(f"Getting current balance for {FEE_COLLECTOR}...")
        balance = monitor.get_current_balance()
        print(json.dumps(balance, indent=2))
    
    elif args.analyze:
        print(f"Analyzing transactions for the last {args.hours} hours...")
        analysis = monitor.analyze_recent_transactions(args.hours)
        
        print(f"\\n{'='*60}")
        print("ANALYSIS RESULTS")
        print(f"{'='*60}")
        print(f"Total Transactions: {analysis.get('total_transactions', 0)}")
        print(f"Outgoing Transfers: {len(analysis.get('outgoing_transfers', []))}")
        print(f"Incoming Transfers: {len(analysis.get('incoming_transfers', []))}")
        print(f"Suspicious Activity: {len(analysis.get('suspicious_activity', []))}")
        print(f"Bridge Interactions: {len(analysis.get('bridge_interactions', []))}")
        print(f"CEX Interactions: {len(analysis.get('cex_interactions', []))}")
        
        if analysis.get('suspicious_activity'):
            print(f"\\n🚨 ALERTS:")
            for alert in analysis['suspicious_activity']:
                print(f"  - {alert.get('alert_type', 'UNKNOWN')}: {alert.get('amount_sol', 0):.4f} SOL")
                print(f"    To: {alert.get('to', 'UNKNOWN')}")
                print(f"    Tx: {alert.get('tx_hash', 'UNKNOWN')}")
        
        print(f"{'='*60}")
    
    else:
        parser.print_help()
        print("\\nQuick start:")
        print("  1. Generate handler: python setup_fee_collector_monitoring.py --generate-handler")
        print("  2. Start handler: python webhook_handler.py")
        print("  3. Create webhook: python setup_fee_collector_monitoring.py --create --webhook-url YOUR_URL")
        print("  4. Check balance: python setup_fee_collector_monitoring.py --balance")


if __name__ == "__main__":
    main()
