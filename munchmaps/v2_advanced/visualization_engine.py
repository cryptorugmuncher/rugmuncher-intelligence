#!/usr/bin/env python3
"""
MunchMaps Visualization Engine
Using free, powerful libraries for BubbleMaps-style visualizations
"""
import json
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class Node:
    id: str
    label: str
    x: float = 0
    y: float = 0
    size: float = 10
    color: str = '#4A90E2'
    risk_score: float = 0
    wallet_type: str = 'unknown'
    chain: str = 'ethereum'
    
@dataclass
class Edge:
    source: str
    target: str
    value: float = 0
    color: str = '#999'
    width: float = 1
    type: str = 'transfer'

class BubbleMapVisualizer:
    """
    Create BubbleMaps-style visualizations
    Using free libraries (Sigma.js, Cytoscape.js, D3.js compatible output)
    """
    
    def __init__(self, width: int = 1200, height: int = 800):
        self.width = width
        self.height = height
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        
    def add_wallet(self, address: str, metadata: Dict):
        """Add wallet node to visualization"""
        # Calculate size based on transaction volume
        tx_count = metadata.get('transaction_count', 0)
        size = min(50, 10 + math.log(tx_count + 1) * 5) if tx_count > 0 else 10
        
        # Color based on risk
        risk = metadata.get('risk_score', 0)
        color = self._risk_to_color(risk)
        
        # Position using force-directed layout algorithm
        x, y = self._calculate_position(address, metadata)
        
        node = Node(
            id=address,
            label=self._truncate_address(address),
            x=x,
            y=y,
            size=size,
            color=color,
            risk_score=risk,
            wallet_type=metadata.get('wallet_type', 'unknown'),
            chain=metadata.get('chain', 'ethereum')
        )
        
        self.nodes[address] = node
        
    def add_connection(self, from_addr: str, to_addr: str, value: float = 0, tx_type: str = 'transfer'):
        """Add connection between wallets"""
        edge = Edge(
            source=from_addr,
            target=to_addr,
            value=value,
            width=min(10, 1 + math.log(value + 1)) if value > 0 else 1,
            color='#FF6B6B' if value > 10000 else '#999',
            type=tx_type
        )
        self.edges.append(edge)
        
    def _risk_to_color(self, risk: float) -> str:
        """Convert risk score to color"""
        if risk >= 0.8:
            return '#FF0000'  # Red - Critical
        elif risk >= 0.6:
            return '#FF6B6B'  # Light red - High
        elif risk >= 0.4:
            return '#FFA500'  # Orange - Medium
        elif risk >= 0.2:
            return '#FFD700'  # Yellow - Low
        return '#4A90E2'  # Blue - Safe
        
    def _truncate_address(self, addr: str) -> str:
        """Truncate address for display"""
        if len(addr) <= 12:
            return addr
        return f"{addr[:6]}...{addr[-4:]}"
        
    def _calculate_position(self, address: str, metadata: Dict) -> tuple:
        """Calculate node position using force-directed approach"""
        # Simple circular layout for now
        # In production, use force-directed algorithm
        import hashlib
        
        # Use hash for deterministic pseudo-random position
        hash_val = int(hashlib.md5(address.encode()).hexdigest(), 16)
        angle = (hash_val % 360) * (math.pi / 180)
        radius = 100 + (hash_val % 300)
        
        x = self.width / 2 + radius * math.cos(angle)
        y = self.height / 2 + radius * math.sin(angle)
        
        return x, y
        
    def export_sigma_js(self) -> Dict:
        """Export for Sigma.js visualization"""
        return {
            'nodes': [
                {
                    'id': n.id,
                    'label': n.label,
                    'x': n.x,
                    'y': n.y,
                    'size': n.size,
                    'color': n.color,
                    'attributes': {
                        'risk_score': n.risk_score,
                        'wallet_type': n.wallet_type,
                        'chain': n.chain
                    }
                }
                for n in self.nodes.values()
            ],
            'edges': [
                {
                    'id': f"e{i}",
                    'source': e.source,
                    'target': e.target,
                    'size': e.width,
                    'color': e.color,
                    'attributes': {
                        'value': e.value,
                        'type': e.type
                    }
                }
                for i, e in enumerate(self.edges)
            ]
        }
        
    def export_cytoscape_js(self) -> Dict:
        """Export for Cytoscape.js visualization"""
        elements = []
        
        # Nodes
        for node in self.nodes.values():
            elements.append({
                'data': {
                    'id': node.id,
                    'label': node.label,
                    'risk': node.risk_score,
                    'type': node.wallet_type,
                    'chain': node.chain
                },
                'position': {'x': node.x, 'y': node.y},
                'style': {
                    'background-color': node.color,
                    'width': node.size * 2,
                    'height': node.size * 2
                }
            })
        
        # Edges
        for i, edge in enumerate(self.edges):
            elements.append({
                'data': {
                    'id': f"e{i}",
                    'source': edge.source,
                    'target': edge.target,
                    'value': edge.value
                },
                'style': {
                    'width': edge.width,
                    'line-color': edge.color
                }
            })
        
        return {'elements': elements}
        
    def export_d3_js(self) -> Dict:
        """Export for D3.js visualization"""
        return {
            'nodes': [
                {
                    'id': n.id,
                    'group': int(n.risk_score * 10),
                    'radius': n.size
                }
                for n in self.nodes.values()
            ],
            'links': [
                {
                    'source': e.source,
                    'target': e.target,
                    'value': e.value
                }
                for e in self.edges
            ]
        }
        
    def export_html(self, title: str = "MunchMaps Visualization") -> str:
        """Generate standalone HTML with embedded visualization"""
        
        cytoscape_data = self.export_cytoscape_js()
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script src="https://unpkg.com/cytoscape@3.26.0/dist/cytoscape.min.js"></script>
    <style>
        body {{ margin: 0; font-family: Arial, sans-serif; }}
        #cy {{ width: 100vw; height: 100vh; background: #1a1a2e; }}
        #info {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 15px;
            border-radius: 8px;
            max-width: 300px;
        }}
        .legend {{
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 15px;
            border-radius: 8px;
        }}
        .legend-item {{ display: flex; align-items: center; margin: 5px 0; }}
        .color-box {{ width: 20px; height: 20px; margin-right: 10px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div id="cy"></div>
    <div id="info">
        <h3>🍔 MunchMaps V2</h3>
        <p><strong>Nodes:</strong> {len(self.nodes)}</p>
        <p><strong>Connections:</strong> {len(self.edges)}</p>
        <p><strong>Critical Risk:</strong> {sum(1 for n in self.nodes.values() if n.risk_score >= 0.8)}</p>
        <p><strong>High Risk:</strong> {sum(1 for n in self.nodes.values() if 0.6 <= n.risk_score < 0.8)}</p>
        <p>Click node for details • Drag to rearrange • Scroll to zoom</p>
    </div>
    <div class="legend">
        <h4>Risk Level</h4>
        <div class="legend-item"><div class="color-box" style="background:#FF0000"></div>Critical (80%+)</div>
        <div class="legend-item"><div class="color-box" style="background:#FF6B6B"></div>High (60-79%)</div>
        <div class="legend-item"><div class="color-box" style="background:#FFA500"></div>Medium (40-59%)</div>
        <div class="legend-item"><div class="color-box" style="background:#FFD700"></div>Low (20-39%)</div>
        <div class="legend-item"><div class="color-box" style="background:#4A90E2"></div>Safe (0-19%)</div>
    </div>
    <script>
        var cy = cytoscape({{
            container: document.getElementById('cy'),
            elements: {json.dumps(cytoscape_data['elements'])},
            style: [
                {{
                    selector: 'node',
                    style: {{
                        'label': 'data(label)',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'color': '#fff',
                        'font-size': '10px',
                        'border-width': 2,
                        'border-color': '#fff'
                    }}
                }},
                {{
                    selector: 'edge',
                    style: {{
                        'curve-style': 'bezier',
                        'target-arrow-shape': 'triangle',
                        'arrow-scale': 1.5
                    }}
                }}
            ],
            layout: {{
                name: 'cose',
                padding: 10,
                nodeRepulsion: 4500,
                idealEdgeLength: 100,
                animate: true
            }}
        }});
        
        // Add click handler
        cy.on('tap', 'node', function(evt){{
            var node = evt.target;
            alert('Wallet: ' + node.id() + '\\nRisk: ' + (node.data('risk') * 100).toFixed(1) + '%');
        }});
    </script>
</body>
</html>'''
        
        return html


class TemporalVisualizer:
    """
    Create temporal playback visualizations
    Frame-by-frame evolution of network
    """
    
    def __init__(self):
        self.frames = []
        
    def add_frame(self, timestamp: str, active_wallets: List[str], new_connections: List[Dict]):
        """Add a timeline frame"""
        self.frames.append({
            'timestamp': timestamp,
            'active_wallets': active_wallets,
            'new_connections': new_connections,
            'stats': {
                'total_active': len(active_wallets),
                'new_connections_count': len(new_connections)
            }
        })
        
    def export_video_frames(self) -> List[Dict]:
        """Export frames for video generation"""
        return self.frames
        
    def export_html_player(self) -> str:
        """Generate HTML5 video player with timeline"""
        # Returns HTML with scrubbable timeline
        frames_json = json.dumps(self.frames)
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>MunchMaps Temporal Playback</title>
    <style>
        body {{ margin: 0; background: #1a1a2e; color: white; font-family: Arial; }}
        #timeline {{ width: 100%; height: 60px; background: #2d2d44; display: flex; align-items: center; padding: 0 20px; }}
        #scrubber {{ width: 80%; height: 8px; background: #444; border-radius: 4px; cursor: pointer; }}
        #play-pause {{ 
            width: 40px; height: 40px; background: #4A90E2; border: none; border-radius: 50%; 
            color: white; font-size: 16px; cursor: pointer; margin-right: 20px;
        }}
        #frame-info {{ margin-left: 20px; }}
        #visualization {{ width: 100%; height: calc(100vh - 60px); }}
    </style>
</head>
<body>
    <div id="timeline">
        <button id="play-pause">▶</button>
        <div id="scrubber"></div>
        <div id="frame-info">Frame 0 / {len(self.frames)}</div>
    </div>
    <div id="visualization"></div>
    <script>
        const frames = {frames_json};
        let currentFrame = 0;
        let isPlaying = false;
        let playInterval;
        
        function updateFrame(index) {{
            currentFrame = index;
            document.getElementById('frame-info').textContent = 
                `Frame ${{index + 1}} / ${{frames.length}} - ${{frames[index].timestamp}}`;
            // Update visualization here
        }}
        
        document.getElementById('play-pause').onclick = function() {{
            if (isPlaying) {{
                clearInterval(playInterval);
                this.textContent = '▶';
            }} else {{
                playInterval = setInterval(() => {{
                    currentFrame = (currentFrame + 1) % frames.length;
                    updateFrame(currentFrame);
                }}, 1000);
                this.textContent = '⏸';
            }}
            isPlaying = !isPlaying;
        }};
        
        // Initialize
        updateFrame(0);
    </script>
</body>
</html>'''
        
        return html


class HeatmapVisualizer:
    """
    Create risk heatmaps
    """
    
    def create_risk_heatmap(self, wallet_data: List[Dict]) -> Dict:
        """Create risk heatmap data"""
        
        # Grid-based heatmap
        grid_size = 50
        heatmap = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        
        for wallet in wallet_data:
            x = int(wallet.get('grid_x', 0) * grid_size) % grid_size
            y = int(wallet.get('grid_y', 0) * grid_size) % grid_size
            risk = wallet.get('risk_score', 0)
            
            # Add heat to surrounding cells
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < grid_size and 0 <= ny < grid_size:
                        distance = math.sqrt(dx*dx + dy*dy)
                        heatmap[ny][nx] += risk / (1 + distance)
        
        return {
            'grid_size': grid_size,
            'heatmap': heatmap,
            'max_value': max(max(row) for row in heatmap)
        }


if __name__ == "__main__":
    print("MunchMaps Visualization Engine")
    print("=" * 50)
    
    # Demo
    viz = BubbleMapVisualizer()
    
    # Add some demo nodes
    viz.add_wallet("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", {
        'transaction_count': 150,
        'risk_score': 0.85,
        'wallet_type': 'PIG_BUTCHER_OPERATOR',
        'chain': 'ethereum'
    })
    
    viz.add_wallet("0x123abc...", {
        'transaction_count': 50,
        'risk_score': 0.3,
        'wallet_type': 'victim',
        'chain': 'ethereum'
    })
    
    viz.add_connection("0x123abc...", "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb", 5000)
    
    print(f"\nCreated visualization with {len(viz.nodes)} nodes and {len(viz.edges)} edges")
    print("\nExport formats available:")
    print("  • Sigma.js (free, WebGL accelerated)")
    print("  • Cytoscape.js (free, interactive)")
    print("  • D3.js (free, customizable)")
    print("  • Standalone HTML (embedded)")
    
    # Save HTML example
    html = viz.export_html("Demo Investigation")
    with open('/tmp/demo_viz.html', 'w') as f:
        f.write(html)
    print("\n✓ Demo saved to /tmp/demo_viz.html")
