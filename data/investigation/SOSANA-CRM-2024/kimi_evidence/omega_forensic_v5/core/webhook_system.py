"""
RMI Webhook System
==================
Real-time webhook notifications for events and alerts.
"""

import asyncio
import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import aiohttp


class WebhookEvent(Enum):
    """Types of webhook events."""
    # Investigation events
    INVESTIGATION_CREATED = "investigation.created"
    INVESTIGATION_UPDATED = "investigation.updated"
    INVESTIGATION_COMPLETED = "investigation.completed"
    
    # Wallet events
    WALLET_ANALYSIS_COMPLETE = "wallet.analysis.complete"
    WALLET_RISK_CHANGE = "wallet.risk.change"
    WALLET_TRANSACTION_DETECTED = "wallet.transaction.detected"
    
    # Token events
    TOKEN_SCAN_COMPLETE = "token.scan.complete"
    TOKEN_RISK_CHANGE = "token.risk.change"
    TOKEN_LIQUIDITY_CHANGE = "token.liquidity.change"
    
    # Cluster events
    CLUSTER_DETECTED = "cluster.detected"
    CLUSTER_UPDATED = "cluster.updated"
    
    # KOL events
    KOL_CALL_DETECTED = "kol.call.detected"
    KOL_POSITION_CHANGE = "kol.position.change"
    
    # Alert events
    SECURITY_ALERT = "security.alert"
    SCAM_DETECTED = "scam.detected"
    
    # News events
    NEWS_PUBLISHED = "news.published"
    
    # Portfolio events
    PORTFOLIO_ALERT = "portfolio.alert"
    PRICE_ALERT = "price.alert"


@dataclass
class WebhookSubscription:
    """Webhook subscription."""
    id: str
    user_id: str
    
    # Endpoint
    url: str
    secret: str  # For HMAC signature
    
    # Events
    events: List[WebhookEvent]
    
    # Filters
    filters: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Stats
    success_count: int = 0
    failure_count: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    last_error: Optional[str] = None


@dataclass
class WebhookDelivery:
    """Webhook delivery attempt."""
    id: str
    subscription_id: str
    event_type: WebhookEvent
    
    payload: Dict[str, Any]
    
    # Delivery
    attempted_at: datetime = field(default_factory=datetime.utcnow)
    success: bool = False
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    
    # Retry
    retry_count: int = 0
    next_retry_at: Optional[datetime] = None


class WebhookManager:
    """
    Manages webhook subscriptions and deliveries.
    """
    
    MAX_RETRIES = 5
    RETRY_DELAYS = [1, 5, 15, 60, 300]  # seconds
    
    def __init__(self):
        self.subscriptions: Dict[str, WebhookSubscription] = {}
        self.deliveries: List[WebhookDelivery] = []
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def create_subscription(
        self,
        user_id: str,
        url: str,
        events: List[str],
        filters: Dict = None
    ) -> Dict:
        """Create new webhook subscription."""
        # Validate URL
        if not url.startswith("https://"):
            return {"error": "URL must use HTTPS"}
        
        # Validate events
        valid_events = []
        for event_str in events:
            try:
                event = WebhookEvent(event_str)
                valid_events.append(event)
            except ValueError:
                return {"error": f"Invalid event type: {event_str}"}
        
        # Generate subscription ID and secret
        subscription_id = hashlib.sha256(
            f"{user_id}:{url}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        secret = hashlib.sha256(
            f"{subscription_id}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()
        
        subscription = WebhookSubscription(
            id=subscription_id,
            user_id=user_id,
            url=url,
            secret=secret,
            events=valid_events,
            filters=filters or {}
        )
        
        self.subscriptions[subscription_id] = subscription
        
        return {
            "subscription_id": subscription_id,
            "secret": secret,
            "url": url,
            "events": [e.value for e in valid_events],
            "message": "Subscription created. Save the secret - it won't be shown again."
        }
    
    async def update_subscription(
        self,
        subscription_id: str,
        events: List[str] = None,
        filters: Dict = None,
        is_active: bool = None
    ) -> Dict:
        """Update webhook subscription."""
        subscription = self.subscriptions.get(subscription_id)
        if not subscription:
            return {"error": "Subscription not found"}
        
        if events:
            valid_events = []
            for event_str in events:
                try:
                    event = WebhookEvent(event_str)
                    valid_events.append(event)
                except ValueError:
                    return {"error": f"Invalid event type: {event_str}"}
            subscription.events = valid_events
        
        if filters:
            subscription.filters = filters
        
        if is_active is not None:
            subscription.is_active = is_active
        
        return {
            "subscription_id": subscription_id,
            "events": [e.value for e in subscription.events],
            "is_active": subscription.is_active
        }
    
    async def delete_subscription(self, subscription_id: str) -> Dict:
        """Delete webhook subscription."""
        if subscription_id not in self.subscriptions:
            return {"error": "Subscription not found"}
        
        del self.subscriptions[subscription_id]
        
        return {"success": True, "message": "Subscription deleted"}
    
    async def get_subscriptions(self, user_id: str) -> List[Dict]:
        """Get all subscriptions for user."""
        user_subs = [
            sub for sub in self.subscriptions.values()
            if sub.user_id == user_id
        ]
        
        return [
            {
                "id": sub.id,
                "url": sub.url,
                "events": [e.value for e in sub.events],
                "is_active": sub.is_active,
                "created_at": sub.created_at.isoformat(),
                "stats": {
                    "success_count": sub.success_count,
                    "failure_count": sub.failure_count,
                    "last_success": sub.last_success.isoformat() if sub.last_success else None,
                    "last_failure": sub.last_failure.isoformat() if sub.last_failure else None
                }
            }
            for sub in user_subs
        ]
    
    async def trigger_event(
        self,
        event_type: WebhookEvent,
        payload: Dict[str, Any],
        filters: Dict = None
    ) -> Dict:
        """Trigger webhook event to all matching subscriptions."""
        # Find matching subscriptions
        matching = []
        for sub in self.subscriptions.values():
            if not sub.is_active:
                continue
            
            if event_type not in sub.events:
                continue
            
            # Check filters
            if sub.filters and filters:
                match = True
                for key, value in sub.filters.items():
                    if filters.get(key) != value:
                        match = False
                        break
                if not match:
                    continue
            
            matching.append(sub)
        
        # Deliver to all matching subscriptions
        deliveries = []
        for sub in matching:
            delivery = await self._deliver(sub, event_type, payload)
            deliveries.append(delivery)
        
        successful = len([d for d in deliveries if d.success])
        
        return {
            "event": event_type.value,
            "subscriptions_notified": len(matching),
            "successful_deliveries": successful,
            "failed_deliveries": len(matching) - successful,
            "deliveries": [
                {
                    "subscription_id": d.subscription_id,
                    "success": d.success,
                    "status": d.response_status
                }
                for d in deliveries
            ]
        }
    
    async def _deliver(
        self,
        subscription: WebhookSubscription,
        event_type: WebhookEvent,
        payload: Dict
    ) -> WebhookDelivery:
        """Deliver webhook to subscription."""
        delivery_id = hashlib.sha256(
            f"{subscription.id}:{event_type.value}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # Build payload
        webhook_payload = {
            "event": event_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "data": payload
        }
        
        # Generate signature
        signature = self._generate_signature(
            subscription.secret,
            json.dumps(webhook_payload, separators=(',', ':'))
        )
        
        delivery = WebhookDelivery(
            id=delivery_id,
            subscription_id=subscription.id,
            event_type=event_type,
            payload=webhook_payload
        )
        
        try:
            session = await self._get_session()
            
            async with session.post(
                subscription.url,
                json=webhook_payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature,
                    "X-Webhook-Event": event_type.value,
                    "X-Webhook-ID": delivery_id,
                    "User-Agent": "RMI-Webhook/1.0"
                }
            ) as response:
                delivery.response_status = response.status
                delivery.response_body = await response.text()
                
                if response.status < 400:
                    delivery.success = True
                    subscription.success_count += 1
                    subscription.last_success = datetime.utcnow()
                else:
                    delivery.success = False
                    delivery.error_message = f"HTTP {response.status}"
                    subscription.failure_count += 1
                    subscription.last_failure = datetime.utcnow()
                    subscription.last_error = delivery.error_message
                    
        except Exception as e:
            delivery.success = False
            delivery.error_message = str(e)
            subscription.failure_count += 1
            subscription.last_failure = datetime.utcnow()
            subscription.last_error = str(e)
        
        self.deliveries.append(delivery)
        
        # Schedule retry if failed
        if not delivery.success and delivery.retry_count < self.MAX_RETRIES:
            delay = self.RETRY_DELAYS[min(delivery.retry_count, len(self.RETRY_DELAYS) - 1)]
            delivery.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)
        
        return delivery
    
    def _generate_signature(self, secret: str, payload: str) -> str:
        """Generate HMAC signature for webhook."""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def verify_signature(
        self,
        secret: str,
        payload: str,
        signature: str
    ) -> bool:
        """Verify webhook signature."""
        expected = self._generate_signature(secret, payload)
        return hmac.compare_digest(expected, signature)
    
    async def get_delivery_log(
        self,
        subscription_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get webhook delivery log."""
        deliveries = self.deliveries
        
        if subscription_id:
            deliveries = [d for d in deliveries if d.subscription_id == subscription_id]
        
        deliveries = sorted(deliveries, key=lambda x: x.attempted_at, reverse=True)[:limit]
        
        return [
            {
                "id": d.id,
                "subscription_id": d.subscription_id,
                "event": d.event_type.value,
                "success": d.success,
                "status": d.response_status,
                "attempted_at": d.attempted_at.isoformat(),
                "retry_count": d.retry_count,
                "error": d.error_message
            }
            for d in deliveries
        ]
    
    async def retry_failed(self, subscription_id: Optional[str] = None) -> Dict:
        """Retry failed deliveries."""
        failed = [
            d for d in self.deliveries
            if not d.success
            and d.retry_count < self.MAX_RETRIES
            and (subscription_id is None or d.subscription_id == subscription_id)
        ]
        
        retried = 0
        for delivery in failed:
            if delivery.next_retry_at and delivery.next_retry_at <= datetime.utcnow():
                subscription = self.subscriptions.get(delivery.subscription_id)
                if subscription:
                    delivery.retry_count += 1
                    await self._deliver(subscription, delivery.event_type, delivery.payload["data"])
                    retried += 1
        
        return {"retried": retried, "remaining": len(failed) - retried}


class AlertWebhookBuilder:
    """
    Builder for common webhook alert payloads.
    """
    
    @staticmethod
    def wallet_risk_change(
        wallet_address: str,
        old_risk: int,
        new_risk: int,
        reasons: List[str]
    ) -> Dict:
        """Build wallet risk change payload."""
        return {
            "wallet_address": wallet_address,
            "old_risk_score": old_risk,
            "new_risk_score": new_risk,
            "risk_change": new_risk - old_risk,
            "new_risk_level": "high" if new_risk >= 60 else "medium" if new_risk >= 40 else "low",
            "reasons": reasons,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def token_scan_complete(
        token_address: str,
        token_symbol: str,
        risk_score: int,
        red_flags: List[str]
    ) -> Dict:
        """Build token scan complete payload."""
        return {
            "token_address": token_address,
            "token_symbol": token_symbol,
            "risk_score": risk_score,
            "risk_level": "high" if risk_score >= 60 else "medium" if risk_score >= 40 else "low",
            "red_flags": red_flags,
            "scan_url": f"https://intel.cryptorugmunch.com/scan/{token_address}",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def kol_call_detected(
        kol_handle: str,
        token_address: str,
        token_symbol: str,
        call_type: str,
        price_at_call: float
    ) -> Dict:
        """Build KOL call detected payload."""
        return {
            "kol_handle": kol_handle,
            "token_address": token_address,
            "token_symbol": token_symbol,
            "call_type": call_type,
            "price_at_call": price_at_call,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def security_alert(
        alert_type: str,
        severity: str,
        title: str,
        description: str,
        affected_tokens: List[str] = None
    ) -> Dict:
        """Build security alert payload."""
        return {
            "alert_type": alert_type,
            "severity": severity,
            "title": title,
            "description": description,
            "affected_tokens": affected_tokens or [],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def portfolio_alert(
        portfolio_id: str,
        alert_type: str,
        level: str,
        title: str,
        message: str,
        affected_token: str = None
    ) -> Dict:
        """Build portfolio alert payload."""
        return {
            "portfolio_id": portfolio_id,
            "alert_type": alert_type,
            "level": level,
            "title": title,
            "message": message,
            "affected_token": affected_token,
            "timestamp": datetime.utcnow().isoformat()
        }


# ============== FASTAPI ENDPOINTS ==============

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

# Global instance
webhook_manager = WebhookManager()


class CreateSubscriptionRequest(BaseModel):
    url: str
    events: List[str]
    filters: Optional[Dict] = None


class UpdateSubscriptionRequest(BaseModel):
    events: Optional[List[str]] = None
    filters: Optional[Dict] = None
    is_active: Optional[bool] = None


@router.post("/subscriptions")
async def create_subscription(
    request: CreateSubscriptionRequest,
    user_id: str  # Would come from auth
):
    """Create webhook subscription."""
    result = await webhook_manager.create_subscription(
        user_id,
        request.url,
        request.events,
        request.filters
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/subscriptions")
async def get_subscriptions(user_id: str):
    """Get user subscriptions."""
    return await webhook_manager.get_subscriptions(user_id)


@router.patch("/subscriptions/{subscription_id}")
async def update_subscription(
    subscription_id: str,
    request: UpdateSubscriptionRequest
):
    """Update subscription."""
    result = await webhook_manager.update_subscription(
        subscription_id,
        request.events,
        request.filters,
        request.is_active
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.delete("/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: str):
    """Delete subscription."""
    result = await webhook_manager.delete_subscription(subscription_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/deliveries")
async def get_delivery_log(
    subscription_id: Optional[str] = None,
    limit: int = 100
):
    """Get delivery log."""
    return await webhook_manager.get_delivery_log(subscription_id, limit)


@router.post("/retry-failed")
async def retry_failed(subscription_id: Optional[str] = None):
    """Retry failed deliveries."""
    return await webhook_manager.retry_failed(subscription_id)


@router.get("/events")
async def get_event_types():
    """Get available webhook event types."""
    return {
        "events": [
            {
                "value": e.value,
                "category": e.value.split(".")[0],
                "description": e.name.replace("_", " ").title()
            }
            for e in WebhookEvent
        ]
    }


@router.post("/test")
async def test_webhook(
    url: str,
    event: str,
    secret: str
):
    """Test webhook endpoint."""
    try:
        event_type = WebhookEvent(event)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid event type")
    
    # Build test payload
    payload = {
        "event": event_type.value,
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "message": "This is a test webhook from RMI",
            "test": True
        }
    }
    
    # Generate signature
    signature = webhook_manager._generate_signature(
        secret,
        json.dumps(payload, separators=(',', ':'))
    )
    
    # Send test webhook
    try:
        session = await webhook_manager._get_session()
        async with session.post(
            url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-Webhook-Signature": signature,
                "X-Webhook-Event": event_type.value,
                "X-Webhook-ID": "test_123",
                "User-Agent": "RMI-Webhook/1.0"
            }
        ) as response:
            return {
                "success": response.status < 400,
                "status": response.status,
                "response": await response.text()
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
