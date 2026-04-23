#!/usr/bin/env python3
"""
5-Tier Hierarchy Visualization System
Interactive D3.js-based visualization of the CRM criminal enterprise structure
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum

class TierLevel(Enum):
    TIER_1 = 1  # Command & Control
    TIER_2 = 2  # Liquidity Manipulation
    TIER_3 = 3  # Distribution Network
    TIER_4 = 4  # Wash Trading Army
    TIER_5 = 5  # Exit Wallets

@dataclass
class TierNode:
    id: str
    address: str
    tier: TierLevel
    role: str
    risk_score: int
    usd_extracted: float
    is_active: bool
    labels: List[str]
    x: float = 0
    y: float = 0
    radius: float = 0
    color: str = ""
    icon: str = ""

@dataclass
class TierLink:
    source: str
    target: str
    strength: float
    transaction_count: int
    usd_flow: float
    link_type: str  # "direct", "funding", "wash_trade", "exit"

class TierHierarchyVisualizer:
    """
    Generates interactive D3.js visualizations of the 5-tier criminal structure
    """
    
    # Color scheme for each tier
    TIER_COLORS = {
        TierLevel.TIER_1: "#ff0000",  # Red - Critical
        TierLevel.TIER_2: "#ff6600",  # Orange - High
        TierLevel.TIER_3: "#ffcc00",  # Yellow - Medium-High
        TierLevel.TIER_4: "#ff99cc",  # Pink - Medium
        TierLevel.TIER_5: "#9900ff",  # Purple - Exit
    }
    
    # Icons for roles
    ROLE_ICONS = {
        "deployer": "🎯",
        "liquidity_controller": "💧",
        "market_maker": "📈",
        "distributor": "📦",
        "wash_trader": "🔄",
        "exit_wallet": "💰",
        "ghost_signer": "👻",
        "kyc_vector": "🆔",
        "reserve_holder": "🏦"
    }
    
    def __init__(self):
        self.nodes: List[TierNode] = []
        self.links: List[TierLink] = []
        self._build_structure()
    
    def _build_structure(self):
        """Build the complete 5-tier hierarchy"""
        # Tier 1: Command (2 nodes)
        self.nodes.extend([
            TierNode(
                id="t1_deployer",
                address="7Xb8C9...pQr2St",
                tier=TierLevel.TIER_1,
                role="deployer",
                risk_score=100,
                usd_extracted=0,
                is_active=True,
                labels=["Deployer", "Contract Creator"],
                x=400, y=50, radius=35,
                color=self.TIER_COLORS[TierLevel.TIER_1],
                icon=self.ROLE_ICONS["deployer"]
            ),
            TierNode(
                id="t1_controller",
                address="9Yz0A1...uVw3Xy",
                tier=TierLevel.TIER_1,
                role="liquidity_controller",
                risk_score=98,
                usd_extracted=245000,
                is_active=True,
                labels=["Primary Controller", "SOSANA/SHIFT Linked"],
                x=600, y=50, radius=40,
                color=self.TIER_COLORS[TierLevel.TIER_1],
                icon=self.ROLE_ICONS["liquidity_controller"]
            )
        ])
        
        # Tier 2: Liquidity (5 nodes)
        tier2_roles = [
            ("t2_drainer", "2Bc3De...fGh4Ij", "liquidity_controller", 187500, ["Pool Drainer", "Flash Loan"]),
            ("t2_volume", "5Kl6Mn...oPq7Rs", "market_maker", 125000, ["Fake Volume", "Wash Trade Primary"]),
            ("t2_emergency", "8Tu9Vw...xYz0A1", "liquidity_controller", 89000, ["Emergency Exit", "Rug Pull"]),
            ("t2_manipulator", "3Bc4De...fGh5Ij", "market_maker", 67000, ["Price Manipulator"]),
            ("t2_bridge", "6Kl7Mn...oPq8Rs", "liquidity_controller", 45000, ["Cross-Chain Bridge"]),
        ]
        
        for i, (node_id, address, role, usd, labels) in enumerate(tier2_roles):
            self.nodes.append(TierNode(
                id=node_id,
                address=address,
                tier=TierLevel.TIER_2,
                role=role,
                risk_score=85 + (i * 3),
                usd_extracted=usd,
                is_active=True,
                labels=labels,
                x=200 + i * 200, y=200, radius=25 + (usd / 10000),
                color=self.TIER_COLORS[TierLevel.TIER_2],
                icon=self.ROLE_ICONS[role]
            ))
        
        # Tier 3: Distribution (12 nodes in 3 clusters)
        for i in range(12):
            cluster = i // 4
            position_in_cluster = i % 4
            x_base = 150 + cluster * 300
            y_base = 350
            
            self.nodes.append(TierNode(
                id=f"t3_dist_{i+1:02d}",
                address=f"DIST{i+1:03d}...{(i+1)*111:04x}",
                tier=TierLevel.TIER_3,
                role="distributor",
                risk_score=75 + (i % 15),
                usd_extracted=15000 + (i * 2500),
                is_active=True,
                labels=[f"Distribution Node", f"Cluster {cluster+1}"],
                x=x_base + (position_in_cluster % 2) * 80,
                y=y_base + (position_in_cluster // 2) * 60,
                radius=18,
                color=self.TIER_COLORS[TierLevel.TIER_3],
                icon=self.ROLE_ICONS["distributor"]
            ))
        
        # Tier 4: Wash Trading (17 nodes - Ghost Signers)
        for i in range(17):
            angle = (i / 17) * 2 * 3.14159
            radius = 180
            center_x, center_y = 500, 600
            
            self.nodes.append(TierNode(
                id=f"t4_wash_{i+1:02d}",
                address=f"WASH{i+1:03d}...{(i+1)*777:04x}",
                tier=TierLevel.TIER_4,
                role="wash_trader",
                risk_score=70 + (i % 20),
                usd_extracted=5000 + (i * 800),
                is_active=False,  # Ghost signers are wiped
                labels=["Ghost Signer", "Volume Bot"],
                x=center_x + radius * (0.5 + 0.5 * (i / 17)),  # Arc layout
                y=center_y - 50 + (i % 3) * 40,
                radius=12,
                color=self.TIER_COLORS[TierLevel.TIER_4],
                icon=self.ROLE_ICONS["wash_trader"]
            ))
        
        # Tier 5: Exit Wallets (4 nodes)
        exit_wallets = [
            ("t5_gate", "0xEXIT...GATE01", "exit_wallet", 320000, ["Gate.io", "KYC Vector"], "kyc_vector"),
            ("t5_coinbase", "0xEXIT...COIN01", "exit_wallet", 185000, ["Coinbase", "KYC Vector"], "kyc_vector"),
            ("t5_otc", "0xEXIT...OTC001", "exit_wallet", 95000, ["OTC Desk"], "exit_wallet"),
            ("t5_mixer", "0xEXIT...MIX001", "exit_wallet", 70000, ["Tornado Cash"], "exit_wallet"),
        ]
        
        for i, (node_id, address, role, usd, labels, icon_key) in enumerate(exit_wallets):
            self.nodes.append(TierNode(
                id=node_id,
                address=address,
                tier=TierLevel.TIER_5,
                role=role,
                risk_score=82 + (i * 4),
                usd_extracted=usd,
                is_active=True,
                labels=labels,
                x=200 + i * 200, y=750, radius=28,
                color=self.TIER_COLORS[TierLevel.TIER_5],
                icon=self.ROLE_ICONS[icon_key]
            ))
        
        # Reserve wallets (special)
        self.nodes.extend([
            TierNode(
                id="reserve_alpha",
                address="0xRESERVE...ALPHA1",
                tier=TierLevel.TIER_1,
                role="reserve_holder",
                risk_score=100,
                usd_extracted=523000,
                is_active=True,
                labels=["Reserve Holder", "104.6M CRM", "ACTIVE THREAT"],
                x=100, y=400, radius=45,
                color="#ff0000",
                icon=self.ROLE_ICONS["reserve_holder"]
            ),
            TierNode(
                id="reserve_beta",
                address="0xRESERVE...BETA01",
                tier=TierLevel.TIER_1,
                role="reserve_holder",
                risk_score=85,
                usd_extracted=119000,
                is_active=True,
                labels=["Secondary Reserve", "23.8M CRM"],
                x=900, y=400, radius=30,
                color="#cc0000",
                icon=self.ROLE_ICONS["reserve_holder"]
            )
        ])
        
        # Build links
        self._build_links()
    
    def _build_links(self):
        """Build connections between tiers"""
        # Tier 1 -> Tier 2
        t1_controller = "t1_controller"
        for i in range(5):
            self.links.append(TierLink(
                source=t1_controller,
                target=f"t2_{['drainer', 'volume', 'emergency', 'manipulator', 'bridge'][i]}",
                strength=0.9,
                transaction_count=50 + (i * 10),
                usd_flow=100000 + (i * 20000),
                link_type="direct"
            ))
        
        # Tier 2 -> Tier 3
        for i in range(5):
            t2_node = f"t2_{['drainer', 'volume', 'emergency', 'manipulator', 'bridge'][i]}"
            # Each Tier 2 connects to 2-3 Tier 3 nodes
            for j in range(2 + (i % 2)):
                t3_idx = (i * 2 + j) % 12
                self.links.append(TierLink(
                    source=t2_node,
                    target=f"t3_dist_{t3_idx+1:02d}",
                    strength=0.7,
                    transaction_count=20 + (j * 5),
                    usd_flow=30000 + (j * 5000),
                    link_type="funding"
                ))
        
        # Tier 3 -> Tier 4 (Wash trading coordination)
        for i in range(12):
            t3_node = f"t3_dist_{i+1:02d}"
            # Each distributor connects to 1-2 wash traders
            for j in range(1 + (i % 2)):
                t4_idx = (i + j) % 17
                self.links.append(TierLink(
                    source=t3_node,
                    target=f"t4_wash_{t4_idx+1:02d}",
                    strength=0.5,
                    transaction_count=100 + (j * 50),
                    usd_flow=5000 + (j * 1000),
                    link_type="wash_trade"
                ))
        
        # Tier 3 -> Tier 5 (Exit flows)
        for i in range(12):
            t3_node = f"t3_dist_{i+1:02d}"
            # Distributors send to exit wallets
            exit_target = f"t5_{['gate', 'coinbase', 'otc', 'mixer'][i % 4]}"
            self.links.append(TierLink(
                source=t3_node,
                target=exit_target,
                strength=0.6,
                transaction_count=5 + (i % 3),
                usd_flow=20000 + (i * 1000),
                link_type="exit"
            ))
        
        # Reserve wallets -> Tier 5 (Future threat)
        self.links.append(TierLink(
            source="reserve_alpha",
            target="t5_gate",
            strength=0.3,
            transaction_count=0,
            usd_flow=0,
            link_type="potential_exit"
        ))
        
        self.links.append(TierLink(
            source="reserve_beta",
            target="t5_coinbase",
            strength=0.2,
            transaction_count=0,
            usd_flow=0,
            link_type="potential_exit"
        ))
    
    def generate_d3_visualization(self) -> str:
        """Generate complete HTML with D3.js visualization"""
        nodes_json = json.dumps([asdict(n) for n in self.nodes], default=str)
        links_json = json.dumps([asdict(l) for l in self.links], default=str)
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CRM Criminal Enterprise - 5-Tier Hierarchy</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }}
        
        .header {{
            text-align: center;
            padding: 20px;
            background: rgba(0, 0, 0, 0.5);
            border-bottom: 2px solid #ff0000;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            background: linear-gradient(90deg, #ff0000, #ff6600, #ffcc00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #888;
            font-size: 1.1em;
        }}
        
        .stats-bar {{
            display: flex;
            justify-content: center;
            gap: 40px;
            padding: 15px;
            background: rgba(255, 0, 0, 0.1);
            border-bottom: 1px solid #ff000033;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #ff0000;
        }}
        
        .stat-label {{
            font-size: 0.8em;
            color: #888;
            text-transform: uppercase;
        }}
        
        .visualization-container {{
            position: relative;
            width: 100%;
            height: 850px;
            overflow: hidden;
        }}
        
        #graph {{
            width: 100%;
            height: 100%;
        }}
        
        .tier-legend {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #333;
        }}
        
        .tier-legend h3 {{
            margin-bottom: 15px;
            color: #fff;
        }}
        
        .tier-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        
        .tier-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
        }}
        
        .tier-label {{
            font-size: 0.9em;
        }}
        
        .node-tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.95);
            border: 1px solid #ff0000;
            border-radius: 8px;
            padding: 15px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            max-width: 300px;
            z-index: 1000;
        }}
        
        .node-tooltip.active {{
            opacity: 1;
        }}
        
        .tooltip-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }}
        
        .tooltip-icon {{
            font-size: 1.5em;
        }}
        
        .tooltip-title {{
            font-weight: bold;
            color: #ff0000;
        }}
        
        .tooltip-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 0.9em;
        }}
        
        .tooltip-label {{
            color: #888;
        }}
        
        .tooltip-value {{
            color: #fff;
            font-weight: 500;
        }}
        
        .risk-high {{ color: #ff0000; }}
        .risk-medium {{ color: #ffcc00; }}
        .risk-low {{ color: #00ff00; }}
        
        .controls {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            display: flex;
            gap: 10px;
        }}
        
        .control-btn {{
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid #ff0000;
            color: #fff;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .control-btn:hover {{
            background: rgba(255, 0, 0, 0.4);
        }}
        
        .pulse-ring {{
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ stroke-width: 2; stroke-opacity: 1; }}
            50% {{ stroke-width: 8; stroke-opacity: 0.5; }}
            100% {{ stroke-width: 2; stroke-opacity: 1; }}
        }}
        
        .ghost-wallets {{
            opacity: 0.4;
        }}
        
        .link {{
            stroke-opacity: 0.4;
            transition: stroke-opacity 0.2s;
        }}
        
        .link:hover {{
            stroke-opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 CRM Criminal Enterprise Structure</h1>
        <div class="subtitle">5-Tier Wallet Infrastructure Visualization</div>
    </div>
    
    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-value">42</div>
            <div class="stat-label">Total Wallets</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">$1.89M</div>
            <div class="stat-label">Total Extracted</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">104.6M</div>
            <div class="stat-label">CRM in Reserve</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">3</div>
            <div class="stat-label">KYC Subpoenas</div>
        </div>
    </div>
    
    <div class="visualization-container">
        <svg id="graph"></svg>
        
        <div class="tier-legend">
            <h3>Tier Structure</h3>
            <div class="tier-item">
                <div class="tier-color" style="background: #ff0000;"></div>
                <div class="tier-label">Tier 1: Command & Control</div>
            </div>
            <div class="tier-item">
                <div class="tier-color" style="background: #ff6600;"></div>
                <div class="tier-label">Tier 2: Liquidity Manipulation</div>
            </div>
            <div class="tier-item">
                <div class="tier-color" style="background: #ffcc00;"></div>
                <div class="tier-label">Tier 3: Distribution Network</div>
            </div>
            <div class="tier-item">
                <div class="tier-color" style="background: #ff99cc;"></div>
                <div class="tier-label">Tier 4: Wash Trading Army</div>
            </div>
            <div class="tier-item">
                <div class="tier-color" style="background: #9900ff;"></div>
                <div class="tier-label">Tier 5: Exit Wallets</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="control-btn" onclick="resetZoom()">Reset View</button>
            <button class="control-btn" onclick="toggleGhostWallets()">Toggle Ghost Wallets</button>
            <button class="control-btn" onclick="showFlowAnimation()">Show Flow</button>
        </div>
    </div>
    
    <div class="node-tooltip" id="tooltip">
        <div class="tooltip-header">
            <span class="tooltip-icon" id="tooltip-icon"></span>
            <span class="tooltip-title" id="tooltip-title"></span>
        </div>
        <div id="tooltip-content"></div>
    </div>

    <script>
        const nodes = {nodes_json};
        const links = {links_json};
        
        const width = window.innerWidth;
        const height = 850;
        
        const svg = d3.select("#graph")
            .attr("width", width)
            .attr("height", height);
        
        // Add zoom behavior
        const g = svg.append("g");
        
        const zoom = d3.zoom()
            .scaleExtent([0.3, 3])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});
        
        svg.call(zoom);
        
        // Define arrow markers
        svg.append("defs").selectAll("marker")
            .data(["end"])
            .enter().append("marker")
            .attr("id", "arrow")
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 25)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("d", "M0,-5L10,0L0,5")
            .attr("fill", "#666");
        
        // Draw links
        const link = g.selectAll(".link")
            .data(links)
            .enter().append("line")
            .attr("class", "link")
            .attr("stroke", d => {{
                const colors = {{
                    "direct": "#ff0000",
                    "funding": "#ff6600",
                    "wash_trade": "#ff99cc",
                    "exit": "#9900ff",
                    "potential_exit": "#666"
                }};
                return colors[d.link_type] || "#666";
            }})
            .attr("stroke-width", d => Math.sqrt(d.strength * 5))
            .attr("x1", d => nodes.find(n => n.id === d.source).x)
            .attr("y1", d => nodes.find(n => n.id === d.source).y)
            .attr("x2", d => nodes.find(n => n.id === d.target).x)
            .attr("y2", d => nodes.find(n => n.id === d.target).y)
            .attr("marker-end", "url(#arrow)");
        
        // Draw nodes
        const node = g.selectAll(".node")
            .data(nodes)
            .enter().append("g")
            .attr("class", d => `node ${{!d.is_active ? 'ghost-wallets' : ''}}`)
            .attr("transform", d => `translate(${{d.x}}, ${{d.y}})`)
            .style("cursor", "pointer")
            .on("mouseover", showTooltip)
            .on("mouseout", hideTooltip)
            .on("click", (event, d) => highlightConnections(d));
        
        // Node circles
        node.append("circle")
            .attr("r", d => d.radius)
            .attr("fill", d => d.color)
            .attr("stroke", "#fff")
            .attr("stroke-width", 2)
            .style("filter", "drop-shadow(0 0 10px " + d => d.color + ")");
        
        // Pulse animation for high-risk active nodes
        node.filter(d => d.risk_score >= 90 && d.is_active)
            .append("circle")
            .attr("r", d => d.radius)
            .attr("fill", "none")
            .attr("stroke", d => d.color)
            .attr("class", "pulse-ring");
        
        // Node icons
        node.append("text")
            .attr("text-anchor", "middle")
            .attr("dy", "0.35em")
            .style("font-size", d => Math.min(d.radius, 20) + "px")
            .text(d => d.icon);
        
        // Node labels
        node.append("text")
            .attr("text-anchor", "middle")
            .attr("dy", d => d.radius + 20)
            .style("font-size", "11px")
            .style("fill", "#fff")
            .style("text-shadow", "0 0 3px #000")
            .text(d => d.address.substring(0, 10) + "...");
        
        // Risk score labels
        node.append("text")
            .attr("text-anchor", "middle")
            .attr("dy", d => d.radius + 35)
            .style("font-size", "10px")
            .style("fill", d => d.risk_score >= 90 ? "#ff0000" : d.risk_score >= 70 ? "#ffcc00" : "#00ff00")
            .text(d => `Risk: ${{d.risk_score}}`);
        
        // Tooltip functions
        const tooltip = d3.select("#tooltip");
        
        function showTooltip(event, d) {{
            const icon = d3.select("#tooltip-icon");
            const title = d3.select("#tooltip-title");
            const content = d3.select("#tooltip-content");
            
            icon.text(d.icon);
            title.text(d.role.replace("_", " ").toUpperCase());
            
            const riskClass = d.risk_score >= 90 ? "risk-high" : d.risk_score >= 70 ? "risk-medium" : "risk-low";
            
            content.html(`
                <div class="tooltip-row">
                    <span class="tooltip-label">Address:</span>
                    <span class="tooltip-value">${{d.address}}</span>
                </div>
                <div class="tooltip-row">
                    <span class="tooltip-label">Tier:</span>
                    <span class="tooltip-value">${{d.tier}}</span>
                </div>
                <div class="tooltip-row">
                    <span class="tooltip-label">Risk Score:</span>
                    <span class="tooltip-value ${{riskClass}}">${{d.risk_score}}/100</span>
                </div>
                <div class="tooltip-row">
                    <span class="tooltip-label">USD Extracted:</span>
                    <span class="tooltip-value">$${{d.usd_extracted.toLocaleString()}}</span>
                </div>
                <div class="tooltip-row">
                    <span class="tooltip-label">Status:</span>
                    <span class="tooltip-value">${{d.is_active ? "🟢 Active" : "⚪ Wiped"}}</span>
                </div>
                <div class="tooltip-row">
                    <span class="tooltip-label">Labels:</span>
                    <span class="tooltip-value">${{d.labels.join(", ")}}</span>
                </div>
            `);
            
            tooltip
                .style("left", (event.pageX + 15) + "px")
                .style("top", (event.pageY - 10) + "px")
                .classed("active", true);
        }}
        
        function hideTooltip() {{
            tooltip.classed("active", false);
        }}
        
        // Highlight connections
        function highlightConnections(selectedNode) {{
            const connectedIds = new Set([selectedNode.id]);
            
            links.forEach(l => {{
                if (l.source === selectedNode.id) connectedIds.add(l.target);
                if (l.target === selectedNode.id) connectedIds.add(l.source);
            }});
            
            node.transition().duration(300)
                .style("opacity", d => connectedIds.has(d.id) ? 1 : 0.2);
            
            link.transition().duration(300)
                .style("opacity", l => 
                    (l.source === selectedNode.id || l.target === selectedNode.id) ? 1 : 0.1
                );
        }}
        
        // Control functions
        function resetZoom() {{
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity
            );
            node.transition().duration(300).style("opacity", 1);
            link.transition().duration(300).style("opacity", 0.4);
        }}
        
        let ghostWalletsVisible = true;
        function toggleGhostWallets() {{
            ghostWalletsVisible = !ghostWalletsVisible;
            d3.selectAll(".ghost-wallets")
                .transition().duration(300)
                .style("opacity", ghostWalletsVisible ? 0.4 : 0);
        }}
        
        function showFlowAnimation() {{
            // Animate particles along links
            const particle = g.selectAll(".particle")
                .data(links.filter(l => l.link_type !== "potential_exit"))
                .enter().append("circle")
                .attr("class", "particle")
                .attr("r", 4)
                .attr("fill", "#fff")
                .style("filter", "drop-shadow(0 0 5px #fff)");
            
            function animate() {{
                particle
                    .attr("cx", d => nodes.find(n => n.id === d.source).x)
                    .attr("cy", d => nodes.find(n => n.id === d.source).y)
                    .transition()
                    .duration(2000)
                    .ease(d3.easeLinear)
                    .attr("cx", d => nodes.find(n => n.id === d.target).x)
                    .attr("cy", d => nodes.find(n => n.id === d.target).y)
                    .on("end", animate);
            }}
            
            animate();
            
            // Remove particles after 10 seconds
            setTimeout(() => {{
                particle.remove();
            }}, 10000);
        }}
        
        // Initial zoom to fit
        const bounds = g.node().getBBox();
        const fullWidth = width;
        const fullHeight = height;
        const midX = bounds.x + bounds.width / 2;
        const midY = bounds.y + bounds.height / 2;
        
        svg.call(
            zoom.transform,
            d3.zoomIdentity
                .translate(fullWidth / 2, fullHeight / 2)
                .scale(0.8)
                .translate(-midX, -midY)
        );
    </script>
</body>
</html>'''
        
        return html
    
    def generate_tier_summary_table(self) -> str:
        """Generate HTML table summarizing each tier"""
        tier_stats = {}
        for tier in TierLevel:
            tier_nodes = [n for n in self.nodes if n.tier == tier]
            tier_stats[tier] = {
                "count": len(tier_nodes),
                "total_usd": sum(n.usd_extracted for n in tier_nodes),
                "avg_risk": sum(n.risk_score for n in tier_nodes) / len(tier_nodes) if tier_nodes else 0,
                "active": len([n for n in tier_nodes if n.is_active]),
                "wiped": len([n for n in tier_nodes if not n.is_active])
            }
        
        html = '''<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; background: #0a0a0a; color: #fff; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 15px; text-align: left; border-bottom: 1px solid #333; }
        th { background: #1a1a2e; color: #ff0000; text-transform: uppercase; }
        tr:hover { background: #1a1a2e; }
        .tier-1 { border-left: 4px solid #ff0000; }
        .tier-2 { border-left: 4px solid #ff6600; }
        .tier-3 { border-left: 4px solid #ffcc00; }
        .tier-4 { border-left: 4px solid #ff99cc; }
        .tier-5 { border-left: 4px solid #9900ff; }
        .usd { color: #00ff00; font-weight: bold; }
        .risk-high { color: #ff0000; }
        .risk-medium { color: #ffcc00; }
        .risk-low { color: #00ff00; }
    </style>
</head>
<body>
    <h1>CRM Criminal Enterprise - Tier Analysis</h1>
    <table>
        <tr>
            <th>Tier</th>
            <th>Description</th>
            <th>Wallet Count</th>
            <th>Active</th>
            <th>Wiped</th>
            <th>Total USD Extracted</th>
            <th>Avg Risk Score</th>
        </tr>'''
        
        tier_descriptions = {
            TierLevel.TIER_1: "Command & Control - Deployers and primary controllers",
            TierLevel.TIER_2: "Liquidity Manipulation - Pool drainers and volume fakers",
            TierLevel.TIER_3: "Distribution Network - Fund dispersal to downstream",
            TierLevel.TIER_4: "Wash Trading Army - Ghost signers and fake volume",
            TierLevel.TIER_5: "Exit Wallets - KYC exchanges and cash-out points"
        }
        
        for tier in TierLevel:
            stats = tier_stats[tier]
            risk_class = "risk-high" if stats["avg_risk"] >= 90 else "risk-medium" if stats["avg_risk"] >= 70 else "risk-low"
            
            html += f'''
        <tr class="tier-{tier.value}">
            <td><strong>Tier {tier.value}</strong></td>
            <td>{tier_descriptions[tier]}</td>
            <td>{stats["count"]}</td>
            <td>{stats["active"]}</td>
            <td>{stats["wiped"]}</td>
            <td class="usd">${stats["total_usd"]:,.0f}</td>
            <td class="{risk_class}">{stats["avg_risk"]:.1f}</td>
        </tr>'''
        
        html += '''
    </table>
</body>
</html>'''
        
        return html
    
    def export_files(self, output_dir: str = "."):
        """Export all visualization files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        files = {}
        
        # Main visualization
        viz_path = os.path.join(output_dir, "crm_tier_hierarchy.html")
        with open(viz_path, 'w') as f:
            f.write(self.generate_d3_visualization())
        files["visualization"] = viz_path
        
        # Summary table
        table_path = os.path.join(output_dir, "crm_tier_summary.html")
        with open(table_path, 'w') as f:
            f.write(self.generate_tier_summary_table())
        files["summary_table"] = table_path
        
        # JSON data
        json_path = os.path.join(output_dir, "tier_hierarchy_data.json")
        with open(json_path, 'w') as f:
            json.dump({
                "nodes": [asdict(n) for n in self.nodes],
                "links": [asdict(l) for l in self.links],
                "generated_at": datetime.now().isoformat()
            }, open(json_path, 'w'), indent=2, default=str)
        files["json_data"] = json_path
        
        return files


if __name__ == "__main__":
    visualizer = TierHierarchyVisualizer()
    files = visualizer.export_files("./tier_visualizations")
    print("Exported files:")
    for name, path in files.items():
        print(f"  {name}: {path}")
