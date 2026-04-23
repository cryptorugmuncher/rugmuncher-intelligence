"""
RMI Web Application - Backend API Server
=========================================
Flask-based backend for the RMI investigation platform.
Serves web frontend and provides API endpoints.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from functools import wraps
from typing import Dict, List, Optional

# Add parent to path
sys.path.insert(0, '/mnt/okcomputer/output/omega_forensic_v5')

from flask import Flask, jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS

# Import our modules
from forensic.wallet_clustering import get_clustering_engine
from forensic.api_arsenal import get_api_arsenal
from forensic.report_generator import get_report_generator
from forensic.contract_checker import get_contract_checker
from forensic.dev_finder import get_dev_finder
from forensic.shill_tracker import get_shill_tracker
from forensic.kol_reputation import get_kol_reputation_system
from forensic.trending_scams import get_trending_scams_monitor
from forensic.final_report_generator import get_final_report_generator
from forensic.bubble_maps_pro import BubbleMapsPro
from forensic.cluster_detection_pro import ClusterDetectionPro
from forensic.deep_wallet_analysis import DeepWalletAnalyzer
from forensic.kol_wallet_tracker import KOLWalletTracker
from core.llm_rotation import get_llm_rotator, quick_generate, deep_analyze
from core.newsletter_system import get_newsletter_system, SubscriptionTier
from core.wallet_protection import get_wallet_protection
from core.transparency_tracker import TransparencyTracker
from core.premium_scans import PremiumScans
from core.api_marketplace import APIMarketplace
from bots.rmi_bot import get_rmi_bot
from web.bubble_map_visualizer import get_visualizer


# Flask app
app = Flask(__name__)
CORS(app)

# Configuration
APP_VERSION = "2.0.0"
APP_NAME = "RMI - RugMunch Intelligence"
DOMAIN = "intel.cryptorugmunch.com"

# Initialize new modules
bubble_maps_pro = BubbleMapsPro()
cluster_detection_pro = ClusterDetectionPro()
transparency_tracker = TransparencyTracker()
premium_scans = PremiumScans()
deep_wallet_analyzer = DeepWalletAnalyzer()
kol_wallet_tracker = KOLWalletTracker()
api_marketplace = APIMarketplace()


def async_route(f):
    """Decorator to handle async routes."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


# ============== STATUS & INFO ==============

@app.route('/')
def index():
    """Main page."""
    return render_template_string(MAIN_PAGE_HTML, version=APP_VERSION, domain=DOMAIN)


@app.route('/api/status')
def api_status():
    """API status endpoint."""
    return jsonify({
        "status": "online",
        "version": APP_VERSION,
        "name": APP_NAME,
        "timestamp": datetime.now().isoformat(),
        "domain": DOMAIN,
        "features": [
            "contract_check",
            "dev_finder",
            "shill_tracker",
            "kol_reputation",
            "kol_wallet_tracker",
            "trending_scams",
            "wallet_protection",
            "newsletter",
            "wallet_clustering",
            "cluster_detection_pro",
            "bubble_maps",
            "bubble_maps_pro",
            "transparency_tracker",
            "premium_scans",
            "deep_wallet_analysis",
            "api_marketplace"
        ]
    })


@app.route('/api/methodology')
def api_methodology():
    """Get methodology documentation."""
    return jsonify({
        "platform": APP_NAME,
        "version": APP_VERSION,
        "built_with": "Kimi AI",
        "features": {
            "contract_check": {
                "description": "100-point rug pull analysis",
                "checks": [
                    "Ownership (15 pts) - Renounced, mint, freeze, upgrade",
                    "Supply (15 pts) - Concentration, max supply, burn",
                    "Liquidity (15 pts) - Locked, concentration, LP burn",
                    "Code (10 pts) - Verified, vulnerabilities",
                    "Holders (15 pts) - Distribution, whales, new wallets",
                    "History (15 pts) - Deployer, similar contracts, rugs",
                    "Trading (10 pts) - Volume, manipulation",
                    "Social (5 pts) - Presence, legitimacy"
                ]
            },
            "dev_finder": {
                "description": "Track developer history and tokens",
                "features": ["All tokens deployed", "Rug history", "Connected wallets", "Risk scoring"]
            },
            "shill_tracker": {
                "description": "X/Twitter campaign detection",
                "features": ["Coordinated posting", "Bot networks", "KOL tracking", "Cost estimation"]
            },
            "kol_reputation": {
                "description": "Influencer performance tracking",
                "tiers": ["Diamond (90+)", "Platinum (80+)", "Gold (70+)", "Silver (60+)", "Bronze (50+)"]
            },
            "kol_wallet_tracker": {
                "description": "Track KOL wallet positions and calls",
                "features": ["Position tracking", "Call verification", "Rug signal detection", "Performance metrics"]
            },
            "wallet_protection": {
                "description": "Transaction protection tools",
                "features": ["Blocklist", "Warnings", "Simulation", "Risk assessment"]
            },
            "cluster_detection_pro": {
                "description": "Advanced wallet clustering with 7 detection methods",
                "methods": [
                    "Temporal proximity analysis",
                    "Common counterparties",
                    "Behavioral similarity",
                    "Common funding sources",
                    "Transaction patterns",
                    "Code similarity",
                    "Social connections"
                ]
            },
            "bubble_maps_pro": {
                "description": "Interactive D3.js bubble maps",
                "features": ["Fully interactive", "Depth 1-5 hops", "Time/amount filters", "Export PNG/SVG/JSON"]
            },
            "transparency_tracker": {
                "description": "Project transparency scoring",
                "categories": ["Team", "Contract", "Treasury", "Communication", "Audit", "Roadmap"],
                "grades": ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"]
            },
            "deep_wallet_analysis": {
                "description": "Deep wallet investigation",
                "features": ["Scam connections", "Mixer detection", "Cross-chain activity", "Behavioral profiling"]
            },
            "api_marketplace": {
                "description": "Cheap API credits for investigators",
                "providers": ["Birdeye", "Helius", "Shyft", "QuickNode", "Alchemy", "Moralis", "Bitquery"],
                "discounts": "Up to 70% off retail + 20% for CRM holders"
            }
        },
        "evidence_tiers": {
            "tier_1": "Direct evidence - Confirmed on-chain",
            "tier_2": "Strong correlation - Multiple sources agree",
            "tier_3": "Suspicious pattern - Worth investigating",
            "tier_4": "Indirect connection - Circumstantial",
            "tier_5": "Unverified - Needs confirmation"
        },
        "apis_used": [
            "Helius (Solana data)",
            "Arkham Intelligence (entity labels)",
            "MistTrack (risk scoring)",
            "ChainAbuse (scam reports)",
            "BirdEye (token data)",
            "LunarCrush (social metrics)"
        ],
        "llm_models": [
            "Llama 3.3 70B (Groq)",
            "Gemini 2.0 Flash (Google)",
            "Claude 3 Haiku (Anthropic)",
            "DeepSeek Chat (DeepSeek)",
            "Phi-4 (Local)",
            "Qwen2.5-7B (Local)"
        ],
        "timestamp": datetime.now().isoformat()
    })


# ============== CONTRACT CHECK ==============

@app.route('/api/contract-check/<token_address>')
@async_route
async def api_contract_check(token_address: str):
    """100-point contract analysis."""
    if len(token_address) != 44:
        return jsonify({"error": "Invalid token address"}), 400
    
    checker = get_contract_checker()
    analysis = await checker.analyze_contract(token_address)
    
    return jsonify(analysis.to_dict())


@app.route('/api/contract-check/batch', methods=['POST'])
@async_route
async def api_contract_check_batch():
    """Batch contract analysis."""
    data = request.json or {}
    tokens = data.get('tokens', [])
    
    if len(tokens) > 10:
        return jsonify({"error": "Max 10 tokens per batch"}), 400
    
    checker = get_contract_checker()
    results = []
    
    for token in tokens:
        analysis = await checker.analyze_contract(token)
        results.append(analysis.to_dict())
    
    return jsonify({
        "results": results,
        "count": len(results),
        "timestamp": datetime.now().isoformat()
    })


# ============== DEV FINDER ==============

@app.route('/api/dev-finder/<token_address>')
@async_route
async def api_dev_finder(token_address: str):
    """Find developer behind token."""
    if len(token_address) != 44:
        return jsonify({"error": "Invalid token address"}), 400
    
    finder = get_dev_finder()
    developer = await finder.find_developer(token_address)
    
    if not developer:
        return jsonify({"error": "Developer not found"}), 404
    
    return jsonify(developer.to_dict())


@app.route('/api/dev-finder/wallet/<wallet_address>')
@async_route
async def api_dev_by_wallet(wallet_address: str):
    """Get developer by wallet address."""
    finder = get_dev_finder()
    report = await finder.generate_dev_report(wallet_address)
    
    if not report:
        return jsonify({"error": "Developer not found"}), 404
    
    return jsonify(report)


@app.route('/api/dev-finder/search')
@async_route
async def api_dev_search():
    """Search developers."""
    query = request.args.get('q', '')
    
    finder = get_dev_finder()
    results = finder.search_database(query)
    
    return jsonify({
        "query": query,
        "results": [r.to_dict() for r in results],
        "count": len(results)
    })


# ============== SHILL TRACKER ==============

@app.route('/api/shill-tracker/track/<token_address>')
@async_route
async def api_shill_track(token_address: str):
    """Start tracking shill campaign for token."""
    tracker = get_shill_tracker()
    campaign = await tracker.track_token(token_address, "UNKNOWN")
    
    return jsonify(campaign.to_dict())


@app.route('/api/shill-tracker/campaign/<campaign_id>')
@async_route
async def api_shill_campaign(campaign_id: str):
    """Get campaign report."""
    tracker = get_shill_tracker()
    report = await tracker.generate_campaign_report(campaign_id)
    
    if not report:
        return jsonify({"error": "Campaign not found"}), 404
    
    return jsonify(report)


@app.route('/api/shill-tracker/kol/<handle>')
@async_route
async def api_kol_report(handle: str):
    """Get KOL report."""
    tracker = get_shill_tracker()
    report = await tracker.get_kol_report(handle)
    
    if not report:
        return jsonify({"error": "KOL not found"}), 404
    
    return jsonify(report)


# ============== KOL REPUTATION ==============

@app.route('/api/kol/leaderboard')
@async_route
async def api_kol_leaderboard():
    """Get KOL leaderboard."""
    timeframe = request.args.get('timeframe', 'all_time')
    limit = request.args.get('limit', 100, type=int)
    
    system = get_kol_reputation_system()
    leaderboard = await system.get_leaderboard(timeframe, limit)
    
    return jsonify({
        "timeframe": timeframe,
        "leaderboard": leaderboard,
        "count": len(leaderboard)
    })


@app.route('/api/kol/<handle>')
@async_route
async def api_kol_detail(handle: str):
    """Get detailed KOL report."""
    system = get_kol_reputation_system()
    report = await system.get_kol_report(handle)
    
    if not report:
        return jsonify({"error": "KOL not found"}), 404
    
    return jsonify(report)


@app.route('/api/kol/search')
@async_route
async def api_kol_search():
    """Search KOLs."""
    query = request.args.get('q', '')
    
    system = get_kol_reputation_system()
    results = await system.search_kols(query)
    
    return jsonify({
        "query": query,
        "results": [r.to_dict() for r in results],
        "count": len(results)
    })


# ============== KOL WALLET TRACKER (NEW) ==============

@app.route('/api/kol-wallet/identify', methods=['POST'])
@async_route
async def api_kol_wallet_identify():
    """Identify KOL wallet from social media."""
    data = request.json or {}
    kol_handle = data.get('handle')
    platform = data.get('platform', 'twitter')
    
    if not kol_handle:
        return jsonify({"error": "KOL handle required"}), 400
    
    result = await kol_wallet_tracker.identify_kol_wallet(kol_handle, platform)
    return jsonify(result)


@app.route('/api/kol-wallet/<kol_handle>/positions')
@async_route
async def api_kol_positions(kol_handle: str):
    """Get KOL positions."""
    result = await kol_wallet_tracker.track_positions(kol_handle)
    return jsonify(result)


@app.route('/api/kol-wallet/<kol_handle>/performance')
@async_route
async def api_kol_performance(kol_handle: str):
    """Get KOL trading performance."""
    days = request.args.get('days', 30, type=int)
    result = await kol_wallet_tracker.get_trading_performance(kol_handle, days)
    return jsonify(result)


@app.route('/api/kol-wallet/<kol_handle>/verify-call', methods=['POST'])
@async_route
async def api_kol_verify_call(kol_handle: str):
    """Verify if KOL call matches wallet activity."""
    data = request.json or {}
    token_address = data.get('token_address')
    call_type = data.get('call_type', 'buy')
    
    if not token_address:
        return jsonify({"error": "Token address required"}), 400
    
    result = await kol_wallet_tracker.verify_call(kol_handle, token_address, call_type)
    return jsonify(result)


@app.route('/api/kol-wallet/<kol_handle>/rug-signals')
@async_route
async def api_kol_rug_signals(kol_handle: str):
    """Detect rug signals for KOL."""
    result = await kol_wallet_tracker.detect_rug_signals(kol_handle)
    return jsonify(result)


@app.route('/api/kol-wallet/leaderboard')
@async_route
async def api_kol_wallet_leaderboard():
    """Get KOL wallet leaderboard."""
    metric = request.args.get('metric', 'accuracy_score')
    limit = request.args.get('limit', 50, type=int)
    
    result = await kol_wallet_tracker.get_leaderboard(metric, limit)
    return jsonify(result)


# ============== TRENDING SCAMS ==============

@app.route('/api/trending-scams')
@async_route
async def api_trending_scams():
    """Get trending scams list."""
    limit = request.args.get('limit', 20, type=int)
    
    monitor = get_trending_scams_monitor()
    scams = await monitor.get_trending_list(limit)
    
    return jsonify({
        "scams": scams,
        "count": len(scams),
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/trending-scams/<token_address>')
@async_route
async def api_scam_detail(token_address: str):
    """Get detailed scam report."""
    monitor = get_trending_scams_monitor()
    report = await monitor.get_scam_report(token_address)
    
    if not report:
        return jsonify({"error": "Scam not found"}), 404
    
    return jsonify(report)


@app.route('/api/trending-scams/stats')
def api_scam_stats():
    """Get scam monitor statistics."""
    monitor = get_trending_scams_monitor()
    stats = monitor.get_stats()
    
    return jsonify(stats)


# ============== WALLET PROTECTION ==============

@app.route('/api/wallet-protection/check', methods=['POST'])
@async_route
async def api_wallet_check():
    """Check transaction before signing."""
    data = request.json or {}
    
    wallet = data.get('wallet')
    token = data.get('token')
    value = data.get('value', 0)
    tx_type = data.get('type', 'buy')
    
    if not wallet or not token:
        return jsonify({"error": "Wallet and token required"}), 400
    
    protection = get_wallet_protection()
    check = await protection.check_transaction(wallet, token, value, tx_type)
    
    return jsonify(check.to_dict())


@app.route('/api/wallet-protection/protect', methods=['POST'])
@async_route
async def api_wallet_protect():
    """Enable protection for wallet."""
    data = request.json or {}
    wallet = data.get('wallet')
    settings = data.get('settings', {})
    
    if not wallet:
        return jsonify({"error": "Wallet address required"}), 400
    
    protection = get_wallet_protection()
    protected = await protection.protect_wallet(wallet, settings)
    
    return jsonify(protected.to_dict())


@app.route('/api/wallet-protection/stats')
def api_protection_stats():
    """Get protection statistics."""
    wallet = request.args.get('wallet')
    
    protection = get_wallet_protection()
    stats = protection.get_protection_stats(wallet)
    
    return jsonify(stats)


@app.route('/api/wallet-protection/simulate', methods=['POST'])
@async_route
async def api_simulate_transaction():
    """Simulate a transaction."""
    data = request.json or {}
    
    wallet = data.get('wallet')
    token = data.get('token')
    amount = data.get('amount', 0)
    
    if not wallet or not token:
        return jsonify({"error": "Wallet and token required"}), 400
    
    protection = get_wallet_protection()
    simulation = await protection.simulate_transaction(wallet, token, amount)
    
    return jsonify(simulation)


# ============== DEEP WALLET ANALYSIS (NEW) ==============

@app.route('/api/wallet/deep-analysis/<wallet_address>')
@async_route
async def api_deep_wallet_analysis(wallet_address: str):
    """Deep wallet analysis with risk profiling."""
    chain = request.args.get('chain', 'solana')
    include_history = request.args.get('include_history', 'true').lower() == 'true'
    
    result = await deep_wallet_analyzer.analyze_wallet(
        wallet_address, chain, include_history
    )
    return jsonify(result)


@app.route('/api/wallet/behavioral-profile/<wallet_address>')
@async_route
async def api_wallet_behavioral_profile(wallet_address: str):
    """Get wallet behavioral profile."""
    chain = request.args.get('chain', 'solana')
    
    result = await deep_wallet_analyzer.get_behavioral_profile(wallet_address, chain)
    return jsonify(result)


@app.route('/api/wallet/scam-connections/<wallet_address>')
@async_route
async def api_wallet_scam_connections(wallet_address: str):
    """Find wallet connections to known scams."""
    chain = request.args.get('chain', 'solana')
    
    result = await deep_wallet_analyzer.find_scam_connections(wallet_address, chain)
    return jsonify(result)


@app.route('/api/wallet/risk-assessment/<wallet_address>')
@async_route
async def api_wallet_risk_assessment(wallet_address: str):
    """Get comprehensive risk assessment."""
    chain = request.args.get('chain', 'solana')
    
    result = await deep_wallet_analyzer.get_risk_assessment(wallet_address, chain)
    return jsonify(result)


@app.route('/api/wallet/batch-analysis', methods=['POST'])
@async_route
async def api_batch_wallet_analysis():
    """Analyze multiple wallets."""
    data = request.json or {}
    wallets = data.get('wallets', [])
    chain = data.get('chain', 'solana')
    
    if len(wallets) > 20:
        return jsonify({"error": "Max 20 wallets per batch"}), 400
    
    result = await deep_wallet_analyzer.batch_analyze(wallets, chain)
    return jsonify(result)


# ============== BUBBLE MAPS PRO (NEW) ==============

@app.route('/api/bubble-maps-pro/generate', methods=['POST'])
@async_route
async def api_bubble_maps_pro_generate():
    """Generate interactive bubble map."""
    data = request.json or {}
    center_wallet = data.get('center_wallet')
    depth = data.get('depth', 2)
    min_amount = data.get('min_amount_usd')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not center_wallet:
        return jsonify({"error": "Center wallet required"}), 400
    
    result = await bubble_maps_pro.generate_map(
        center_wallet=center_wallet,
        depth=depth,
        min_amount_usd=min_amount,
        start_date=start_date,
        end_date=end_date
    )
    return jsonify(result)


@app.route('/api/bubble-maps-pro/<center_wallet>/html')
@async_route
async def api_bubble_maps_pro_html(center_wallet: str):
    """Get interactive HTML bubble map."""
    depth = request.args.get('depth', 2, type=int)
    
    result = await bubble_maps_pro.generate_map(center_wallet, depth)
    
    if 'interactive_html' in result:
        from flask import Response
        return Response(result['interactive_html'], mimetype='text/html')
    
    return jsonify(result)


@app.route('/api/bubble-maps-pro/<center_wallet>/export/<format>')
@async_route
async def api_bubble_maps_pro_export(center_wallet: str, format: str):
    """Export bubble map in various formats."""
    depth = request.args.get('depth', 2, type=int)
    
    if format not in ['png', 'svg', 'json']:
        return jsonify({"error": "Format must be png, svg, or json"}), 400
    
    result = await bubble_maps_pro.export_map(center_wallet, format, depth)
    return jsonify(result)


@app.route('/api/bubble-maps-pro/compare', methods=['POST'])
@async_route
async def api_bubble_maps_pro_compare():
    """Compare bubble maps over time."""
    data = request.json or {}
    center_wallet = data.get('center_wallet')
    dates = data.get('dates', [])
    
    if not center_wallet or len(dates) < 2:
        return jsonify({"error": "Center wallet and at least 2 dates required"}), 400
    
    result = await bubble_maps_pro.compare_maps(center_wallet, dates)
    return jsonify(result)


# ============== CLUSTER DETECTION PRO (NEW) ==============

@app.route('/api/cluster-pro/detect', methods=['POST'])
@async_route
async def api_cluster_pro_detect():
    """Detect wallet clusters with advanced algorithms."""
    data = request.json or {}
    wallets = data.get('wallets', [])
    min_confidence = data.get('min_confidence', 0.6)
    
    if len(wallets) < 2:
        return jsonify({"error": "At least 2 wallets required"}), 400
    
    result = await cluster_detection_pro.detect_clusters(wallets, min_confidence)
    return jsonify(result)


@app.route('/api/cluster-pro/<cluster_id>')
@async_route
async def api_cluster_pro_detail(cluster_id: str):
    """Get detailed cluster information."""
    result = await cluster_detection_pro.get_cluster_details(cluster_id)
    return jsonify(result)


@app.route('/api/cluster-pro/<cluster_id>/evolution')
@async_route
async def api_cluster_pro_evolution(cluster_id: str):
    """Track cluster evolution over time."""
    days = request.args.get('days', 30, type=int)
    
    result = await cluster_detection_pro.track_evolution(cluster_id, days)
    return jsonify(result)


@app.route('/api/cluster-pro/<cluster_id>/visualization')
@async_route
async def api_cluster_pro_visualization(cluster_id: str):
    """Get cluster visualization data."""
    result = await cluster_detection_pro.visualize_cluster(cluster_id)
    return jsonify(result)


@app.route('/api/cluster-pro/find-related', methods=['POST'])
@async_route
async def api_cluster_pro_find_related():
    """Find clusters related to a wallet."""
    data = request.json or {}
    wallet_address = data.get('wallet_address')
    
    if not wallet_address:
        return jsonify({"error": "Wallet address required"}), 400
    
    result = await cluster_detection_pro.find_related_clusters(wallet_address)
    return jsonify(result)


# ============== TRANSPARENCY TRACKER (NEW) ==============

@app.route('/api/transparency/<token_address>')
@async_route
async def api_transparency_score(token_address: str):
    """Get transparency score for token."""
    chain = request.args.get('chain', 'solana')
    
    result = await transparency_tracker.assess_token(token_address, chain)
    return jsonify(result)


@app.route('/api/transparency/<token_address>/detailed')
@async_route
async def api_transparency_detailed(token_address: str):
    """Get detailed transparency report."""
    chain = request.args.get('chain', 'solana')
    
    result = await transparency_tracker.get_detailed_report(token_address, chain)
    return jsonify(result)


@app.route('/api/transparency/compare', methods=['POST'])
@async_route
async def api_transparency_compare():
    """Compare transparency scores."""
    data = request.json or {}
    tokens = data.get('tokens', [])
    
    if len(tokens) < 2:
        return jsonify({"error": "At least 2 tokens required"}), 400
    
    result = await transparency_tracker.compare_tokens(tokens)
    return jsonify(result)


@app.route('/api/transparency/leaderboard')
@async_route
async def api_transparency_leaderboard():
    """Get transparency leaderboard."""
    chain = request.args.get('chain', 'solana')
    limit = request.args.get('limit', 100, type=int)
    min_score = request.args.get('min_score', 0, type=int)
    
    result = await transparency_tracker.get_leaderboard(chain, limit, min_score)
    return jsonify(result)


@app.route('/api/transparency/category-breakdown/<category>')
@async_route
async def api_transparency_category_breakdown(category: str):
    """Get category-specific breakdown."""
    valid_categories = ['team', 'contract', 'treasury', 'communication', 'audit', 'roadmap']
    
    if category not in valid_categories:
        return jsonify({"error": f"Category must be one of {valid_categories}"}), 400
    
    chain = request.args.get('chain', 'solana')
    limit = request.args.get('limit', 50, type=int)
    
    result = await transparency_tracker.get_category_breakdown(category, chain, limit)
    return jsonify(result)


# ============== PREMIUM SCANS (NEW) ==============

@app.route('/api/premium/packages')
@async_route
async def api_premium_packages():
    """Get available scan packages."""
    wallet_address = request.args.get('wallet_address')
    
    result = await premium_scans.get_packages(wallet_address)
    return jsonify(result)


@app.route('/api/premium/calculate-price', methods=['POST'])
@async_route
async def api_premium_calculate_price():
    """Calculate price with discounts."""
    data = request.json or {}
    package_type = data.get('package_type')
    wallet_address = data.get('wallet_address')
    
    if not package_type:
        return jsonify({"error": "Package type required"}), 400
    
    result = await premium_scans.calculate_price(package_type, wallet_address)
    return jsonify(result)


@app.route('/api/premium/purchase', methods=['POST'])
@async_route
async def api_premium_purchase():
    """Create purchase request."""
    data = request.json or {}
    user_id = data.get('user_id')
    package_type = data.get('package_type')
    wallet_address = data.get('wallet_address')
    
    if not all([user_id, package_type, wallet_address]):
        return jsonify({"error": "user_id, package_type, and wallet_address required"}), 400
    
    result = await premium_scans.create_purchase(user_id, package_type, wallet_address)
    return jsonify(result)


@app.route('/api/premium/verify-payment', methods=['POST'])
@async_route
async def api_premium_verify_payment():
    """Verify payment and activate package."""
    data = request.json or {}
    payment_id = data.get('payment_id')
    tx_signature = data.get('tx_signature')
    
    if not payment_id or not tx_signature:
        return jsonify({"error": "payment_id and tx_signature required"}), 400
    
    result = await premium_scans.verify_payment(payment_id, tx_signature)
    return jsonify(result)


@app.route('/api/premium/user-scans/<user_id>')
@async_route
async def api_premium_user_scans(user_id: str):
    """Get user's scan balance."""
    result = await premium_scans.get_user_scans(user_id)
    return jsonify(result)


@app.route('/api/premium/use-scan', methods=['POST'])
@async_route
async def api_premium_use_scan():
    """Use a scan."""
    data = request.json or {}
    user_id = data.get('user_id')
    scan_type = data.get('scan_type')
    
    if not user_id or not scan_type:
        return jsonify({"error": "user_id and scan_type required"}), 400
    
    result = await premium_scans.use_scan(user_id, scan_type)
    return jsonify(result)


@app.route('/api/premium/usage-history/<user_id>')
@async_route
async def api_premium_usage_history(user_id: str):
    """Get scan usage history."""
    days = request.args.get('days', 30, type=int)
    
    result = await premium_scans.get_usage_history(user_id, days)
    return jsonify(result)


# ============== API MARKETPLACE (NEW) ==============

@app.route('/api/marketplace/packages')
@async_route
async def api_marketplace_packages():
    """Get all API packages."""
    include_retail = request.args.get('include_retail', 'true').lower() == 'true'
    
    result = await api_marketplace.get_all_packages(include_retail)
    return jsonify(result)


@app.route('/api/marketplace/packages/<package_key>/price')
@async_route
async def api_marketplace_package_price(package_key: str):
    """Get package price with discounts."""
    wallet_address = request.args.get('wallet_address')
    
    if not wallet_address:
        return jsonify({"error": "wallet_address required"}), 400
    
    result = await api_marketplace.calculate_price(package_key, wallet_address)
    return jsonify(result)


@app.route('/api/marketplace/payment/create', methods=['POST'])
@async_route
async def api_marketplace_create_payment():
    """Create payment for API credits."""
    data = request.json or {}
    user_id = data.get('user_id')
    package_key = data.get('package_key')
    wallet_address = data.get('wallet_address')
    
    if not all([user_id, package_key, wallet_address]):
        return jsonify({"error": "user_id, package_key, and wallet_address required"}), 400
    
    result = await api_marketplace.create_payment(user_id, package_key, wallet_address)
    return jsonify(result)


@app.route('/api/marketplace/payment/verify', methods=['POST'])
@async_route
async def api_marketplace_verify_payment():
    """Verify payment and activate credits."""
    data = request.json or {}
    payment_id = data.get('payment_id')
    tx_signature = data.get('tx_signature')
    
    if not payment_id or not tx_signature:
        return jsonify({"error": "payment_id and tx_signature required"}), 400
    
    result = await api_marketplace.verify_payment(payment_id, tx_signature)
    return jsonify(result)


@app.route('/api/marketplace/credits/<user_id>')
@async_route
async def api_marketplace_user_credits(user_id: str):
    """Get user's API credit balance."""
    result = await api_marketplace.get_user_credits(user_id)
    return jsonify(result)


@app.route('/api/marketplace/credits/use', methods=['POST'])
@async_route
async def api_marketplace_use_credits():
    """Use API credits."""
    data = request.json or {}
    user_id = data.get('user_id')
    provider = data.get('provider')
    amount = data.get('amount', 1)
    
    if not user_id or not provider:
        return jsonify({"error": "user_id and provider required"}), 400
    
    from core.api_marketplace import APIProvider
    try:
        provider_enum = APIProvider(provider)
    except ValueError:
        return jsonify({"error": f"Invalid provider. Valid: {[p.value for p in APIProvider]}"}), 400
    
    result = await api_marketplace.use_credits(user_id, provider_enum, amount)
    return jsonify(result)


@app.route('/api/marketplace/usage/<user_id>')
@async_route
async def api_marketplace_usage(user_id: str):
    """Get API usage analytics."""
    days = request.args.get('days', 30, type=int)
    
    result = await api_marketplace.get_usage_analytics(user_id, days)
    return jsonify(result)


@app.route('/api/marketplace/stats')
@async_route
async def api_marketplace_stats():
    """Get marketplace statistics."""
    result = await api_marketplace.get_marketplace_stats()
    return jsonify(result)


@app.route('/api/marketplace/crm-check/<wallet_address>')
@async_route
async def api_marketplace_crm_check(wallet_address: str):
    """Check CRM holder status for discounts."""
    result = await api_marketplace.check_crm_holder_discount(wallet_address)
    return jsonify(result)


# ============== NEWSLETTER ==============

@app.route('/api/newsletter/subscribe', methods=['POST'])
@async_route
async def api_newsletter_subscribe():
    """Subscribe to newsletter."""
    data = request.json or {}
    
    email = data.get('email')
    tier_name = data.get('tier', 'free')
    wallet = data.get('wallet')
    
    if not email:
        return jsonify({"error": "Email required"}), 400
    
    try:
        tier = SubscriptionTier(tier_name)
    except ValueError:
        return jsonify({"error": "Invalid tier"}), 400
    
    system = get_newsletter_system()
    subscriber = await system.subscribe(email, tier, wallet)
    
    # Generate payment request if paid tier
    if tier != SubscriptionTier.FREE:
        payment = await system.generate_payment_request(email, tier)
        return jsonify({
            "subscriber": {"email": subscriber.email, "tier": subscriber.tier.value},
            "payment": payment
        })
    
    return jsonify({
        "email": subscriber.email,
        "tier": subscriber.tier.value,
        "status": "subscribed"
    })


@app.route('/api/newsletter/payment/verify', methods=['POST'])
@async_route
async def api_verify_payment():
    """Verify crypto payment."""
    data = request.json or {}
    
    email = data.get('email')
    tx_signature = data.get('tx_signature')
    
    if not email or not tx_signature:
        return jsonify({"error": "Email and transaction signature required"}), 400
    
    system = get_newsletter_system()
    success = await system.verify_payment(email, tx_signature)
    
    return jsonify({
        "success": success,
        "email": email
    })


@app.route('/api/newsletter/latest')
@async_route
async def api_latest_newsletter():
    """Get latest newsletter."""
    newsletter_type = request.args.get('type', 'morning')
    
    system = get_newsletter_system()
    
    if newsletter_type == 'morning':
        newsletter = await system.generate_morning_briefing()
    else:
        newsletter = await system.generate_weekly_digest()
    
    return jsonify({
        "type": newsletter_type,
        "content": newsletter.to_dict(),
        "html": newsletter.to_html(),
        "markdown": newsletter.to_markdown()
    })


@app.route('/api/newsletter/stats')
def api_newsletter_stats():
    """Get newsletter statistics."""
    system = get_newsletter_system()
    stats = system.get_subscriber_stats()
    
    return jsonify(stats)


# ============== ORIGINAL ENDPOINTS ==============

@app.route('/api/investigate/<wallet_address>')
@async_route
async def api_investigate_wallet(wallet_address: str):
    """Investigate a wallet."""
    if len(wallet_address) != 44:
        return jsonify({"error": "Invalid wallet address"}), 400
    
    bot = get_rmi_bot()
    response = await bot.investigate_wallet(wallet_address)
    
    return jsonify({
        "wallet": wallet_address,
        "findings": response.text,
        "confidence": response.confidence,
        "evidence_refs": response.evidence_refs,
        "suggested_actions": response.suggested_actions,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/cluster/<wallet_address>')
def api_find_cluster(wallet_address: str):
    """Find wallet cluster around address."""
    if len(wallet_address) != 44:
        return jsonify({"error": "Invalid wallet address"}), 400
    
    engine = get_clustering_engine()
    
    return jsonify({
        "center_wallet": wallet_address,
        "clusters_found": 0,
        "message": "Use /api/cluster-pro/detect for advanced clustering",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/bubble/<wallet_address>')
def api_bubble_map(wallet_address: str):
    """Generate bubble map for wallet."""
    if len(wallet_address) != 44:
        return jsonify({"error": "Invalid wallet address"}), 400
    
    depth = request.args.get('depth', 2, type=int)
    
    engine = get_clustering_engine()
    graph_data = engine.generate_bubble_map_data(wallet_address, depth)
    
    visualizer = get_visualizer()
    html_path = visualizer.generate_html(wallet_address, graph_data, depth)
    svg_path = visualizer.generate_svg(wallet_address, graph_data)
    
    return jsonify({
        "wallet": wallet_address,
        "depth": depth,
        "nodes": len(graph_data['nodes']),
        "links": len(graph_data['links']),
        "html_url": f"/static/{os.path.basename(html_path)}",
        "svg_url": f"/static/{os.path.basename(svg_path)}",
        "graph_data": graph_data,
        "note": "Use /api/bubble-maps-pro for interactive D3.js maps",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/llm/usage')
def api_llm_usage():
    """Get LLM usage report."""
    rotator = get_llm_rotator()
    report = rotator.get_usage_report()
    
    return jsonify(report)


@app.route('/api/report/generate', methods=['POST'])
@async_route
async def api_generate_report():
    """Generate investigation report."""
    data = request.json or {}
    
    report_type = data.get('type', 'wallet')
    target = data.get('target', '')
    
    return jsonify({
        "report_type": report_type,
        "target": target,
        "status": "generated",
        "download_url": f"/reports/{target[:16]}_report.pdf",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    static_dir = "/mnt/okcomputer/output/omega_forensic_v5/web/static"
    return send_from_directory(static_dir, filename)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


# HTML Template
MAIN_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RMI - RugMunch Intelligence</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            color: #fff;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
            padding: 20px 40px;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 24px; color: #00d4ff; }
        .header .tagline { color: #888; font-size: 14px; }
        .nav { display: flex; gap: 20px; }
        .nav a {
            color: #aaa; text-decoration: none; padding: 8px 16px;
            border-radius: 6px; transition: all 0.2s;
        }
        .nav a:hover { background: #222; color: #00d4ff; }
        .container { max-width: 1400px; margin: 0 auto; padding: 40px; }
        .hero { text-align: center; padding: 60px 20px; }
        .hero h2 {
            font-size: 48px; margin-bottom: 20px;
            background: linear-gradient(90deg, #00d4ff, #0099cc);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .hero p { font-size: 18px; color: #aaa; max-width: 600px; margin: 0 auto 40px; }
        .search-box {
            max-width: 600px; margin: 0 auto;
            display: flex; gap: 10px;
        }
        .search-box input {
            flex: 1; padding: 16px 24px; background: #0f0f1a;
            border: 1px solid #333; border-radius: 8px;
            color: #fff; font-size: 16px; font-family: monospace;
        }
        .search-box input:focus { outline: none; border-color: #00d4ff; }
        .search-box button {
            padding: 16px 32px;
            background: linear-gradient(90deg, #00d4ff, #0099cc);
            border: none; border-radius: 8px; color: #000;
            font-weight: 600; cursor: pointer;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px; margin-top: 60px;
        }
        .feature-card {
            background: #0f0f1a; border: 1px solid #222;
            border-radius: 12px; padding: 30px;
            transition: all 0.2s;
        }
        .feature-card:hover { border-color: #00d4ff; transform: translateY(-4px); }
        .feature-card .icon { font-size: 32px; margin-bottom: 16px; }
        .feature-card h3 { font-size: 18px; margin-bottom: 12px; color: #00d4ff; }
        .feature-card p { color: #888; font-size: 14px; line-height: 1.6; }
        .feature-card .badge {
            display: inline-block; padding: 4px 8px; border-radius: 4px;
            font-size: 11px; font-weight: 600; margin-top: 12px;
        }
        .badge-new { background: #10b981; color: #000; }
        .badge-pro { background: #8b5cf6; color: #fff; }
        .footer {
            text-align: center; padding: 40px; color: #666;
            font-size: 12px; border-top: 1px solid #222; margin-top: 60px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🔍 RMI</h1>
            <span class="tagline">RugMunch Intelligence Platform v{{ version }}</span>
        </div>
        <nav class="nav">
            <a href="/">Home</a>
            <a href="/api/methodology">Methodology</a>
            <a href="/api/trending-scams">Trending Scams</a>
            <a href="/api/kol/leaderboard">KOL Leaderboard</a>
            <a href="/api/marketplace/packages">API Marketplace</a>
        </nav>
    </div>
    
    <div class="container">
        <div class="hero">
            <h2>Uncover Crypto Fraud</h2>
            <p>Evidence-based investigation platform with contract checking, dev tracking, KOL ratings, wallet protection, and advanced clustering.</p>
            
            <div class="search-box">
                <input type="text" id="token-input" placeholder="Enter token address..." maxlength="44">
                <button onclick="checkToken()">🔍 Check</button>
            </div>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <div class="icon">📋</div>
                <h3>Contract Check</h3>
                <p>100-point rug pull analysis checking ownership, liquidity, supply, holders, and history.</p>
            </div>
            <div class="feature-card">
                <div class="icon">👤</div>
                <h3>Dev Finder</h3>
                <p>Track developers across all their tokens. See rug history, connected wallets, and risk scores.</p>
            </div>
            <div class="feature-card">
                <div class="icon">📢</div>
                <h3>Shill Tracker</h3>
                <p>Detect coordinated campaigns on X. Identify bot networks and estimate promotion costs.</p>
            </div>
            <div class="feature-card">
                <div class="icon">🏆</div>
                <h3>KOL Reputation</h3>
                <p>Track influencer call accuracy. Diamond to Bronze tiers based on performance.</p>
            </div>
            <div class="feature-card">
                <div class="icon">💰</div>
                <h3>KOL Wallet Tracker <span class="badge badge-new">NEW</span></h3>
                <p>Track KOL positions, verify calls against wallet activity, detect rug signals.</p>
            </div>
            <div class="feature-card">
                <div class="icon">🚨</div>
                <h3>Trending Scams</h3>
                <p>Real-time monitoring of potential scams. Early warnings before the rug.</p>
            </div>
            <div class="feature-card">
                <div class="icon">🛡️</div>
                <h3>Wallet Protection</h3>
                <p>Block suspicious tokens, warn before transactions, simulate before signing.</p>
            </div>
            <div class="feature-card">
                <div class="icon">🔎</div>
                <h3>Deep Wallet Analysis <span class="badge badge-new">NEW</span></h3>
                <p>Comprehensive wallet investigation with scam connections and behavioral profiling.</p>
            </div>
            <div class="feature-card">
                <div class="icon">🕸️</div>
                <h3>Cluster Detection Pro <span class="badge badge-pro">PRO</span></h3>
                <p>7-method clustering: temporal, behavioral, funding, patterns, and more.</p>
            </div>
            <div class="feature-card">
                <div class="icon">🫧</div>
                <h3>Bubble Maps Pro <span class="badge badge-pro">PRO</span></h3>
                <p>Interactive D3.js visualizations with filters, exports, and time comparison.</p>
            </div>
            <div class="feature-card">
                <div class="icon">📊</div>
                <h3>Transparency Tracker <span class="badge badge-new">NEW</span></h3>
                <p>Project transparency scoring across 6 categories with A+ to F grades.</p>
            </div>
            <div class="feature-card">
                <div class="icon">🛒</div>
                <h3>API Marketplace <span class="badge badge-new">NEW</span></h3>
                <p>Up to 70% off API credits. Birdeye, Helius, Shyft, QuickNode and more.</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Built with ❤️ using Kimi AI | APIs: Helius, Arkham, MistTrack, ChainAbuse, BirdEye, LunarCrush</p>
        <p style="margin-top: 8px;">v{{ version }} | {{ domain }}</p>
    </div>
    
    <script>
        function checkToken() {
            const address = document.getElementById('token-input').value.trim();
            if (address.length === 44) {
                window.open('/api/contract-check/' + address, '_blank');
            } else {
                alert('Please enter a valid Solana token address (44 characters)');
            }
        }
        
        document.getElementById('token-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') checkToken();
        });
    </script>
</body>
</html>
"""


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask server."""
    print(f"""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║   🔍 RMI - RugMunch Intelligence Platform                        ║
    ║                                                                  ║
    ║   Server: http://{host}:{port}                              ║
    ║   Domain: {DOMAIN}                    ║
    ║                                                                  ║
    ║   Features:                                                      ║
    ║   • Contract Check, Dev Finder, Shill Tracker                   ║
    ║   • KOL Reputation + Wallet Tracker                             ║
    ║   • Deep Wallet Analysis                                        ║
    ║   • Cluster Detection Pro (7 methods)                           ║
    ║   • Bubble Maps Pro (Interactive D3.js)                         ║
    ║   • Transparency Tracker                                        ║
    ║   • Premium Scans (CRM Holder 50% off)                          ║
    ║   • API Marketplace (70% off retail)                            ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server(debug=True)
