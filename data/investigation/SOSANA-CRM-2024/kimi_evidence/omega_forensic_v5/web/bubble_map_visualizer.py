"""
Bubble Map Visualizer - Interactive Wallet Association Maps
===========================================================
Generates interactive D3.js bubble maps for wallet relationships.
Actually useful - finds connections based on real on-chain logic.
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


# HTML template for interactive bubble map
BUBBLE_MAP_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RMI Bubble Map - {center_wallet_short}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #fff;
            overflow: hidden;
        }}
        
        #header {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            z-index: 1000;
            border-bottom: 1px solid #333;
        }}
        
        #header h1 {{
            font-size: 18px;
            font-weight: 600;
            color: #00d4ff;
        }}
        
        #header .wallet-id {{
            font-family: monospace;
            font-size: 12px;
            color: #888;
        }}
        
        #controls {{
            position: fixed;
            top: 60px;
            left: 0;
            width: 280px;
            bottom: 0;
            background: #0f0f1a;
            padding: 20px;
            overflow-y: auto;
            border-right: 1px solid #222;
        }}
        
        .control-group {{
            margin-bottom: 20px;
        }}
        
        .control-group label {{
            display: block;
            font-size: 12px;
            color: #888;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .control-group input[type="range"] {{
            width: 100%;
            height: 6px;
            background: #222;
            border-radius: 3px;
            outline: none;
            -webkit-appearance: none;
        }}
        
        .control-group input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 16px;
            height: 16px;
            background: #00d4ff;
            border-radius: 50%;
            cursor: pointer;
        }}
        
        .control-group button {{
            width: 100%;
            padding: 10px;
            background: linear-gradient(90deg, #00d4ff, #0099cc);
            border: none;
            border-radius: 6px;
            color: #000;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
        }}
        
        .control-group button:hover {{
            opacity: 0.9;
        }}
        
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
        }}
        
        .legend-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        
        #graph-container {{
            position: fixed;
            top: 60px;
            left: 280px;
            right: 0;
            bottom: 0;
        }}
        
        #tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #333;
            border-radius: 8px;
            padding: 12px;
            font-size: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 1001;
            max-width: 300px;
        }}
        
        #tooltip .wallet-address {{
            font-family: monospace;
            color: #00d4ff;
            margin-bottom: 8px;
            word-break: break-all;
        }}
        
        #tooltip .stat {{
            display: flex;
            justify-content: space-between;
            margin: 4px 0;
        }}
        
        #tooltip .stat-label {{
            color: #888;
        }}
        
        #tooltip .stat-value {{
            color: #fff;
            font-weight: 500;
        }}
        
        #info-panel {{
            position: fixed;
            top: 60px;
            right: -400px;
            width: 400px;
            bottom: 0;
            background: #0f0f1a;
            padding: 20px;
            overflow-y: auto;
            border-left: 1px solid #222;
            transition: right 0.3s ease;
            z-index: 999;
        }}
        
        #info-panel.open {{
            right: 0;
        }}
        
        #info-panel h2 {{
            font-size: 16px;
            margin-bottom: 16px;
            color: #00d4ff;
        }}
        
        .node {{
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .node:hover {{
            stroke: #fff;
            stroke-width: 3px;
        }}
        
        .link {{
            stroke-opacity: 0.6;
            transition: all 0.2s;
        }}
        
        .link:hover {{
            stroke-opacity: 1;
            stroke: #fff;
        }}
        
        .node-label {{
            font-size: 10px;
            fill: #aaa;
            pointer-events: none;
            text-shadow: 0 1px 2px rgba(0,0,0,0.8);
        }}
        
        #stats-bar {{
            position: fixed;
            bottom: 0;
            left: 280px;
            right: 0;
            height: 40px;
            background: #0a0a0f;
            border-top: 1px solid #222;
            display: flex;
            align-items: center;
            padding: 0 20px;
            gap: 30px;
            font-size: 12px;
        }}
        
        #stats-bar .stat {{
            display: flex;
            gap: 8px;
        }}
        
        #stats-bar .stat-value {{
            color: #00d4ff;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div id="header">
        <h1>🔍 RMI Bubble Map</h1>
        <span class="wallet-id">{center_wallet}</span>
    </div>
    
    <div id="controls">
        <div class="control-group">
            <label>Connection Depth</label>
            <input type="range" id="depth-slider" min="1" max="4" value="{depth}" />
            <span id="depth-value">{depth}</span>
        </div>
        
        <div class="control-group">
            <label>Min Connection Strength</label>
            <input type="range" id="strength-slider" min="0" max="100" value="30" />
            <span id="strength-value">0.30</span>
        </div>
        
        <div class="control-group">
            <label>Node Size</label>
            <input type="range" id="size-slider" min="50" max="200" value="100" />
        </div>
        
        <div class="control-group">
            <button id="regenerate-btn">Regenerate Map</button>
        </div>
        
        <div class="control-group">
            <button id="export-btn">Export as PNG</button>
        </div>
        
        <div class="control-group">
            <label>Wallet Types</label>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-dot" style="background: #ff6b6b;"></div>
                    <span>Center</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #ff0000;"></div>
                    <span>Scammer</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #4dabf7;"></div>
                    <span>Exchange</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #69db7c;"></div>
                    <span>Wallet</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #888;"></div>
                    <span>Unknown</span>
                </div>
            </div>
        </div>
        
        <div class="control-group">
            <label>Connection Strength</label>
            <div class="legend">
                <div class="legend-item">
                    <div style="width: 30px; height: 3px; background: #00d4ff;"></div>
                    <span>Strong</span>
                </div>
                <div class="legend-item">
                    <div style="width: 30px; height: 1px; background: #666;"></div>
                    <span>Weak</span>
                </div>
            </div>
        </div>
    </div>
    
    <div id="graph-container"></div>
    
    <div id="tooltip"></div>
    
    <div id="info-panel">
        <h2>Wallet Details</h2>
        <div id="wallet-details"></div>
    </div>
    
    <div id="stats-bar">
        <div class="stat">
            <span>Wallets:</span>
            <span class="stat-value" id="wallet-count">0</span>
        </div>
        <div class="stat">
            <span>Connections:</span>
            <span class="stat-value" id="connection-count">0</span>
        </div>
        <div class="stat">
            <span>Clusters:</span>
            <span class="stat-value" id="cluster-count">0</span>
        </div>
    </div>
    
    <script>
        // Graph data
        const graphData = {graph_data_json};
        
        // Setup
        const container = d3.select("#graph-container");
        const width = container.node().clientWidth;
        const height = container.node().clientHeight;
        
        const svg = container.append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height]);
        
        // Add zoom behavior
        const g = svg.append("g");
        
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});
        
        svg.call(zoom);
        
        // Force simulation
        let simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(d => d.size + 10));
        
        // Draw links
        const link = g.append("g")
            .selectAll("line")
            .data(graphData.links)
            .join("line")
            .attr("class", "link")
            .attr("stroke", "#00d4ff")
            .attr("stroke-width", d => Math.max(1, d.strength * 5))
            .attr("stroke-opacity", 0.6);
        
        // Draw nodes
        const node = g.append("g")
            .selectAll("circle")
            .data(graphData.nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", d => d.size)
            .attr("fill", d => d.color)
            .attr("stroke", "#222")
            .attr("stroke-width", 2)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        // Add labels to larger nodes
        const labels = g.append("g")
            .selectAll("text")
            .data(graphData.nodes.filter(d => d.size > 20))
            .join("text")
            .attr("class", "node-label")
            .attr("text-anchor", "middle")
            .attr("dy", ".35em")
            .text(d => d.label);
        
        // Tooltip
        const tooltip = d3.select("#tooltip");
        
        node.on("mouseover", function(event, d) {{
            tooltip.style("opacity", 1)
                .html(`
                    <div class="wallet-address">${d.id}</div>
                    <div class="stat">
                        <span class="stat-label">Type:</span>
                        <span class="stat-value">${d.type}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Volume:</span>
                        <span class="stat-value">${d.volume.toLocaleString()} SOL</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Transactions:</span>
                        <span class="stat-value">${d.transactions}</span>
                    </div>
                `)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px");
        }})
        .on("mouseout", function() {{
            tooltip.style("opacity", 0);
        }})
        .on("click", function(event, d) {{
            showWalletDetails(d);
        }});
        
        // Update positions
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            labels
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});
        
        // Drag functions
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // Show wallet details
        function showWalletDetails(d) {{
            const panel = document.getElementById("info-panel");
            const details = document.getElementById("wallet-details");
            
            details.innerHTML = `
                <div style="margin-bottom: 20px;">
                    <label style="color: #888; font-size: 11px; text-transform: uppercase;">Address</label>
                    <div style="font-family: monospace; font-size: 12px; word-break: break-all; color: #00d4ff; margin-top: 4px;">
                        ${d.id}
                    </div>
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="color: #888; font-size: 11px; text-transform: uppercase;">Type</label>
                    <div style="margin-top: 4px; text-transform: capitalize;">${d.type}</div>
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="color: #888; font-size: 11px; text-transform: uppercase;">Transaction Volume</label>
                    <div style="margin-top: 4px; font-size: 18px; font-weight: 600;">
                        ${d.volume.toLocaleString()} SOL
                    </div>
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="color: #888; font-size: 11px; text-transform: uppercase;">Total Transactions</label>
                    <div style="margin-top: 4px; font-size: 18px; font-weight: 600;">
                        ${d.transactions.toLocaleString()}
                    </div>
                </div>
                <div style="margin-bottom: 20px;">
                    <button onclick="investigateWallet('${d.id}')" style="width: 100%; padding: 12px; background: #00d4ff; border: none; border-radius: 6px; color: #000; font-weight: 600; cursor: pointer;">
                        Investigate This Wallet
                    </button>
                </div>
                <div style="margin-bottom: 20px;">
                    <button onclick="centerOnWallet('${d.id}')" style="width: 100%; padding: 12px; background: #333; border: none; border-radius: 6px; color: #fff; font-weight: 600; cursor: pointer;">
                        Center Map Here
                    </button>
                </div>
            `;
            
            panel.classList.add("open");
        }}
        
        function investigateWallet(address) {{
            window.open(`/investigate/${address}`, '_blank');
        }}
        
        function centerOnWallet(address) {{
            window.location.href = `/bubble/${address}`;
        }}
        
        // Update stats
        document.getElementById("wallet-count").textContent = graphData.nodes.length;
        document.getElementById("connection-count").textContent = graphData.links.length;
        
        // Count clusters (simple connected components)
        const clusters = findClusters(graphData);
        document.getElementById("cluster-count").textContent = clusters;
        
        function findClusters(data) {{
            const visited = new Set();
            let clusters = 0;
            
            const adj = {{}};
            data.nodes.forEach(n => adj[n.id] = new Set());
            data.links.forEach(l => {{
                adj[l.source.id || l.source].add(l.target.id || l.target);
                adj[l.target.id || l.target].add(l.source.id || l.source);
            }});
            
            data.nodes.forEach(n => {{
                if (!visited.has(n.id)) {{
                    clusters++;
                    const stack = [n.id];
                    while (stack.length) {{
                        const curr = stack.pop();
                        if (!visited.has(curr)) {{
                            visited.add(curr);
                            adj[curr].forEach(neighbor => {{
                                if (!visited.has(neighbor)) stack.push(neighbor);
                            }});
                        }}
                    }}
                }}
            }});
            
            return clusters;
        }}
        
        // Controls
        document.getElementById("depth-slider").addEventListener("input", function() {{
            document.getElementById("depth-value").textContent = this.value;
        }});
        
        document.getElementById("strength-slider").addEventListener("input", function() {{
            document.getElementById("strength-value").textContent = (this.value / 100).toFixed(2);
        }});
        
        document.getElementById("regenerate-btn").addEventListener("click", function() {{
            const depth = document.getElementById("depth-slider").value;
            const strength = document.getElementById("strength-slider").value / 100;
            window.location.href = `/bubble/{center_wallet}?depth=${depth}&min_strength=${strength}`;
        }});
        
        document.getElementById("export-btn").addEventListener("click", function() {{
            const svgElement = document.querySelector("svg");
            const svgData = new XMLSerializer().serializeToString(svgElement);
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");
            const img = new Image();
            
            canvas.width = width;
            canvas.height = height;
            
            img.onload = function() {{
                ctx.fillStyle = "#0a0a0f";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0);
                
                const link = document.createElement("a");
                link.download = `bubble-map-{center_wallet_short}.png`;
                link.href = canvas.toDataURL("image/png");
                link.click();
            }};
            
            img.src = "data:image/svg+xml;base64," + btoa(svgData);
        }});
    </script>
</body>
</html>
"""


class BubbleMapVisualizer:
    """
    Generates interactive bubble map visualizations.
    """
    
    def __init__(self, output_dir: str = "/mnt/okcomputer/output/omega_forensic_v5/web/static"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_html(
        self, 
        center_wallet: str, 
        graph_data: Dict,
        depth: int = 2
    ) -> str:
        """
        Generate interactive HTML bubble map.
        
        Args:
            center_wallet: The center wallet address
            graph_data: Bubble map data from clustering engine
            depth: Connection depth
            
        Returns:
            Path to generated HTML file
        """
        # Prepare data
        graph_json = json.dumps(graph_data)
        
        # Fill template
        html = BUBBLE_MAP_HTML.format(
            center_wallet=center_wallet,
            center_wallet_short=center_wallet[:8],
            depth=depth,
            graph_data_json=graph_json
        )
        
        # Save file
        filename = f"bubble_map_{center_wallet[:16]}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(html)
        
        return filepath
    
    def generate_svg(
        self, 
        center_wallet: str, 
        graph_data: Dict,
        width: int = 1200,
        height: int = 800
    ) -> str:
        """
        Generate static SVG bubble map.
        
        Returns:
            Path to generated SVG file
        """
        import xml.etree.ElementTree as ET
        
        # Create SVG root
        svg = ET.Element('svg')
        svg.set('width', str(width))
        svg.set('height', str(height))
        svg.set('viewBox', f'0 0 {width} {height}')
        svg.set('xmlns', 'http://www.w3.org/2000/svg')
        
        # Background
        bg = ET.SubElement(svg, 'rect')
        bg.set('width', '100%')
        bg.set('height', '100%')
        bg.set('fill', '#0a0a0f')
        
        # Title
        title = ET.SubElement(svg, 'text')
        title.set('x', '20')
        title.set('y', '30')
        title.set('fill', '#00d4ff')
        title.set('font-family', 'sans-serif')
        title.set('font-size', '16')
        title.set('font-weight', 'bold')
        title.text = f"RMI Bubble Map - {center_wallet[:16]}..."
        
        # Simple circle packing layout
        nodes = graph_data.get('nodes', [])
        links = graph_data.get('links', [])
        
        # Position nodes in a circle around center
        center_x, center_y = width // 2, height // 2
        
        node_positions = {}
        
        # Center node
        for node in nodes:
            if node['type'] == 'center':
                node_positions[node['id']] = (center_x, center_y)
                break
        
        # Position other nodes in concentric circles by connection strength
        other_nodes = [n for n in nodes if n['type'] != 'center']
        
        if other_nodes:
            angle_step = 2 * 3.14159 / len(other_nodes)
            radius = min(width, height) * 0.35
            
            for i, node in enumerate(other_nodes):
                angle = i * angle_step
                x = center_x + radius * (0.5 + 0.5 * (i % 2)) * (1 if i % 2 == 0 else -1)
                y = center_y + radius * (0.5 + 0.5 * ((i + 1) % 2)) * (1 if (i + 1) % 2 == 0 else -1)
                node_positions[node['id']] = (x, y)
        
        # Draw links
        for link in links:
            source = link.get('source', '')
            target = link.get('target', '')
            
            if source in node_positions and target in node_positions:
                x1, y1 = node_positions[source]
                x2, y2 = node_positions[target]
                
                line = ET.SubElement(svg, 'line')
                line.set('x1', str(x1))
                line.set('y1', str(y1))
                line.set('x2', str(x2))
                line.set('y2', str(y2))
                line.set('stroke', '#00d4ff')
                line.set('stroke-width', str(max(1, link.get('strength', 0.5) * 3)))
                line.set('stroke-opacity', '0.6')
        
        # Draw nodes
        for node in nodes:
            if node['id'] in node_positions:
                x, y = node_positions[node['id']]
                
                circle = ET.SubElement(svg, 'circle')
                circle.set('cx', str(x))
                circle.set('cy', str(y))
                circle.set('r', str(node.get('size', 15)))
                circle.set('fill', node.get('color', '#69db7c'))
                circle.set('stroke', '#222')
                circle.set('stroke-width', '2')
                
                # Label
                label = ET.SubElement(svg, 'text')
                label.set('x', str(x))
                label.set('y', str(y + node.get('size', 15) + 15))
                label.set('text-anchor', 'middle')
                label.set('fill', '#aaa')
                label.set('font-family', 'sans-serif')
                label.set('font-size', '10')
                label.text = node.get('label', node['id'][:8])
        
        # Legend
        legend_y = height - 100
        legend_items = [
            ('#ff6b6b', 'Center'),
            ('#ff0000', 'Scammer'),
            ('#4dabf7', 'Exchange'),
            ('#69db7c', 'Wallet'),
        ]
        
        for i, (color, label) in enumerate(legend_items):
            y = legend_y + i * 20
            
            dot = ET.SubElement(svg, 'circle')
            dot.set('cx', '30')
            dot.set('cy', str(y))
            dot.set('r', '6')
            dot.set('fill', color)
            
            text = ET.SubElement(svg, 'text')
            text.set('x', '45')
            text.set('y', str(y + 4))
            text.set('fill', '#888')
            text.set('font-family', 'sans-serif')
            text.set('font-size', '11')
            text.text = label
        
        # Stats
        stats_text = ET.SubElement(svg, 'text')
        stats_text.set('x', '20')
        stats_text.set('y', str(height - 20))
        stats_text.set('fill', '#888')
        stats_text.set('font-family', 'sans-serif')
        stats_text.set('font-size', '11')
        stats_text.text = f"Wallets: {len(nodes)} | Connections: {len(links)} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Save
        filename = f"bubble_map_{center_wallet[:16]}.svg"
        filepath = os.path.join(self.output_dir, filename)
        
        tree = ET.ElementTree(svg)
        tree.write(filepath)
        
        return filepath


# Global instance
_visualizer = None

def get_visualizer() -> BubbleMapVisualizer:
    """Get global visualizer instance."""
    global _visualizer
    if _visualizer is None:
        _visualizer = BubbleMapVisualizer()
    return _visualizer


if __name__ == "__main__":
    print("=" * 70)
    print("BUBBLE MAP VISUALIZER")
    print("=" * 70)
    
    # Example usage
    example_data = {
        "nodes": [
            {"id": "WalletA123...", "type": "center", "size": 30, "color": "#ff6b6b", "volume": 50000, "transactions": 150},
            {"id": "WalletB456...", "type": "wallet", "size": 20, "color": "#69db7c", "volume": 25000, "transactions": 80},
            {"id": "WalletC789...", "type": "wallet", "size": 15, "color": "#69db7c", "volume": 10000, "transactions": 45},
        ],
        "links": [
            {"source": "WalletA123...", "target": "WalletB456...", "strength": 0.8, "volume": 20000},
            {"source": "WalletA123...", "target": "WalletC789...", "strength": 0.5, "volume": 5000},
        ]
    }
    
    viz = get_visualizer()
    html_path = viz.generate_html("WalletA123456789", example_data)
    print(f"\n✅ Generated: {html_path}")
    
    svg_path = viz.generate_svg("WalletA123456789", example_data)
    print(f"✅ Generated: {svg_path}")
    
    print("\n" + "=" * 70)
