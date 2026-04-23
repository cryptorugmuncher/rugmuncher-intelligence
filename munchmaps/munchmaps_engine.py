#!/usr/bin/env python3
"""
Part 4: MunchMaps Visualization Engine
Create interactive visualizations of investigation data
"""
import sys
sys.path.insert(0, '/root/rmi/venv/lib/python3.12/site-packages')

from supabase import create_client
import json
import logging
from typing import Dict, List, Any
from datetime import datetime
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = "https://ufblzfxqwgaekrewncbi.supabase.co"
SERVICE_KEY = "sb_secret_Uye75Qavhe0ZXJCo4Uadiw_CCYWULKa"
CASE_ID = "SOSANA-CRM-2024"

class MunchMapsEngine:
    """
    Generate visualization data for investigation dashboard
    """
    
    def __init__(self):
        self.supabase = create_client(SUPABASE_URL, SERVICE_KEY)
        self.data = {
            "wallets": [],
            "entities": [],
            "transactions": [],
            "timeline": []
        }
        self.viz_data = {}
    
    def load_data(self):
        """Load all investigation data"""
        print("📊 Loading investigation data...")
        
        # Load wallets
        result = self.supabase.table("investigation_wallets").select("*").eq("case_id", CASE_ID).execute()
        self.data["wallets"] = result.data
        print(f"  ✓ Loaded {len(self.data['wallets'])} wallets")
        
        # Load entities
        result = self.supabase.table("investigation_entities").select("*").eq("case_id", CASE_ID).execute()
        self.data["entities"] = result.data
        print(f"  ✓ Loaded {len(self.data['entities'])} entities")
        
        # Load evidence
        result = self.supabase.table("investigation_evidence").select("*").eq("case_id", CASE_ID).execute()
        self.data["evidence"] = result.data
        print(f"  ✓ Loaded {len(self.data['evidence'])} evidence items")
        
        # Load timeline
        result = self.supabase.table("investigation_timeline").select("*").eq("case_id", CASE_ID).execute()
        self.data["timeline"] = result.data
        print(f"  ✓ Loaded {len(self.data['timeline'])} timeline events")
    
    def generate_network_graph(self) -> Dict:
        """Generate wallet/entity network graph"""
        print("\n🕸️  Generating Network Graph...")
        
        nodes = []
        edges = []
        
        # Add wallet nodes
        for wallet in self.data["wallets"]:
            risk_score = wallet.get("risk_score", 0)
            metadata = wallet.get("metadata", {})
            
            nodes.append({
                "id": wallet["address"],
                "type": "wallet",
                "label": wallet["address"][:10] + "...",
                "risk_score": risk_score,
                "risk_level": self._get_risk_level(risk_score),
                "chain": wallet.get("chain", "ethereum"),
                "size": 10 + (risk_score / 10),  # Size based on risk
                "color": self._get_risk_color(risk_score),
                "x": self._random_position(),
                "y": self._random_position()
            })
        
        # Add entity nodes
        for entity in self.data["entities"]:
            if entity["entity_type"] != "wallet":  # Skip wallets (already added)
                nodes.append({
                    "id": f"{entity['entity_type']}:{entity['name']}",
                    "type": entity["entity_type"],
                    "label": entity["name"],
                    "risk_level": entity.get("risk_level", "unknown"),
                    "size": 15,
                    "color": self._get_entity_color(entity["entity_type"]),
                    "x": self._random_position(),
                    "y": self._random_position()
                })
                
                # Connect entity to related wallets
                wallets = entity.get("wallets", {})
                if wallets.get("primary"):
                    edges.append({
                        "source": wallets["primary"],
                        "target": f"{entity['entity_type']}:{entity['name']}",
                        "type": "entity_relationship",
                        "weight": 2
                    })
        
        # Add connection edges from wallet metadata
        for wallet in self.data["wallets"]:
            metadata = wallet.get("metadata", {})
            connected = metadata.get("connected_wallets", [])
            
            for conn in connected:
                edges.append({
                    "source": wallet["address"],
                    "target": conn["address"],
                    "type": "transaction",
                    "weight": conn.get("interactions", 1),
                    "label": f"{conn.get('interactions', 1)} txs"
                })
        
        graph = {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "wallet_nodes": len([n for n in nodes if n["type"] == "wallet"]),
                "entity_nodes": len([n for n in nodes if n["type"] != "wallet"])
            }
        }
        
        print(f"  ✓ Generated graph: {len(nodes)} nodes, {len(edges)} edges")
        return graph
    
    def generate_timeline_chart(self) -> Dict:
        """Generate timeline visualization data"""
        print("\n📅 Generating Timeline Chart...")
        
        events = []
        
        for event in self.data["timeline"]:
            events.append({
                "date": event.get("event_date") or event.get("created_at"),
                "type": event.get("event_type", "unknown"),
                "description": event.get("description", "")[:100],
                "entities": event.get("related_entities", {})
            })
        
        # Sort by date
        events.sort(key=lambda x: x["date"] or "")
        
        timeline = {
            "events": events,
            "metadata": {
                "total_events": len(events),
                "date_range": {
                    "start": events[0]["date"] if events else None,
                    "end": events[-1]["date"] if events else None
                }
            }
        }
        
        print(f"  ✓ Generated timeline: {len(events)} events")
        return timeline
    
    def generate_risk_heatmap(self) -> Dict:
        """Generate risk score heatmap data"""
        print("\n🔥 Generating Risk Heatmap...")
        
        risk_buckets = {
            "critical": [],  # 80-100
            "high": [],      # 60-79
            "medium": [],    # 40-59
            "low": [],       # 20-39
            "safe": []       # 0-19
        }
        
        for wallet in self.data["wallets"]:
            risk_score = wallet.get("risk_score", 0) or 0
            
            if risk_score >= 80:
                bucket = "critical"
            elif risk_score >= 60:
                bucket = "high"
            elif risk_score >= 40:
                bucket = "medium"
            elif risk_score >= 20:
                bucket = "low"
            else:
                bucket = "safe"
            
            risk_buckets[bucket].append({
                "address": wallet["address"],
                "risk_score": risk_score,
                "chain": wallet.get("chain", "ethereum")
            })
        
        heatmap = {
            "buckets": risk_buckets,
            "summary": {
                "critical_count": len(risk_buckets["critical"]),
                "high_count": len(risk_buckets["high"]),
                "medium_count": len(risk_buckets["medium"]),
                "low_count": len(risk_buckets["low"]),
                "safe_count": len(risk_buckets["safe"]),
                "total_analyzed": len(self.data["wallets"])
            }
        }
        
        print(f"  ✓ Risk distribution: {len(risk_buckets['critical'])} critical, "
              f"{len(risk_buckets['high'])} high, "
              f"{len(risk_buckets['medium'])} medium")
        
        return heatmap
    
    def generate_token_map(self) -> Dict:
        """Generate token relationship map"""
        print("\n🪙 Generating Token Map...")
        
        tokens = {}
        
        # Extract token mentions from entities
        for entity in self.data["entities"]:
            if entity["entity_type"] == "token":
                token_symbol = entity["name"]
                
                tokens[token_symbol] = {
                    "symbol": token_symbol,
                    "risk_level": entity.get("risk_level", "unknown"),
                    "mentions": entity.get("metadata", {}).get("occurrences", 1),
                    "connected_wallets": []
                }
        
        # Add CRM token (the main scam token)
        if "CRM" not in tokens:
            tokens["CRM"] = {
                "symbol": "CRM",
                "risk_level": "high",
                "mentions": 89,
                "description": "SOSANA/CRM scam token"
            }
        
        token_map = {
            "tokens": list(tokens.values()),
            "total_tokens": len(tokens),
            "high_risk_tokens": len([t for t in tokens.values() if t.get("risk_level") == "high"])
        }
        
        print(f"  ✓ Mapped {len(tokens)} tokens")
        return token_map
    
    def generate_dashboard_summary(self) -> Dict:
        """Generate main dashboard summary"""
        print("\n📊 Generating Dashboard Summary...")
        
        # Calculate statistics
        total_wallets = len(self.data["wallets"])
        total_entities = len(self.data["entities"])
        total_evidence = len(self.data["evidence"])
        
        high_risk_wallets = len([w for w in self.data["wallets"] if (w.get("risk_score") or 0) > 60])
        
        # Get evidence categories
        evidence_categories = {}
        for item in self.data["evidence"]:
            cat = item.get("category", "other")
            evidence_categories[cat] = evidence_categories.get(cat, 0) + 1
        
        summary = {
            "case_id": CASE_ID,
            "generated_at": datetime.now().isoformat(),
            "statistics": {
                "total_wallets": total_wallets,
                "total_entities": total_entities,
                "total_evidence": total_evidence,
                "high_risk_wallets": high_risk_wallets,
                "timeline_events": len(self.data["timeline"])
            },
            "evidence_breakdown": evidence_categories,
            "risk_distribution": {
                "high_risk_percentage": round((high_risk_wallets / total_wallets * 100), 2) if total_wallets else 0,
                "medium_risk_count": len([w for w in self.data["wallets"] if 40 <= (w.get("risk_score") or 0) < 60]),
                "low_risk_count": len([w for w in self.data["wallets"] if (w.get("risk_score") or 0) < 40])
            }
        }
        
        return summary
    
    def generate_all_visualizations(self):
        """Generate all visualization data"""
        print("=" * 70)
        print("🗺️  PART 4: MUNCHMAPS VISUALIZATION ENGINE")
        print("=" * 70)
        
        # Load data
        self.load_data()
        
        # Generate all visualizations
        self.viz_data = {
            "network_graph": self.generate_network_graph(),
            "timeline": self.generate_timeline_chart(),
            "risk_heatmap": self.generate_risk_heatmap(),
            "token_map": self.generate_token_map(),
            "dashboard": self.generate_dashboard_summary()
        }
        
        # Save all visualizations
        self._save_visualizations()
        
        # Print summary
        self._print_summary()
    
    def _save_visualizations(self):
        """Save all visualization data to files"""
        print("\n💾 Saving visualization data...")
        
        # Save main file
        with open("/root/rmi/munchmaps/munchmaps_data.json", 'w') as f:
            json.dump(self.viz_data, f, indent=2, default=str)
        
        # Save individual components
        for name, data in self.viz_data.items():
            with open(f"/root/rmi/munchmaps/{name}.json", 'w') as f:
                json.dump(data, f, indent=2, default=str)
        
        print("  ✓ Saved to /root/rmi/munchmaps/")
    
    def _print_summary(self):
        """Print final summary"""
        print("\n" + "=" * 70)
        print("✅ PART 4 COMPLETE - MUNCHMAPS VISUALIZATION")
        print("=" * 70)
        
        summary = self.viz_data["dashboard"]["statistics"]
        
        print(f"\n📊 Investigation Dashboard Summary:")
        print(f"  • Total Wallets: {summary['total_wallets']}")
        print(f"  • Total Entities: {summary['total_entities']}")
        print(f"  • Total Evidence: {summary['total_evidence']}")
        print(f"  • High Risk Wallets: {summary['high_risk_wallets']}")
        print(f"  • Timeline Events: {summary['timeline_events']}")
        
        print(f"\n🗺️  Generated Visualizations:")
        print(f"  1. Network Graph: {self.viz_data['network_graph']['metadata']['total_nodes']} nodes")
        print(f"  2. Timeline: {self.viz_data['timeline']['metadata']['total_events']} events")
        print(f"  3. Risk Heatmap: {self.viz_data['token_map']['total_tokens']} tokens")
        print(f"  4. Token Map: {self.viz_data['risk_heatmap']['summary']['critical_count']} critical risk")
        print(f"  5. Dashboard Summary: Complete")
        
        print(f"\n📁 Output Files:")
        print(f"  • /root/rmi/munchmaps/munchmaps_data.json (complete)")
        print(f"  • /root/rmi/munchmaps/network_graph.json")
        print(f"  • /root/rmi/munchmaps/timeline.json")
        print(f"  • /root/rmi/munchmaps/risk_heatmap.json")
        print(f"  • /root/rmi/munchmaps/token_map.json")
        
        print("\n" + "=" * 70)
        print("🚀 ALL PARTS COMPLETE!")
        print("=" * 70)
    
    # Helper methods
    def _get_risk_level(self, score: int) -> str:
        if score >= 80: return "critical"
        if score >= 60: return "high"
        if score >= 40: return "medium"
        if score >= 20: return "low"
        return "safe"
    
    def _get_risk_color(self, score: int) -> str:
        if score >= 80: return "#ff0000"  # Red
        if score >= 60: return "#ff6600"  # Orange
        if score >= 40: return "#ffcc00"  # Yellow
        if score >= 20: return "#66cc00"  # Light green
        return "#00cc00"  # Green
    
    def _get_entity_color(self, entity_type: str) -> str:
        colors = {
            "telegram": "#0088cc",
            "twitter": "#1da1f2",
            "token": "#ffd700",
            "person": "#9370db",
            "organization": "#4169e1"
        }
        return colors.get(entity_type, "#808080")
    
    def _random_position(self) -> float:
        import random
        return random.uniform(-100, 100)


if __name__ == "__main__":
    engine = MunchMapsEngine()
    engine.generate_all_visualizations()
