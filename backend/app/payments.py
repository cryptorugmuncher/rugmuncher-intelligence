"""
RMI Payment Service
===================
Coinbase Commerce integration for crypto payments.
Supports: ETH, USDC, SOL, BTC, CRM token

Environment:
    COINBASE_COMMERCE_API_KEY - Coinbase Commerce API key
    COINBASE_COMMERCE_WEBHOOK_SECRET - Webhook secret for verification
    FRONTEND_URL - Base URL for redirects
"""
import os
import json
import hmac
import hashlib
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx

COMMERCE_API_KEY = os.getenv("COINBASE_COMMERCE_API_KEY", "")
COMMERCE_WEBHOOK_SECRET = os.getenv("COINBASE_COMMERCE_WEBHOOK_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://app.rugmunch.io")

# Product catalog
PRODUCTS = {
    "rehab-class": {
        "name": "Rug Pull Rehab - Class Session",
        "description": "2-hour live session with certified instructor. Honeypot detection, contract reading, or whale tracking.",
        "amount": "100.00",
        "currency": "USD",
        "image_url": f"{FRONTEND_URL}/assets/rehab-class.png",
        "metadata_keys": ["user_id", "class_type", "date", "timezone"],
    },
    "rehab-bundle-3": {
        "name": "Rug Pull Rehab - 3 Class Bundle",
        "description": "Save $50. Three 2-hour live sessions of your choice.",
        "amount": "250.00",
        "currency": "USD",
        "image_url": f"{FRONTEND_URL}/assets/rehab-bundle.png",
        "metadata_keys": ["user_id", "class_types"],
    },
    "newsletter-daily": {
        "name": "The Daily Munch - Newsletter",
        "description": "Daily market briefing with rug alerts, whale moves, and meme momentum.",
        "amount": "5.00",
        "currency": "USD",
        "image_url": f"{FRONTEND_URL}/assets/newsletter.png",
        "metadata_keys": ["user_id", "email", "tier"],
    },
    "newsletter-quarterly": {
        "name": "The Daily Munch - Quarterly",
        "description": "3 months of daily briefings. Save 20%.",
        "amount": "36.00",
        "currency": "USD",
        "image_url": f"{FRONTEND_URL}/assets/newsletter.png",
        "metadata_keys": ["user_id", "email", "tier"],
    },
    "tier-basic": {
        "name": "RMI Basic - Scout Tier",
        "description": "25 scans/day, 3 blockchains, The Trenches access, Telegram DM alerts.",
        "amount": "29.00",
        "currency": "USD",
        "image_url": f"{FRONTEND_URL}/assets/tier-basic.png",
        "metadata_keys": ["user_id", "tier"],
    },
    "tier-pro": {
        "name": "RMI Pro - Operative Tier",
        "description": "Unlimited scans, Muncher Maps, sniper tracking, Daily Rundown, Meme Radar.",
        "amount": "99.00",
        "currency": "USD",
        "image_url": f"{FRONTEND_URL}/assets/tier-pro.png",
        "metadata_keys": ["user_id", "tier"],
    },
    "tier-elite": {
        "name": "RMI Elite - Syndicate Tier",
        "description": "Everything in Pro + 3D Muncher Maps, whale intelligence, smart money flows, Butcher's Block.",
        "amount": "299.00",
        "currency": "USD",
        "image_url": f"{FRONTEND_URL}/assets/tier-elite.png",
        "metadata_keys": ["user_id", "tier"],
    },
}

class PaymentService:
    def __init__(self):
        self.api_key = COMMERCE_API_KEY
        self.webhook_secret = COMMERCE_WEBHOOK_SECRET
        self.base_url = "https://api.commerce.coinbase.com"
        self.demo_mode = not bool(self.api_key)
        self.demo_charges: Dict[str, Any] = {}

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-CC-Api-Key": self.api_key,
            "X-CC-Version": "2018-03-22",
        }

    async def create_charge(
        self,
        product_id: str,
        metadata: Dict[str, Any],
        redirect_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Coinbase Commerce charge."""
        product = PRODUCTS.get(product_id)
        if not product:
            return {"error": "Product not found", "status": 404}

        if self.demo_mode:
            charge_id = f"demo_charge_{product_id}_{datetime.utcnow().timestamp()}"
            charge = {
                "id": charge_id,
                "code": charge_id.replace("_", "-"),
                "status": "new",
                "hosted_url": f"{FRONTEND_URL}/checkout/demo?charge={charge_id}",
                "product_id": product_id,
                "metadata": metadata,
                "pricing": {
                    "local": {"amount": product["amount"], "currency": product["currency"]},
                },
                "created_at": datetime.utcnow().isoformat(),
                "demo": True,
            }
            self.demo_charges[charge_id] = charge
            return {"data": charge, "status": 200}

        payload = {
            "name": product["name"],
            "description": product["description"],
            "pricing_type": "fixed_price",
            "local_price": {
                "amount": product["amount"],
                "currency": product["currency"],
            },
            "metadata": {k: str(v) for k, v in metadata.items() if k in product.get("metadata_keys", [])},
            "redirect_url": redirect_url or f"{FRONTEND_URL}/payment/success",
            "cancel_url": cancel_url or f"{FRONTEND_URL}/payment/cancel",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/charges",
                headers=self._headers(),
                json=payload,
            )
            if resp.status_code >= 400:
                return {"error": resp.text, "status": resp.status_code}
            return {"data": resp.json()["data"], "status": 200}

    async def get_charge(self, charge_id: str) -> Dict[str, Any]:
        """Get charge status."""
        if self.demo_mode:
            charge = self.demo_charges.get(charge_id)
            if not charge:
                return {"error": "Charge not found", "status": 404}
            return {"data": charge, "status": 200}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.base_url}/charges/{charge_id}",
                headers=self._headers(),
            )
            if resp.status_code >= 400:
                return {"error": resp.text, "status": resp.status_code}
            return {"data": resp.json()["data"], "status": 200}

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify Coinbase Commerce webhook signature."""
        if not self.webhook_secret:
            return True  # Demo mode
        try:
            expected = hmac.new(
                self.webhook_secret.encode(),
                payload,
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(expected, signature)
        except Exception:
            return False

    def handle_webhook(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook event. Returns action to take."""
        event_type = event.get("type", "")
        data = event.get("data", {})
        metadata = data.get("metadata", {})

        if event_type in ("charges:confirmed", "charges:resolved"):
            return {
                "action": "fulfill",
                "product_id": metadata.get("product_id"),
                "user_id": metadata.get("user_id"),
                "metadata": metadata,
                "charge_id": data.get("id"),
            }

        if event_type == "charges:failed":
            return {
                "action": "fail",
                "charge_id": data.get("id"),
                "metadata": metadata,
            }

        return {"action": "ignore", "event_type": event_type}


# Singleton
payment_service = PaymentService()


def get_product_catalog() -> List[Dict[str, Any]]:
    """Return product catalog for frontend display."""
    return [
        {
            "id": k,
            "name": v["name"],
            "description": v["description"],
            "amount": v["amount"],
            "currency": v["currency"],
            "category": k.split("-")[0],
        }
        for k, v in PRODUCTS.items()
    ]
