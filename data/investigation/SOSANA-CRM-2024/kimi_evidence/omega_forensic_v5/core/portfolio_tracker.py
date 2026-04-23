"""
RMI Portfolio Tracker with Risk Alerts
======================================
Track user portfolios with automatic risk scoring and alerts.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class RiskAlertLevel(Enum):
    """Risk alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class PortfolioToken:
    """Token in portfolio."""
    token_address: str
    token_symbol: str
    token_name: str
    chain: str
    
    balance: float = 0
    price_usd: float = 0
    value_usd: float = 0
    
    # Risk
    risk_score: int = 0
    risk_level: str = "unknown"
    red_flags: List[str] = field(default_factory=list)
    
    # Performance
    price_change_24h: float = 0
    price_change_7d: float = 0
    price_change_30d: float = 0
    
    # Metadata
    added_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PortfolioAlert:
    """Portfolio risk alert."""
    id: str
    user_id: str
    portfolio_id: str
    
    alert_type: str
    level: RiskAlertLevel
    title: str
    message: str
    
    affected_token: Optional[str] = None
    affected_token_symbol: Optional[str] = None
    
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserPortfolio:
    """User's portfolio."""
    id: str
    user_id: str
    name: str
    
    tokens: List[PortfolioToken] = field(default_factory=list)
    
    total_value_usd: float = 0
    total_cost_basis: float = 0
    total_pnl: float = 0
    total_pnl_percent: float = 0
    
    # Risk
    overall_risk_score: int = 0
    overall_risk_level: str = "unknown"
    high_risk_tokens: int = 0
    
    # Settings
    alert_threshold: str = "medium"  # low, medium, high
    auto_refresh: bool = True
    refresh_interval_minutes: int = 15
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class PortfolioTracker:
    """
    Portfolio tracking with automatic risk analysis.
    """
    
    RISK_THRESHOLDS = {
        "critical": 80,
        "high": 60,
        "medium": 40,
        "low": 20
    }
    
    def __init__(self):
        self.portfolios: Dict[str, UserPortfolio] = {}
        self.alerts: Dict[str, List[PortfolioAlert]] = {}
        self.alert_history: List[PortfolioAlert] = []
    
    async def create_portfolio(self, user_id: str, name: str) -> UserPortfolio:
        """Create new portfolio."""
        portfolio_id = f"portfolio_{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        portfolio = UserPortfolio(
            id=portfolio_id,
            user_id=user_id,
            name=name
        )
        
        self.portfolios[portfolio_id] = portfolio
        
        return portfolio
    
    async def add_token(
        self,
        portfolio_id: str,
        token_address: str,
        token_symbol: str,
        token_name: str,
        chain: str,
        balance: float = 0
    ) -> Dict:
        """Add token to portfolio."""
        portfolio = self.portfolios.get(portfolio_id)
        if not portfolio:
            return {"error": "Portfolio not found"}
        
        # Check if already exists
        for token in portfolio.tokens:
            if token.token_address == token_address:
                return {"error": "Token already in portfolio"}
        
        # Get risk analysis
        risk_data = await self._analyze_token_risk(token_address, chain)
        
        token = PortfolioToken(
            token_address=token_address,
            token_symbol=token_symbol,
            token_name=token_name,
            chain=chain,
            balance=balance,
            risk_score=risk_data.get("score", 0),
            risk_level=risk_data.get("level", "unknown"),
            red_flags=risk_data.get("red_flags", [])
        )
        
        portfolio.tokens.append(token)
        
        # Recalculate portfolio
        await self._recalculate_portfolio(portfolio)
        
        # Check for alerts
        alerts = await self._check_token_alerts(portfolio, token)
        
        return {
            "success": True,
            "token": {
                "address": token.token_address,
                "symbol": token.token_symbol,
                "risk_score": token.risk_score,
                "risk_level": token.risk_level
            },
            "alerts": [a.title for a in alerts]
        }
    
    async def remove_token(self, portfolio_id: str, token_address: str) -> Dict:
        """Remove token from portfolio."""
        portfolio = self.portfolios.get(portfolio_id)
        if not portfolio:
            return {"error": "Portfolio not found"}
        
        portfolio.tokens = [t for t in portfolio.tokens if t.token_address != token_address]
        
        await self._recalculate_portfolio(portfolio)
        
        return {"success": True}
    
    async def refresh_portfolio(self, portfolio_id: str) -> Dict:
        """Refresh portfolio data."""
        portfolio = self.portfolios.get(portfolio_id)
        if not portfolio:
            return {"error": "Portfolio not found"}
        
        for token in portfolio.tokens:
            # Refresh token data
            price_data = await self._get_token_price(token.token_address, token.chain)
            token.price_usd = price_data.get("price", 0)
            token.value_usd = token.balance * token.price_usd
            token.price_change_24h = price_data.get("change_24h", 0)
            token.last_updated = datetime.utcnow()
            
            # Refresh risk data
            risk_data = await self._analyze_token_risk(token.token_address, token.chain)
            token.risk_score = risk_data.get("score", token.risk_score)
            token.risk_level = risk_data.get("level", token.risk_level)
        
        await self._recalculate_portfolio(portfolio)
        
        # Check for new alerts
        new_alerts = await self._check_portfolio_alerts(portfolio)
        
        return {
            "success": True,
            "portfolio": await self._portfolio_to_dict(portfolio),
            "new_alerts": len(new_alerts)
        }
    
    async def get_portfolio(self, portfolio_id: str) -> Optional[Dict]:
        """Get portfolio details."""
        portfolio = self.portfolios.get(portfolio_id)
        if not portfolio:
            return None
        
        return await self._portfolio_to_dict(portfolio)
    
    async def get_user_portfolios(self, user_id: str) -> List[Dict]:
        """Get all portfolios for user."""
        portfolios = [
            p for p in self.portfolios.values()
            if p.user_id == user_id
        ]
        
        return [
            await self._portfolio_to_dict(p)
            for p in portfolios
        ]
    
    async def get_alerts(
        self,
        user_id: str,
        level: Optional[str] = None,
        unacknowledged_only: bool = False
    ) -> List[Dict]:
        """Get user alerts."""
        user_alerts = self.alerts.get(user_id, [])
        
        if level:
            user_alerts = [a for a in user_alerts if a.level.value == level]
        
        if unacknowledged_only:
            user_alerts = [a for a in user_alerts if not a.acknowledged_at]
        
        return [
            {
                "id": a.id,
                "type": a.alert_type,
                "level": a.level.value,
                "title": a.title,
                "message": a.message,
                "token": a.affected_token_symbol,
                "triggered_at": a.triggered_at.isoformat(),
                "acknowledged": a.acknowledged_at is not None
            }
            for a in sorted(user_alerts, key=lambda x: x.triggered_at, reverse=True)
        ]
    
    async def acknowledge_alert(self, alert_id: str) -> Dict:
        """Acknowledge an alert."""
        for user_alerts in self.alerts.values():
            for alert in user_alerts:
                if alert.id == alert_id:
                    alert.acknowledged_at = datetime.utcnow()
                    return {"success": True}
        
        return {"error": "Alert not found"}
    
    async def _analyze_token_risk(self, token_address: str, chain: str) -> Dict:
        """Analyze token risk."""
        # In production, call contract checker
        # For now, return mock data
        return {
            "score": random.randint(10, 90),
            "level": random.choice(["low", "medium", "high"]),
            "red_flags": random.sample([
                "Mint authority not revoked",
                "High holder concentration",
                "Low liquidity",
                "No audit",
                "Anonymous team"
            ], k=random.randint(0, 3))
        }
    
    async def _get_token_price(self, token_address: str, chain: str) -> Dict:
        """Get token price data."""
        # In production, call price API
        return {
            "price": random.uniform(0.0001, 100),
            "change_24h": random.uniform(-20, 20),
            "change_7d": random.uniform(-50, 100)
        }
    
    async def _recalculate_portfolio(self, portfolio: UserPortfolio):
        """Recalculate portfolio totals."""
        portfolio.total_value_usd = sum(t.value_usd for t in portfolio.tokens)
        
        # Calculate overall risk
        if portfolio.tokens:
            avg_risk = sum(t.risk_score for t in portfolio.tokens) / len(portfolio.tokens)
            portfolio.overall_risk_score = int(avg_risk)
            portfolio.overall_risk_level = self._get_risk_level(avg_risk)
            portfolio.high_risk_tokens = len([t for t in portfolio.tokens if t.risk_level == "high"])
        
        portfolio.last_updated = datetime.utcnow()
    
    def _get_risk_level(self, score: float) -> str:
        """Get risk level from score."""
        if score >= self.RISK_THRESHOLDS["critical"]:
            return "critical"
        elif score >= self.RISK_THRESHOLDS["high"]:
            return "high"
        elif score >= self.RISK_THRESHOLDS["medium"]:
            return "medium"
        elif score >= self.RISK_THRESHOLDS["low"]:
            return "low"
        return "safe"
    
    async def _check_token_alerts(
        self,
        portfolio: UserPortfolio,
        token: PortfolioToken
    ) -> List[PortfolioAlert]:
        """Check for alerts on a token."""
        alerts = []
        
        # High risk token alert
        if token.risk_score >= 70:
            alert = PortfolioAlert(
                id=f"alert_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                user_id=portfolio.user_id,
                portfolio_id=portfolio.id,
                alert_type="high_risk_token",
                level=RiskAlertLevel.HIGH,
                title=f"High Risk Token Added: {token.token_symbol}",
                message=f"{token.token_symbol} has a risk score of {token.risk_score}/100. Review carefully before investing.",
                affected_token=token.token_address,
                affected_token_symbol=token.token_symbol
            )
            alerts.append(alert)
        
        # Red flags alert
        if token.red_flags:
            alert = PortfolioAlert(
                id=f"alert_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_flags",
                user_id=portfolio.user_id,
                portfolio_id=portfolio.id,
                alert_type="red_flags",
                level=RiskAlertLevel.MEDIUM,
                title=f"Red Flags Detected: {token.token_symbol}",
                message=f"Found {len(token.red_flags)} red flags: {', '.join(token.red_flags[:3])}",
                affected_token=token.token_address,
                affected_token_symbol=token.token_symbol,
                data={"red_flags": token.red_flags}
            )
            alerts.append(alert)
        
        # Store alerts
        if portfolio.user_id not in self.alerts:
            self.alerts[portfolio.user_id] = []
        
        self.alerts[portfolio.user_id].extend(alerts)
        self.alert_history.extend(alerts)
        
        return alerts
    
    async def _check_portfolio_alerts(self, portfolio: UserPortfolio) -> List[PortfolioAlert]:
        """Check for portfolio-wide alerts."""
        alerts = []
        
        # Portfolio concentration alert
        if portfolio.tokens:
            largest = max(portfolio.tokens, key=lambda t: t.value_usd)
            if portfolio.total_value_usd > 0:
                concentration = (largest.value_usd / portfolio.total_value_usd) * 100
                if concentration > 50:
                    alert = PortfolioAlert(
                        id=f"alert_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_concentration",
                        user_id=portfolio.user_id,
                        portfolio_id=portfolio.id,
                        alert_type="concentration_risk",
                        level=RiskAlertLevel.MEDIUM,
                        title="Portfolio Concentration Warning",
                        message=f"{largest.token_symbol} makes up {concentration:.1f}% of your portfolio. Consider diversifying.",
                        affected_token=largest.token_address,
                        affected_token_symbol=largest.token_symbol,
                        data={"concentration_percent": concentration}
                    )
                    alerts.append(alert)
        
        # High risk concentration
        high_risk_value = sum(t.value_usd for t in portfolio.tokens if t.risk_level == "high")
        if portfolio.total_value_usd > 0:
            high_risk_percent = (high_risk_value / portfolio.total_value_usd) * 100
            if high_risk_percent > 30:
                alert = PortfolioAlert(
                    id=f"alert_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_highrisk",
                    user_id=portfolio.user_id,
                    portfolio_id=portfolio.id,
                    alert_type="high_risk_concentration",
                    level=RiskAlertLevel.HIGH,
                    title="High Risk Token Concentration",
                    message=f"{high_risk_percent:.1f}% of your portfolio is in high-risk tokens. Consider reducing exposure.",
                    data={"high_risk_percent": high_risk_percent}
                )
                alerts.append(alert)
        
        # Store alerts
        if alerts:
            if portfolio.user_id not in self.alerts:
                self.alerts[portfolio.user_id] = []
            
            self.alerts[portfolio.user_id].extend(alerts)
            self.alert_history.extend(alerts)
        
        return alerts
    
    async def _portfolio_to_dict(self, portfolio: UserPortfolio) -> Dict:
        """Convert portfolio to dict."""
        return {
            "id": portfolio.id,
            "name": portfolio.name,
            "total_value_usd": round(portfolio.total_value_usd, 2),
            "total_pnl": round(portfolio.total_pnl, 2),
            "total_pnl_percent": round(portfolio.total_pnl_percent, 2),
            "overall_risk_score": portfolio.overall_risk_score,
            "overall_risk_level": portfolio.overall_risk_level,
            "high_risk_tokens": portfolio.high_risk_tokens,
            "token_count": len(portfolio.tokens),
            "tokens": [
                {
                    "address": t.token_address,
                    "symbol": t.token_symbol,
                    "name": t.token_name,
                    "chain": t.chain,
                    "balance": t.balance,
                    "price_usd": round(t.price_usd, 6),
                    "value_usd": round(t.value_usd, 2),
                    "risk_score": t.risk_score,
                    "risk_level": t.risk_level,
                    "price_change_24h": round(t.price_change_24h, 2),
                    "red_flags": t.red_flags
                }
                for t in sorted(portfolio.tokens, key=lambda x: x.value_usd, reverse=True)
            ],
            "last_updated": portfolio.last_updated.isoformat()
        }


# ============== FASTAPI ENDPOINTS ==============

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio Tracker"])

# Global instance
portfolio_tracker = PortfolioTracker()


class CreatePortfolioRequest(BaseModel):
    user_id: str
    name: str


class AddTokenRequest(BaseModel):
    token_address: str
    token_symbol: str
    token_name: str
    chain: str
    balance: float = 0


class UpdateSettingsRequest(BaseModel):
    alert_threshold: Optional[str] = None
    auto_refresh: Optional[bool] = None


@router.post("/create")
async def create_portfolio(request: CreatePortfolioRequest):
    """Create new portfolio."""
    portfolio = await portfolio_tracker.create_portfolio(request.user_id, request.name)
    return {
        "portfolio_id": portfolio.id,
        "name": portfolio.name,
        "message": "Portfolio created successfully"
    }


@router.post("/{portfolio_id}/add-token")
async def add_token(portfolio_id: str, request: AddTokenRequest):
    """Add token to portfolio."""
    result = await portfolio_tracker.add_token(
        portfolio_id,
        request.token_address,
        request.token_symbol,
        request.token_name,
        request.chain,
        request.balance
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.delete("/{portfolio_id}/token/{token_address}")
async def remove_token(portfolio_id: str, token_address: str):
    """Remove token from portfolio."""
    result = await portfolio_tracker.remove_token(portfolio_id, token_address)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/{portfolio_id}/refresh")
async def refresh_portfolio(portfolio_id: str):
    """Refresh portfolio data."""
    result = await portfolio_tracker.refresh_portfolio(portfolio_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    """Get portfolio details."""
    portfolio = await portfolio_tracker.get_portfolio(portfolio_id)
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return portfolio


@router.get("/user/{user_id}")
async def get_user_portfolios(user_id: str):
    """Get all user portfolios."""
    portfolios = await portfolio_tracker.get_user_portfolios(user_id)
    return {"portfolios": portfolios, "count": len(portfolios)}


@router.get("/alerts/{user_id}")
async def get_user_alerts(
    user_id: str,
    level: Optional[str] = None,
    unacknowledged_only: bool = False
):
    """Get user alerts."""
    alerts = await portfolio_tracker.get_alerts(user_id, level, unacknowledged_only)
    return {"alerts": alerts, "count": len(alerts)}


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge alert."""
    result = await portfolio_tracker.acknowledge_alert(alert_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result


@router.get("/alerts/{user_id}/stats")
async def get_alert_stats(user_id: str):
    """Get alert statistics."""
    alerts = await portfolio_tracker.get_alerts(user_id)
    
    by_level = {}
    for alert in alerts:
        level = alert["level"]
        by_level[level] = by_level.get(level, 0) + 1
    
    return {
        "total": len(alerts),
        "by_level": by_level,
        "unacknowledged": len([a for a in alerts if not a["acknowledged"]])
    }
