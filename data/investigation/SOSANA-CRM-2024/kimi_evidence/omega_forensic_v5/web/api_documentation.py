"""
RMI API Documentation & Developer Portal
========================================
Complete API documentation and developer resources.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


class APIVersion(Enum):
    """API versions."""
    V1 = "v1"
    V2 = "v2"


@dataclass
class APIEndpoint:
    """API endpoint documentation."""
    path: str
    method: str
    description: str
    
    # Request/Response
    parameters: List[Dict] = field(default_factory=list)
    request_body: Dict = field(default_factory=dict)
    response_schema: Dict = field(default_factory=dict)
    
    # Examples
    example_request: Dict = field(default_factory=dict)
    example_response: Dict = field(default_factory=dict)
    
    # Metadata
    authentication: str = "api_key"
    rate_limit: str = "100/minute"
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False


@dataclass
class APICategory:
    """Category of API endpoints."""
    name: str
    description: str
    endpoints: List[APIEndpoint]


class APIDocumentation:
    """
    Complete API documentation for RMI platform.
    """
    
    def __init__(self):
        self.categories: List[APICategory] = []
        self._build_documentation()
    
    def _build_documentation(self):
        """Build complete API documentation."""
        
        # Core Investigation APIs
        self.categories.append(APICategory(
            name="Investigation",
            description="Create and manage fraud investigations",
            endpoints=[
                APIEndpoint(
                    path="/api/investigations",
                    method="GET",
                    description="List all investigations for authenticated user",
                    parameters=[
                        {"name": "status", "type": "string", "required": False, "description": "Filter by status: active, completed, archived"},
                        {"name": "limit", "type": "integer", "required": False, "description": "Number of results (max 100)"},
                        {"name": "offset", "type": "integer", "required": False, "description": "Pagination offset"}
                    ],
                    response_schema={
                        "type": "object",
                        "properties": {
                            "investigations": {"type": "array"},
                            "total": {"type": "integer"},
                            "has_more": {"type": "boolean"}
                        }
                    },
                    example_response={
                        "investigations": [
                            {
                                "id": "inv_123",
                                "title": "Suspicious Token Analysis",
                                "status": "active",
                                "risk_level": "high",
                                "created_at": "2025-01-15T10:30:00Z"
                            }
                        ],
                        "total": 42,
                        "has_more": True
                    },
                    tags=["investigation", "list"]
                ),
                APIEndpoint(
                    path="/api/investigations",
                    method="POST",
                    description="Create new investigation",
                    request_body={
                        "type": "object",
                        "required": ["title"],
                        "properties": {
                            "title": {"type": "string", "description": "Investigation title"},
                            "description": {"type": "string", "description": "Optional description"},
                            "token_address": {"type": "string", "description": "Related token address"},
                            "tags": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    example_request={
                        "title": "CRM Token Investigation",
                        "description": "Investigating suspicious wallet clusters",
                        "token_address": "Eyi4JcxVkS9fWzubSu5yS7dHy4kAiFHJN6Rwu6y7r8U",
                        "tags": ["wallet-clustering", "high-priority"]
                    },
                    example_response={
                        "id": "inv_456",
                        "title": "CRM Token Investigation",
                        "status": "active",
                        "created_at": "2025-01-15T12:00:00Z",
                        "message": "Investigation created successfully"
                    },
                    tags=["investigation", "create"]
                ),
            ]
        ))
        
        # Wallet Analysis APIs
        self.categories.append(APICategory(
            name="Wallet Analysis",
            description="Analyze wallets for risk and connections",
            endpoints=[
                APIEndpoint(
                    path="/api/wallet/deep-analysis/{wallet_address}",
                    method="GET",
                    description="Comprehensive wallet analysis with risk profiling",
                    parameters=[
                        {"name": "wallet_address", "type": "string", "required": True, "description": "Wallet address to analyze"},
                        {"name": "chain", "type": "string", "required": False, "description": "Blockchain: solana, ethereum, bsc"},
                        {"name": "include_history", "type": "boolean", "required": False, "description": "Include transaction history"}
                    ],
                    example_response={
                        "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                        "risk_score": 75,
                        "risk_level": "high",
                        "risk_factors": [
                            {"type": "known_scammer", "severity": "critical", "description": "Connected to known scammer wallets"},
                            {"type": "mixer_usage", "severity": "high", "description": "Frequent mixer interactions"}
                        ],
                        "connected_wallets": 45,
                        "transaction_count": 1234,
                        "related_scams": ["FakeToken2024", "RugPullXYZ"],
                        "behavioral_profile": {
                            "trading_style": "aggressive",
                            "risk_tolerance": "high",
                            "sophistication": "advanced"
                        }
                    },
                    tags=["wallet", "analysis", "risk"]
                ),
                APIEndpoint(
                    path="/api/wallet/behavioral-profile/{wallet_address}",
                    method="GET",
                    description="Get wallet behavioral profile",
                    parameters=[
                        {"name": "wallet_address", "type": "string", "required": True, "description": "Wallet address"},
                        {"name": "chain", "type": "string", "required": False, "description": "Blockchain"}
                    ],
                    example_response={
                        "wallet_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                        "trading_style": "swing_trader",
                        "holding_period_avg_days": 12.5,
                        "profit_loss_ratio": 1.3,
                        "risk_tolerance": "medium_high",
                        "sophistication_level": "intermediate",
                        "preferred_tokens": ["SOL", "BONK", "JUP"],
                        "activity_hours": [14, 15, 16, 20, 21],
                        "patterns": ["buys_dips", "takes_profits", "uses_dca"]
                    },
                    tags=["wallet", "behavior", "profile"]
                ),
            ]
        ))
        
        # Token Analysis APIs
        self.categories.append(APICategory(
            name="Token Analysis",
            description="Analyze tokens for security and risk",
            endpoints=[
                APIEndpoint(
                    path="/api/contract-check/{token_address}",
                    method="GET",
                    description="100-point contract security analysis",
                    parameters=[
                        {"name": "token_address", "type": "string", "required": True, "description": "Token contract address"}
                    ],
                    example_response={
                        "token_address": "Eyi4JcxVkS9fWzubSu5yS7dHy4kAiFHJN6Rwu6y7r8U",
                        "token_symbol": "CRM",
                        "overall_score": 85,
                        "risk_level": "low",
                        "category_scores": {
                            "ownership": 15,
                            "supply": 15,
                            "liquidity": 15,
                            "code": 10,
                            "holders": 15,
                            "history": 15
                        },
                        "flags": {
                            "red": [],
                            "yellow": ["High holder concentration"],
                            "green": ["Mint authority revoked", "Liquidity locked"]
                        },
                        "recommendation": "Low risk token with good security practices"
                    },
                    tags=["token", "contract", "security"]
                ),
            ]
        ))
        
        # Bubble Maps APIs
        self.categories.append(APICategory(
            name="Bubble Maps",
            description="Interactive wallet relationship visualizations",
            endpoints=[
                APIEndpoint(
                    path="/api/bubble-maps-pro/generate",
                    method="POST",
                    description="Generate interactive D3.js bubble map",
                    request_body={
                        "type": "object",
                        "required": ["center_wallet"],
                        "properties": {
                            "center_wallet": {"type": "string", "description": "Center wallet address"},
                            "depth": {"type": "integer", "description": "Exploration depth (1-5)", "default": 2},
                            "min_amount_usd": {"type": "number", "description": "Minimum transaction amount filter"},
                            "start_date": {"type": "string", "format": "date", "description": "Start date filter"},
                            "end_date": {"type": "string", "format": "date", "description": "End date filter"}
                        }
                    },
                    example_request={
                        "center_wallet": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                        "depth": 3,
                        "min_amount_usd": 100
                    },
                    example_response={
                        "map_id": "map_123",
                        "center_wallet": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                        "depth": 3,
                        "node_count": 156,
                        "edge_count": 423,
                        "cluster_count": 5,
                        "interactive_html_url": "/api/bubble-maps-pro/map_123/html",
                        "export_urls": {
                            "png": "/api/bubble-maps-pro/map_123/export/png",
                            "svg": "/api/bubble-maps-pro/map_123/export/svg",
                            "json": "/api/bubble-maps-pro/map_123/export/json"
                        }
                    },
                    tags=["bubble-maps", "visualization"]
                ),
            ]
        ))
        
        # Cluster Detection APIs
        self.categories.append(APICategory(
            name="Cluster Detection",
            description="Advanced wallet clustering with 7 detection methods",
            endpoints=[
                APIEndpoint(
                    path="/api/cluster-pro/detect",
                    method="POST",
                    description="Detect wallet clusters using multiple signals",
                    request_body={
                        "type": "object",
                        "required": ["wallets"],
                        "properties": {
                            "wallets": {"type": "array", "items": {"type": "string"}, "description": "List of wallet addresses"},
                            "min_confidence": {"type": "number", "description": "Minimum confidence threshold (0-1)", "default": 0.6}
                        }
                    },
                    example_request={
                        "wallets": [
                            "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                            "ABC123...",
                            "DEF456..."
                        ],
                        "min_confidence": 0.7
                    },
                    example_response={
                        "clusters_found": 2,
                        "wallets_analyzed": 3,
                        "clusters": [
                            {
                                "cluster_id": "cluster_1",
                                "wallets": ["7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU", "ABC123..."],
                                "confidence": 0.85,
                                "detection_methods": ["temporal_proximity", "common_funding", "behavioral_similarity"],
                                "cluster_type": "coordinated_group",
                                "behavior_tags": ["synchronized_trading", "shared_funding"]
                            }
                        ]
                    },
                    tags=["cluster", "detection", "wallets"]
                ),
            ]
        ))
        
        # KOL Tracking APIs
        self.categories.append(APICategory(
            name="KOL Tracking",
            description="Track influencer wallets and verify calls",
            endpoints=[
                APIEndpoint(
                    path="/api/kol-wallet/{handle}/positions",
                    method="GET",
                    description="Get KOL current positions",
                    parameters=[
                        {"name": "handle", "type": "string", "required": True, "description": "KOL handle (without @)"}
                    ],
                    example_response={
                        "kol_handle": "cryptoinfluencer",
                        "verified_wallets": ["7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"],
                        "positions": [
                            {
                                "token_address": "Eyi4JcxVkS9fWzubSu5yS7dHy4kAiFHJN6Rwu6y7r8U",
                                "token_symbol": "CRM",
                                "amount": 500000,
                                "value_usd": 25000,
                                "entry_price": 0.04,
                                "current_price": 0.05,
                                "unrealized_pnl": 5000,
                                "first_acquired": "2025-01-01T00:00:00Z"
                            }
                        ],
                        "total_value_usd": 125000,
                        "last_updated": "2025-01-15T12:00:00Z"
                    },
                    tags=["kol", "positions", "tracking"]
                ),
            ]
        ))
        
        # Transparency Tracker APIs
        self.categories.append(APICategory(
            name="Transparency Tracker",
            description="Project transparency scoring and assessment",
            endpoints=[
                APIEndpoint(
                    path="/api/transparency/{token_address}",
                    method="GET",
                    description="Get transparency score for token",
                    parameters=[
                        {"name": "token_address", "type": "string", "required": True, "description": "Token address"},
                        {"name": "chain", "type": "string", "required": False, "description": "Blockchain"}
                    ],
                    example_response={
                        "token_address": "Eyi4JcxVkS9fWzubSu5yS7dHy4kAiFHJN6Rwu6y7r8U",
                        "token_symbol": "CRM",
                        "overall_score": 78,
                        "overall_grade": "B+",
                        "percentile_rank": 72,
                        "category_scores": {
                            "team": 70,
                            "contract": 90,
                            "treasury": 75,
                            "communication": 80,
                            "audit": 85,
                            "roadmap": 70
                        },
                        "red_flags": [],
                        "green_flags": ["Mint authority revoked", "Liquidity locked for 2 years", "Team doxxed"],
                        "assessed_at": "2025-01-15T10:00:00Z"
                    },
                    tags=["transparency", "score", "assessment"]
                ),
            ]
        ))
        
        # Premium & Payment APIs
        self.categories.append(APICategory(
            name="Premium & Payments",
            description="Scan packs, API credits, and payments",
            endpoints=[
                APIEndpoint(
                    path="/api/premium/packages",
                    method="GET",
                    description="Get available scan packages with pricing",
                    parameters=[
                        {"name": "wallet_address", "type": "string", "required": False, "description": "For CRM holder discount calculation"}
                    ],
                    example_response={
                        "packages": [
                            {
                                "id": "starter",
                                "name": "Starter Pack",
                                "scan_count": 10,
                                "price": 10.00,
                                "crm_holder_price": 5.00,
                                "features": ["Contract Check", "Basic Wallet Investigation"]
                            },
                            {
                                "id": "pro",
                                "name": "Pro Pack",
                                "scan_count": 50,
                                "price": 35.00,
                                "crm_holder_price": 17.50,
                                "features": ["Contract Check", "Deep Wallet Analysis", "Cluster Detection", "Bubble Map"]
                            }
                        ],
                        "crm_holder_discount": "50%"
                    },
                    tags=["premium", "pricing", "scans"]
                ),
                APIEndpoint(
                    path="/api/marketplace/packages",
                    method="GET",
                    description="Get API marketplace packages",
                    parameters=[
                        {"name": "include_retail", "type": "boolean", "required": False, "description": "Include retail price comparison"}
                    ],
                    example_response={
                        "single_provider": {
                            "birdeye": [
                                {
                                    "key": "birdeye_starter",
                                    "credits": 10000,
                                    "final_price": 12.50,
                                    "price_per_1k": 1.25,
                                    "savings_vs_retail": "50%"
                                }
                            ]
                        },
                        "bundles": {
                            "bundle_forensic": {
                                "credits": 400000,
                                "final_price": 299.00,
                                "savings_vs_retail": {
                                    "retail_cost": 790.00,
                                    "total_savings": 491.00
                                }
                            }
                        }
                    },
                    tags=["marketplace", "api", "credits"]
                ),
            ]
        ))
        
        # Content Management APIs
        self.categories.append(APICategory(
            name="Content Management",
            description="Scam Library content and editorial workflow",
            endpoints=[
                APIEndpoint(
                    path="/api/content/library/search",
                    method="GET",
                    description="Search Scam Library articles",
                    parameters=[
                        {"name": "q", "type": "string", "required": True, "description": "Search query"},
                        {"name": "category", "type": "string", "required": False, "description": "Filter by category"}
                    ],
                    example_response={
                        "query": "rug pull",
                        "results": [
                            {
                                "id": "article_123",
                                "title": "Rug Pull: A Complete Guide",
                                "slug": "rug-pull-guide",
                                "excerpt": "Learn how rug pulls work and how to spot them...",
                                "type": "scam_guide",
                                "difficulty": "beginner",
                                "read_time": 8,
                                "score": 15.5
                            }
                        ],
                        "count": 12
                    },
                    tags=["content", "library", "search"]
                ),
            ]
        ))
        
        # News Aggregator APIs
        self.categories.append(APICategory(
            name="News Aggregator",
            description="Crypto security news aggregation",
            endpoints=[
                APIEndpoint(
                    path="/api/news/fetch",
                    method="POST",
                    description="Fetch latest news from all sources",
                    example_response={
                        "fetched": 15,
                        "items": [
                            {
                                "id": "news_123",
                                "title": "Major Exchange Hacked",
                                "source": "peckshield",
                                "category": "hack",
                                "risk_level": "critical",
                                "published_at": "2025-01-15T10:00:00Z"
                            }
                        ]
                    },
                    tags=["news", "aggregator"]
                ),
            ]
        ))
        
        # Portfolio APIs
        self.categories.append(APICategory(
            name="Portfolio",
            description="Portfolio tracking with risk alerts",
            endpoints=[
                APIEndpoint(
                    path="/api/portfolio/{portfolio_id}",
                    method="GET",
                    description="Get portfolio details with risk analysis",
                    example_response={
                        "id": "portfolio_123",
                        "name": "My Crypto Portfolio",
                        "total_value_usd": 50000.00,
                        "overall_risk_score": 45,
                        "overall_risk_level": "medium",
                        "high_risk_tokens": 2,
                        "tokens": [
                            {
                                "symbol": "CRM",
                                "value_usd": 25000.00,
                                "risk_score": 25,
                                "risk_level": "low"
                            }
                        ]
                    },
                    tags=["portfolio", "tracking", "risk"]
                ),
            ]
        ))
    
    def get_full_documentation(self) -> Dict:
        """Get complete API documentation."""
        return {
            "api_name": "RMI Platform API",
            "version": "2.0.0",
            "base_url": "https://intel.cryptorugmunch.com/api",
            "authentication": {
                "type": "API Key",
                "header": "X-API-Key",
                "description": "Include your API key in the X-API-Key header"
            },
            "rate_limits": {
                "free": "100 requests/minute",
                "starter": "500 requests/minute",
                "pro": "2000 requests/minute",
                "enterprise": "10000 requests/minute"
            },
            "categories": [
                {
                    "name": cat.name,
                    "description": cat.description,
                    "endpoints": [
                        {
                            "path": ep.path,
                            "method": ep.method,
                            "description": ep.description,
                            "parameters": ep.parameters,
                            "authentication": ep.authentication,
                            "rate_limit": ep.rate_limit,
                            "tags": ep.tags,
                            "deprecated": ep.deprecated
                        }
                        for ep in cat.endpoints
                    ]
                }
                for cat in self.categories
            ]
        }
    
    def get_openapi_spec(self) -> Dict:
        """Generate OpenAPI 3.0 specification."""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "RMI Platform API",
                "version": "2.0.0",
                "description": "Crypto fraud investigation and protection platform",
                "contact": {
                    "name": "RMI Support",
                    "url": "https://intel.cryptorugmunch.com/support"
                }
            },
            "servers": [
                {"url": "https://intel.cryptorugmunch.com/api", "description": "Production"},
                {"url": "https://staging.intel.cryptorugmunch.com/api", "description": "Staging"}
            ],
            "paths": {}
        }
        
        # Add paths
        for category in self.categories:
            for endpoint in category.endpoints:
                path = endpoint.path.replace("/api", "")
                
                if path not in spec["paths"]:
                    spec["paths"][path] = {}
                
                method = endpoint.method.lower()
                spec["paths"][path][method] = {
                    "summary": endpoint.description,
                    "tags": endpoint.tags,
                    "parameters": [
                        {
                            "name": p["name"],
                            "in": "query" if "{" not in endpoint.path else "path",
                            "required": p.get("required", False),
                            "schema": {"type": p["type"]},
                            "description": p.get("description", "")
                        }
                        for p in endpoint.parameters
                    ],
                    "responses": {
                        "200": {
                            "description": "Success",
                            "content": {
                                "application/json": {
                                    "schema": endpoint.response_schema,
                                    "example": endpoint.example_response
                                }
                            }
                        }
                    }
                }
                
                if endpoint.request_body:
                    spec["paths"][path][method]["requestBody"] = {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": endpoint.request_body,
                                "example": endpoint.example_request
                            }
                        }
                    }
        
        return spec


# ============== FASTAPI ENDPOINTS ==============

from fastapi import APIRouter

router = APIRouter(prefix="/api/docs", tags=["API Documentation"])

# Global instance
api_docs = APIDocumentation()


@router.get("")
async def get_documentation():
    """Get complete API documentation."""
    return api_docs.get_full_documentation()


@router.get("/openapi.json")
async def get_openapi_spec():
    """Get OpenAPI 3.0 specification."""
    return api_docs.get_openapi_spec()


@router.get("/categories")
async def get_categories():
    """Get API categories."""
    return {
        "categories": [
            {"name": cat.name, "description": cat.description, "endpoint_count": len(cat.endpoints)}
            for cat in api_docs.categories
        ]
    }


@router.get("/endpoints")
async def get_all_endpoints():
    """Get all API endpoints."""
    endpoints = []
    for cat in api_docs.categories:
        for ep in cat.endpoints:
            endpoints.append({
                "path": ep.path,
                "method": ep.method,
                "description": ep.description,
                "category": cat.name,
                "tags": ep.tags
            })
    
    return {"endpoints": endpoints, "count": len(endpoints)}
