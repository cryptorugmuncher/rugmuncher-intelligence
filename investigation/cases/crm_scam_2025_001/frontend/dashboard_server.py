#!/usr/bin/env python3
"""
CRM Investigation Dashboard
===========================

Web-based evidence review and case management dashboard.
Provides secure access to case files, evidence, and analysis.
"""

from flask import Flask, render_template, jsonify, request, send_file, abort
from flask_cors import CORS
import json
import sqlite3
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__, 
    template_folder='/root/crm_investigation/frontend/templates',
    static_folder='/root/crm_investigation/frontend/static'
)
CORS(app)

CASE_ROOT = Path("/root/crm_investigation")
DB_PATH = CASE_ROOT / "evidence/blockchain_analysis.db"

# ==================== ROUTES ====================

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/case/info')
def case_info():
    """Get case metadata"""
    case_file = CASE_ROOT / "case_index.json"
    if case_file.exists():
        with open(case_file) as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Case file not found"}), 404

@app.route('/api/wallets')
def get_wallets():
    """Get all tracked wallets"""
    if not DB_PATH.exists():
        return jsonify({"wallets": []})
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM wallets ORDER BY risk_score DESC")
    rows = c.fetchall()
    conn.close()
    
    wallets = [dict(row) for row in rows]
    return jsonify({"wallets": wallets, "count": len(wallets)})

@app.route('/api/wallet/<address>')
def get_wallet_details(address):
    """Get details for specific wallet"""
    if not DB_PATH.exists():
        return jsonify({"error": "Database not found"}), 404
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM wallets WHERE address = ?", (address,))
    wallet = c.fetchone()
    
    c.execute("SELECT * FROM transactions WHERE from_wallet = ? OR to_wallet = ? ORDER BY block_time DESC",
              (address, address))
    transactions = c.fetchall()
    
    conn.close()
    
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404
    
    return jsonify({
        "wallet": dict(wallet),
        "transactions": [dict(tx) for tx in transactions]
    })

@app.route('/api/transactions')
def get_transactions():
    """Get suspicious transactions"""
    if not DB_PATH.exists():
        return jsonify({"transactions": []})
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    limit = request.args.get('limit', 100, type=int)
    min_suspicion = request.args.get('suspicion', 0.5, type=float)
    
    c.execute("""
        SELECT * FROM transactions 
        WHERE suspicious_score >= ?
        ORDER BY suspicious_score DESC, block_time DESC
        LIMIT ?
    """, (min_suspicion, limit))
    
    rows = c.fetchall()
    conn.close()
    
    return jsonify({
        "transactions": [dict(row) for row in rows],
        "count": len(rows)
    })

@app.route('/api/graph')
def get_relationship_graph():
    """Get wallet relationship graph"""
    graph_file = CASE_ROOT / "evidence/wallet_relationship_graph.json"
    if graph_file.exists():
        with open(graph_file) as f:
            return jsonify(json.load(f))
    return jsonify({"nodes": [], "edges": [], "metadata": {}})

@app.route('/api/evidence/list')
def list_evidence():
    """List all evidence files"""
    evidence_dir = CASE_ROOT / "evidence"
    evidence = {
        "blockchain_data": [],
        "communications": [],
        "forensic_reports": [],
        "photos_screenshots": []
    }
    
    for category in evidence.keys():
        cat_dir = evidence_dir / category
        if cat_dir.exists():
            for f in sorted(cat_dir.glob("*")):
                if f.is_file():
                    stat = f.stat()
                    evidence[category].append({
                        "name": f.name,
                        "path": str(f.relative_to(CASE_ROOT)),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
    
    return jsonify(evidence)

@app.route('/api/evidence/file/<path:filepath>')
def get_evidence_file(filepath):
    """Get specific evidence file"""
    # Security: ensure path doesn't escape evidence directory
    safe_path = (CASE_ROOT / filepath).resolve()
    if not str(safe_path).startswith(str(CASE_ROOT)):
        abort(403)
    
    if safe_path.exists():
        return send_file(safe_path)
    abort(404)

@app.route('/api/timeline')
def get_timeline():
    """Get case timeline"""
    case_file = CASE_ROOT / "case_index.json"
    if case_file.exists():
        with open(case_file) as f:
            data = json.load(f)
            return jsonify({"timeline": data.get("timeline", [])})
    return jsonify({"timeline": []})

@app.route('/api/stats')
def get_stats():
    """Get case statistics"""
    stats = {
        "wallets": {"total": 0, "suspect": 0, "victim": 0},
        "transactions": {"total": 0, "suspicious": 0},
        "financial": {"total_usd": 886597, "victim_count": 970}
    }
    
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*), classification FROM wallets GROUP BY classification")
        for count, classification in c.fetchall():
            stats["wallets"][classification] = count
            stats["wallets"]["total"] += count
        
        c.execute("SELECT COUNT(*), SUM(CASE WHEN suspicious_score > 0.5 THEN 1 ELSE 0 END) FROM transactions")
        result = c.fetchone()
        if result:
            stats["transactions"]["total"] = result[0] or 0
            stats["transactions"]["suspicious"] = result[1] or 0
        
        conn.close()
    
    return jsonify(stats)

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "case_loaded": (CASE_ROOT / "case_index.json").exists(),
        "database_exists": DB_PATH.exists(),
        "timestamp": datetime.now().isoformat()
    })

# ==================== TEMPLATE ====================

def create_templates():
    """Create HTML templates if they don't exist"""
    template_dir = CASE_ROOT / "frontend/templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CRM Investigation Dashboard | CRM-SCAM-2025-001</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            line-height: 1.6;
        }
        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 20px 40px;
            border-bottom: 3px solid #e94560;
        }
        .header h1 {
            color: #fff;
            font-size: 24px;
            margin-bottom: 5px;
        }
        .header .case-id {
            color: #e94560;
            font-family: monospace;
            font-size: 14px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 40px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #1a1a2e;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #2a2a4a;
        }
        .card h3 {
            color: #e94560;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 15px;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #fff;
        }
        .stat-label {
            color: #888;
            font-size: 14px;
        }
        .tier-structure {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin-top: 20px;
        }
        .tier-box {
            background: #0f0f1a;
            border: 1px solid #2a2a4a;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        .tier-box.active {
            border-color: #e94560;
            background: #1a0f1a;
        }
        .tier-box h4 {
            color: #e94560;
            font-size: 12px;
            margin-bottom: 8px;
        }
        .wallet-addr {
            font-family: monospace;
            font-size: 10px;
            color: #888;
            word-break: break-all;
        }
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 1px solid #2a2a4a;
            padding-bottom: 15px;
        }
        .nav-tab {
            background: transparent;
            border: 1px solid #2a2a4a;
            color: #888;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .nav-tab:hover, .nav-tab.active {
            background: #e94560;
            border-color: #e94560;
            color: #fff;
        }
        .section {
            display: none;
        }
        .section.active {
            display: block;
        }
        .wallet-list {
            background: #0f0f1a;
            border-radius: 8px;
            overflow: hidden;
        }
        .wallet-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            border-bottom: 1px solid #1a1a2e;
        }
        .wallet-item:last-child {
            border-bottom: none;
        }
        .wallet-item:hover {
            background: #1a1a2e;
        }
        .risk-high { color: #e94560; }
        .risk-medium { color: #f39c12; }
        .risk-low { color: #27ae60; }
        .timeline {
            position: relative;
            padding-left: 30px;
        }
        .timeline::before {
            content: '';
            position: absolute;
            left: 8px;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #2a2a4a;
        }
        .timeline-item {
            position: relative;
            margin-bottom: 25px;
            padding-left: 20px;
        }
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -26px;
            top: 5px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #e94560;
            border: 2px solid #0a0a0a;
        }
        .timeline-date {
            color: #e94560;
            font-family: monospace;
            font-size: 12px;
        }
        .timeline-event {
            color: #fff;
            font-weight: 500;
            margin: 5px 0;
        }
        .timeline-details {
            color: #888;
            font-size: 14px;
        }
        .footer {
            text-align: center;
            padding: 40px;
            color: #555;
            font-size: 12px;
            border-top: 1px solid #1a1a2e;
            margin-top: 60px;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .error {
            background: #1a0f1a;
            border: 1px solid #e94560;
            color: #e94560;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 CRM Investigation Dashboard</h1>
        <div class="case-id">CASE ID: CRM-SCAM-2025-001 | Multi-Jurisdictional Criminal Enterprise</div>
    </div>
    
    <div class="container">
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showSection('overview')">Overview</button>
            <button class="nav-tab" onclick="showSection('wallets')">Wallets</button>
            <button class="nav-tab" onclick="showSection('timeline')">Timeline</button>
            <button class="nav-tab" onclick="showSection('evidence')">Evidence</button>
            <button class="nav-tab" onclick="showSection('graph')">Graph</button>
        </div>
        
        <div id="overview" class="section active">
            <div class="grid">
                <div class="card">
                    <h3>💰 Financial Impact</h3>
                    <div class="stat-value" id="financial-impact">$886,597+</div>
                    <div class="stat-label">Extracted via pump-and-dump</div>
                </div>
                <div class="card">
                    <h3>👥 Victims</h3>
                    <div class="stat-value" id="victim-count">970+</div>
                    <div class="stat-label">Confirmed victim wallets</div>
                </div>
                <div class="card">
                    <h3>⚠️ Classification</h3>
                    <div class="stat-value" style="font-size: 18px;">RICO-Eligible</div>
                    <div class="stat-label">5-tier criminal hierarchy</div>
                </div>
                <div class="card">
                    <h3>🚩 Status</h3>
                    <div class="stat-value" style="color: #e94560;">ACTIVE</div>
                    <div class="stat-label">Investigation ongoing</div>
                </div>
            </div>
            
            <div class="card">
                <h3>🏗️ Criminal Enterprise Structure</h3>
                <div class="tier-structure">
                    <div class="tier-box active">
                        <h4>TIER 1: ROOT</h4>
                        <div class="wallet-addr">AFXigaYuRK...ztUGb6</div>
                        <div style="color: #888; font-size: 11px; margin-top: 5px;">Master routing</div>
                    </div>
                    <div class="tier-box active">
                        <h4>TIER 2: BRIDGE</h4>
                        <div class="wallet-addr">BMq4XUa3rJ...ADVkX5</div>
                        <div style="color: #888; font-size: 11px; margin-top: 5px;">SHIFT→CRM</div>
                    </div>
                    <div class="tier-box active">
                        <h4>TIER 3: COORD</h4>
                        <div class="wallet-addr">HxyXAE1PHQ...TKeVfi</div>
                        <div style="color: #888; font-size: 11px; margin-top: 5px;">Transaction coord</div>
                    </div>
                    <div class="tier-box active">
                        <h4>TIER 4: DISTRO</h4>
                        <div class="wallet-addr">8eVZa7bEBn...UeuwQj</div>
                        <div style="color: #888; font-size: 11px; margin-top: 5px;">Load execution</div>
                    </div>
                    <div class="tier-box active">
                        <h4>TIER 5: EXEC</h4>
                        <div class="wallet-addr">7abBmGf4HN...CySvyL</div>
                        <div style="color: #888; font-size: 11px; margin-top: 5px;">Victim/compromised</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="wallets" class="section">
            <div class="card">
                <h3>📊 Wallet Analysis</h3>
                <div class="wallet-list" id="wallet-list">
                    <div class="loading">Loading wallet data...</div>
                </div>
            </div>
        </div>
        
        <div id="timeline" class="section">
            <div class="card">
                <h3>📅 Investigation Timeline</h3>
                <div class="timeline" id="timeline-content">
                    <div class="loading">Loading timeline...</div>
                </div>
            </div>
        </div>
        
        <div id="evidence" class="section">
            <div class="card">
                <h3>📁 Evidence Files</h3>
                <div id="evidence-list">
                    <div class="loading">Loading evidence...</div>
                </div>
            </div>
        </div>
        
        <div id="graph" class="section">
            <div class="card">
                <h3>🕸️ Wallet Relationship Graph</h3>
                <div id="graph-container" style="height: 500px; background: #0f0f1a; border-radius: 8px;">
                    <div class="loading">Graph visualization would load here</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            CRM Investigation Framework | Case CRM-SCAM-2025-001<br>
            For authorized law enforcement use only
        </div>
    </div>
    
    <script>
        // Section navigation
        function showSection(sectionId) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.getElementById(sectionId).classList.add('active');
            event.target.classList.add('active');
            
            // Load data if needed
            if (sectionId === 'wallets') loadWallets();
            if (sectionId === 'timeline') loadTimeline();
            if (sectionId === 'evidence') loadEvidence();
        }
        
        // Load wallet data
        async function loadWallets() {
            try {
                const response = await fetch('/api/wallets');
                const data = await response.json();
                
                const list = document.getElementById('wallet-list');
                if (data.wallets.length === 0) {
                    list.innerHTML = '<div class="error">No wallet data in database. Run blockchain analyzer first.</div>';
                    return;
                }
                
                list.innerHTML = data.wallets.map(w => `
                    <div class="wallet-item">
                        <div>
                            <div style="font-family: monospace; color: #fff;">${w.address.substring(0, 20)}...</div>
                            <div style="font-size: 12px; color: #666;">Tier ${w.tier} | ${w.classification}</div>
                        </div>
                        <div style="text-align: right;">
                            <div class="risk-${w.risk_score > 0.8 ? 'high' : w.risk_score > 0.5 ? 'medium' : 'low'}">
                                Risk: ${(w.risk_score * 100).toFixed(0)}%
                            </div>
                            <div style="font-size: 12px; color: #666;">${w.crm_balance?.toLocaleString()} CRM</div>
                        </div>
                    </div>
                `).join('');
            } catch (e) {
                document.getElementById('wallet-list').innerHTML = 
                    '<div class="error">Error loading wallets: ' + e.message + '</div>';
            }
        }
        
        // Load timeline
        async function loadTimeline() {
            try {
                const response = await fetch('/api/timeline');
                const data = await response.json();
                
                const container = document.getElementById('timeline-content');
                container.innerHTML = data.timeline.map(t => `
                    <div class="timeline-item">
                        <div class="timeline-date">${t.date}</div>
                        <div class="timeline-event">${t.event}</div>
                        <div class="timeline-details">${t.details}</div>
                        ${t.significance ? `<div style="color: #e94560; font-size: 12px; margin-top: 5px;">★ ${t.significance}</div>` : ''}
                    </div>
                `).join('');
            } catch (e) {
                document.getElementById('timeline-content').innerHTML = 
                    '<div class="error">Error loading timeline: ' + e.message + '</div>';
            }
        }
        
        // Load evidence
        async function loadEvidence() {
            document.getElementById('evidence-list').innerHTML = 
                '<div style="padding: 20px; color: #666;">Evidence browser would load here. Files are organized in:<br>' +
                '• evidence/blockchain_data/<br>' +
                '• evidence/communications/<br>' +
                '• evidence/forensic_reports/</div>';
        }
        
        // Load stats on page load
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                document.getElementById('victim-count').textContent = data.financial.victim_count + '+';
            } catch (e) {
                console.error('Failed to load stats:', e);
            }
        }
        
        loadStats();
    </script>
</body>
</html>'''
    
    template_file = template_dir / "dashboard.html"
    if not template_file.exists():
        with open(template_file, 'w') as f:
            f.write(dashboard_html)
        print(f"Created dashboard template: {template_file}")

# ==================== MAIN ====================

if __name__ == '__main__':
    create_templates()
    
    print("=" * 60)
    print("🔍 CRM Investigation Dashboard Server")
    print("=" * 60)
    print(f"Case: CRM-SCAM-2025-001")
    print(f"Database: {DB_PATH}")
    print("=" * 60)
    print("Starting server on http://0.0.0.0:8091")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8091, debug=False)
