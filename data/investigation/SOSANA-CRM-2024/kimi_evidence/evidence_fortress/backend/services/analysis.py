"""
================================================================================
ANALYSIS SERVICE - Pattern Detection & LLM Analysis
Evidence Fortress v4.0
================================================================================
"""

import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
import asyncpg

from .llm_cost_optimizer import LLMCostOptimizer, RoutingDecision
from ..security.sanitization_gateway import SanitizationGateway


class PatternDetector:
    """Detect suspicious patterns in transaction data."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
    
    async def detect_rapid_fire(self, pseudonym: str, time_window_seconds: int = 60) -> Dict:
        """
        Detect rapid-fire transaction patterns (botnet seeding).
        
        Args:
            pseudonym: Entity pseudonym to analyze
            time_window_seconds: Time window for grouping
            
        Returns:
            Pattern analysis results
        """
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    block_time,
                    COUNT(*) OVER (
                        ORDER BY block_time 
                        RANGE BETWEEN INTERVAL '1 minute' PRECEDING AND CURRENT ROW
                    ) as tx_in_window
                FROM transaction_graph
                WHERE from_pseudonym = $1
                ORDER BY block_time
                """,
                pseudonym
            )
        
        if not rows:
            return {"detected": False, "reason": "No transactions found"}
        
        # Find peak transaction rate
        max_rate = max(r['tx_in_window'] for r in rows)
        avg_rate = sum(r['tx_in_window'] for r in rows) / len(rows)
        
        # Classification
        is_suspicious = max_rate > 50  # More than 50 tx/min is suspicious
        
        return {
            "detected": is_suspicious,
            "pattern_type": "rapid_fire_seeding" if is_suspicious else "normal",
            "max_tx_per_minute": max_rate,
            "average_tx_per_minute": round(avg_rate, 2),
            "total_transactions": len(rows),
            "confidence": min(max_rate / 100, 0.99) if is_suspicious else 0.0
        }
    
    async def detect_layering(self, pseudonym: str, depth: int = 3) -> Dict:
        """
        Detect layering patterns (funds moved through multiple hops).
        
        Args:
            pseudonym: Starting entity pseudonym
            depth: Maximum traversal depth
            
        Returns:
            Layering analysis
        """
        async with self.db_pool.acquire() as conn:
            # Recursive query to find transaction chains
            rows = await conn.fetch(
                """
                WITH RECURSIVE transaction_chain AS (
                    -- Base case: direct transactions
                    SELECT 
                        from_pseudonym,
                        to_pseudonym,
                        amount_decimal,
                        block_time,
                        1 as depth
                    FROM transaction_graph
                    WHERE from_pseudonym = $1
                    
                    UNION ALL
                    
                    -- Recursive case: follow the chain
                    SELECT 
                        t.from_pseudonym,
                        t.to_pseudonym,
                        t.amount_decimal,
                        t.block_time,
                        tc.depth + 1
                    FROM transaction_graph t
                    JOIN transaction_chain tc ON t.from_pseudonym = tc.to_pseudonym
                    WHERE tc.depth < $2
                )
                SELECT * FROM transaction_chain
                ORDER BY depth, block_time
                """,
                pseudonym, depth
            )
        
        if not rows:
            return {"detected": False, "reason": "No transaction chain found"}
        
        # Analyze chain characteristics
        chain_lengths = {}
        for row in rows:
            d = row['depth']
            chain_lengths[d] = chain_lengths.get(d, 0) + 1
        
        max_depth = max(row['depth'] for row in rows)
        is_layering = max_depth >= 3 and len(rows) >= 10
        
        return {
            "detected": is_layering,
            "pattern_type": "layering" if is_layering else "simple_transfer",
            "max_depth": max_depth,
            "total_hops": len(rows),
            "depth_distribution": chain_lengths,
            "confidence": min(max_depth / 5, 0.99) if is_layering else 0.0
        }
    
    async def detect_structuring(self, pseudonym: str, threshold: float = 10000.0) -> Dict:
        """
        Detect structuring (keeping amounts below reporting thresholds).
        
        Args:
            pseudonym: Entity to analyze
            threshold: Amount threshold to check against
            
        Returns:
            Structuring analysis
        """
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT amount_decimal
                FROM transaction_graph
                WHERE from_pseudonym = $1
                ORDER BY amount_decimal
                """,
                pseudonym
            )
        
        if not rows:
            return {"detected": False, "reason": "No transactions found"}
        
        amounts = [r['amount_decimal'] for r in rows]
        
        # Check for amounts just below threshold
        near_threshold = [a for a in amounts if threshold * 0.8 < a < threshold]
        
        # Check for round numbers (common in structuring)
        round_numbers = [a for a in amounts if a % 1000 == 0 or a % 5000 == 0]
        
        is_structuring = len(near_threshold) > 5 or len(round_numbers) > len(amounts) * 0.7
        
        return {
            "detected": is_structuring,
            "pattern_type": "structuring" if is_structuring else "normal",
            "transactions_near_threshold": len(near_threshold),
            "round_number_transactions": len(round_numbers),
            "total_transactions": len(amounts),
            "confidence": len(near_threshold) / 20 if is_structuring else 0.0
        }


class LLMAnalyzer:
    """LLM-powered analysis with cost optimization."""
    
    def __init__(self, db_pool: asyncpg.Pool, optimizer: LLMCostOptimizer, gateway: SanitizationGateway):
        self.db_pool = db_pool
        self.optimizer = optimizer
        self.gateway = gateway
    
    async def analyze_entity_behavior(
        self, 
        pseudonym: str,
        analysis_type: str = "comprehensive"
    ) -> Dict:
        """
        Perform LLM analysis of entity behavior.
        
        Args:
            pseudonym: Entity pseudonym
            analysis_type: 'quick', 'standard', or 'comprehensive'
            
        Returns:
            Analysis results
        """
        # Get entity data
        async with self.db_pool.acquire() as conn:
            entity = await conn.fetchrow(
                """
                SELECT * FROM crypto_entities WHERE pseudonym = $1
                """,
                pseudonym
            )
            
            transactions = await conn.fetch(
                """
                SELECT * FROM transaction_graph
                WHERE from_pseudonym = $1 OR to_pseudonym = $1
                ORDER BY block_time DESC
                LIMIT 100
                """,
                pseudonym
            )
        
        if not entity:
            return {"error": "Entity not found"}
        
        # Build sanitized context for LLM
        context = self._build_analysis_context(entity, transactions)
        
        # Route to appropriate LLM
        routing = await self.optimizer.route_request(
            task_description=f"Analyze {analysis_type} behavior patterns for crypto entity",
            estimated_input_tokens=len(context) // 4,
            estimated_output_tokens=500 if analysis_type == 'quick' else 1500,
            requires_json=True,
            data_is_pre_sanitized=True  # We only use pseudonyms
        )
        
        # Execute analysis (placeholder - implement actual LLM calls)
        result = await self._execute_llm_analysis(context, routing)
        
        return {
            "entity": pseudonym,
            "analysis_type": analysis_type,
            "llm_used": f"{routing.provider.value}/{routing.model}",
            "cost_microdollars": routing.estimated_cost_microdollars,
            "result": result
        }
    
    def _build_analysis_context(self, entity: asyncpg.Record, transactions: List) -> str:
        """Build sanitized context for LLM analysis."""
        context = f"""
Entity: {entity['pseudonym']}
Tier: {entity['entity_tier']}
Role: {entity['entity_role']}
Risk Score: {entity['risk_score']}
First Seen: {entity['first_seen']}
Last Seen: {entity['last_seen']}
Transaction Count: {entity['transaction_count']}

Recent Transactions:
"""
        for tx in transactions[:20]:
            context += f"- {tx['block_time']}: {tx['from_pseudonym']} -> {tx['to_pseudonym']}: {tx['amount_decimal']} {tx['token_symbol']}\n"
        
        return context
    
    async def _execute_llm_analysis(self, context: str, routing: RoutingDecision) -> Dict:
        """Execute LLM analysis based on routing decision."""
        # This is a placeholder - implement actual LLM calls
        # based on the routing decision
        
        if routing.provider.value == 'ollama':
            # Use local Ollama
            return {"note": "Ollama analysis would run here", "context_length": len(context)}
        elif routing.provider.value == 'groq':
            # Use Groq API
            return {"note": "Groq analysis would run here", "context_length": len(context)}
        else:
            return {"note": f"{routing.provider.value} analysis would run here"}


class EvidenceAnalyzer:
    """Main analysis orchestrator."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.pattern_detector = PatternDetector(db_pool)
        self.optimizer = LLMCostOptimizer(db_pool)
        # Gateway initialized separately with encryption key
        self.llm_analyzer = None
    
    def initialize_gateway(self, gateway: SanitizationGateway):
        """Initialize with sanitization gateway."""
        self.llm_analyzer = LLMAnalyzer(self.db_pool, self.optimizer, gateway)
    
    async def full_entity_analysis(self, pseudonym: str) -> Dict:
        """
        Run complete analysis on an entity.
        
        Args:
            pseudonym: Entity pseudonym
            
        Returns:
            Complete analysis report
        """
        print(f"\n🔍 Analyzing entity: {pseudonym}")
        print("="*60)
        
        # Pattern detection
        print("  Detecting rapid-fire patterns...")
        rapid_fire = await self.pattern_detector.detect_rapid_fire(pseudonym)
        
        print("  Detecting layering patterns...")
        layering = await self.pattern_detector.detect_layering(pseudonym)
        
        print("  Detecting structuring patterns...")
        structuring = await self.pattern_detector.detect_structuring(pseudonym)
        
        # Compile report
        report = {
            "entity": pseudonym,
            "analyzed_at": datetime.now().isoformat(),
            "patterns": {
                "rapid_fire": rapid_fire,
                "layering": layering,
                "structuring": structuring
            },
            "overall_risk": self._calculate_overall_risk(
                rapid_fire, layering, structuring
            ),
            "recommendations": self._generate_recommendations(
                rapid_fire, layering, structuring
            )
        }
        
        print(f"\n📊 Analysis Complete:")
        print(f"  Overall Risk: {report['overall_risk']:.2f}")
        print(f"  Patterns Detected: {sum(1 for p in report['patterns'].values() if p.get('detected', False))}")
        
        return report
    
    def _calculate_overall_risk(self, rapid_fire: Dict, layering: Dict, structuring: Dict) -> float:
        """Calculate overall risk score."""
        risks = []
        
        if rapid_fire.get('detected'):
            risks.append(rapid_fire.get('confidence', 0) * 0.9)
        if layering.get('detected'):
            risks.append(layering.get('confidence', 0) * 0.8)
        if structuring.get('detected'):
            risks.append(structuring.get('confidence', 0) * 0.7)
        
        return max(risks) if risks else 0.0
    
    def _generate_recommendations(self, rapid_fire: Dict, layering: Dict, structuring: Dict) -> List[str]:
        """Generate investigation recommendations."""
        recommendations = []
        
        if rapid_fire.get('detected'):
            recommendations.append(
                f"HIGH PRIORITY: Rapid-fire pattern detected ({rapid_fire.get('max_tx_per_minute')} tx/min). "
                "Likely botnet seeder. Trace recipient wallets for clustering."
            )
        
        if layering.get('detected'):
            recommendations.append(
                f"Layering detected with {layering.get('max_depth')} hops. "
                "Follow chain to identify cashout points."
            )
        
        if structuring.get('detected'):
            recommendations.append(
                f"Structuring pattern detected ({structuring.get('transactions_near_threshold')} near threshold). "
                "Review for AML violations."
            )
        
        if not recommendations:
            recommendations.append("No suspicious patterns detected. Monitor for changes.")
        
        return recommendations


# ==============================================================================
# CLI Interface
# ==============================================================================

async def main():
    """CLI entry point for analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Evidence Fortress Analysis')
    parser.add_argument('--entity', '-e', help='Entity pseudonym to analyze')
    parser.add_argument('--all', '-a', action='store_true', help='Analyze all entities')
    parser.add_argument('--db-url', default='postgresql://localhost/evidence_fortress')
    
    args = parser.parse_args()
    
    # Connect to database
    db_pool = await asyncpg.create_pool(args.db_url)
    
    # Create analyzer
    analyzer = EvidenceAnalyzer(db_pool)
    
    if args.entity:
        # Analyze single entity
        report = await analyzer.full_entity_analysis(args.entity)
        print(json.dumps(report, indent=2))
    
    elif args.all:
        # Analyze all entities
        async with db_pool.acquire() as conn:
            entities = await conn.fetch(
                "SELECT pseudonym FROM crypto_entities WHERE risk_score > 0.5"
            )
        
        for entity in entities:
            report = await analyzer.full_entity_analysis(entity['pseudonym'])
            print(json.dumps(report, indent=2))
            print("\n" + "="*60 + "\n")
    
    else:
        print("Usage:")
        print("  python -m backend.services.analysis --entity [BOTNET_SEEDER_001]")
        print("  python -m backend.services.analysis --all")
    
    await db_pool.close()


if __name__ == '__main__':
    asyncio.run(main())
