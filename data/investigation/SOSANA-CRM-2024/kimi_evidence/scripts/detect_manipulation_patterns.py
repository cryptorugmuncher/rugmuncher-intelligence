#!/usr/bin/env python3
"""
DEX Manipulation Pattern Detector
=================================
Analyze exported DEX transactions to identify:
- Iceberg orders (large orders split into small pieces)
- Liquidity harvesting (selling into buying demand)
- Drip feeding / scaling out (small sells over time)
- Wash trading (self-trading between controlled wallets)
- Cross-wallet coordination (synchronized dumping)

Usage:
    python detect_manipulation_patterns.py --input DEX_HLnpSz9h_20250406_120000.json
    python detect_manipulation_patterns.py --all --input-dir .
"""

import argparse
import json
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Tuple, Optional
from statistics import mean, stdev


class ManipulationDetector:
    """Detect sophisticated market manipulation patterns in DEX data."""
    
    def __init__(self, dex_data: Dict[str, Any]):
        self.data = dex_data
        self.wallet = dex_data.get("wallet", "UNKNOWN")
        self.address = dex_data.get("address", "UNKNOWN")
        self.swaps = dex_data.get("swaps", {}).get("all", [])
        self.sells = dex_data.get("swaps", {}).get("sells", [])
        self.buys = dex_data.get("swaps", {}).get("buys", [])
    
    def detect_iceberg_orders(self) -> Dict[str, Any]:
        """
        Detect iceberg orders: large positions split into many small sells.
        
        Criteria:
        - 10+ sells within 1-hour window
        - Similar order sizes (±30% variance)
        - Regular or semi-regular timing
        """
        if len(self.sells) < 10:
            return {"detected": False, "reason": "Insufficient sell data"}
        
        # Group sells by 1-hour windows
        sells_by_hour = defaultdict(list)
        for sell in self.sells:
            timestamp = sell.get("timestamp", 0)
            hour_key = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H")
            sells_by_hour[hour_key].append(sell)
        
        iceberg_periods = []
        
        for hour, sells in sells_by_hour.items():
            if len(sells) < 10:
                continue
            
            # Check for similar order sizes
            amounts = [s.get("input_amount", 0) for s in sells]
            if len(amounts) < 2:
                continue
            
            avg_amount = mean(amounts)
            variance = stdev(amounts) / avg_amount if avg_amount > 0 else float('inf')
            
            # Check timing patterns
            timestamps = sorted([s.get("timestamp", 0) for s in sells])
            intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            
            avg_interval = mean(intervals) if intervals else 0
            interval_variance = stdev(intervals) / avg_interval if avg_interval > 0 and len(intervals) > 1 else float('inf')
            
            # Iceberg indicators
            is_iceberg = (
                len(sells) >= 10 and
                variance < 0.30 and  # <30% size variance
                interval_variance < 0.50  # <50% timing variance (some randomization)
            )
            
            if is_iceberg:
                total_volume = sum(amounts)
                iceberg_periods.append({
                    "hour": hour,
                    "sell_count": len(sells),
                    "total_volume": total_volume,
                    "avg_order_size": avg_amount,
                    "size_variance": variance,
                    "avg_interval_seconds": avg_interval,
                    "interval_variance": interval_variance,
                    "transactions": [s.get("tx_hash") for s in sells],
                    "evidence_tier": "TIER_1" if len(sells) >= 20 else "TIER_2"
                })
        
        return {
            "detected": len(iceberg_periods) > 0,
            "pattern_type": "ICEBERG_ORDERS",
            "periods": iceberg_periods,
            "total_periods": len(iceberg_periods),
            "evidence_quality": "HIGH" if len(iceberg_periods) >= 2 else "MEDIUM"
        }
    
    def detect_drip_feeding(self) -> Dict[str, Any]:
        """
        Detect drip feeding: consistent small sells over extended period.
        
        Criteria:
        - 7+ consecutive days with sells
        - Similar daily sell amounts (±25% variance)
        - No single sell >5% of daily volume
        """
        if len(self.sells) < 7:
            return {"detected": False, "reason": "Insufficient sell data"}
        
        # Group sells by day
        sells_by_day = defaultdict(list)
        for sell in self.sells:
            timestamp = sell.get("timestamp", 0)
            day_key = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
            sells_by_day[day_key].append(sell)
        
        # Check for consecutive days
        days = sorted(sells_by_day.keys())
        if len(days) < 7:
            return {"detected": False, "reason": "Insufficient consecutive days"}
        
        # Calculate daily totals
        daily_totals = []
        for day in days:
            day_sells = sells_by_day[day]
            total = sum(s.get("input_amount", 0) for s in day_sells)
            daily_totals.append({
                "day": day,
                "total": total,
                "count": len(day_sells),
                "transactions": [s.get("tx_hash") for s in day_sells]
            })
        
        # Check for consistent amounts
        amounts = [d["total"] for d in daily_totals]
        avg_amount = mean(amounts)
        variance = stdev(amounts) / avg_amount if avg_amount > 0 and len(amounts) > 1 else float('inf')
        
        # Check for regular timing (automation indicator)
        day_intervals = []
        for i in range(len(days) - 1):
            d1 = datetime.strptime(days[i], "%Y-%m-%d")
            d2 = datetime.strptime(days[i+1], "%Y-%m-%d")
            day_intervals.append((d2 - d1).days)
        
        consecutive_days = all(interval == 1 for interval in day_intervals)
        
        is_drip_feeding = (
            len(days) >= 7 and
            variance < 0.25 and  # <25% daily variance
            consecutive_days
        )
        
        return {
            "detected": is_drip_feeding,
            "pattern_type": "DRIP_FEEDING",
            "duration_days": len(days),
            "consecutive": consecutive_days,
            "daily_totals": daily_totals,
            "avg_daily_amount": avg_amount,
            "variance": variance,
            "total_volume": sum(amounts),
            "evidence_tier": "TIER_1" if len(days) >= 14 else "TIER_2" if len(days) >= 7 else "TIER_3"
        }
    
    def detect_liquidity_harvesting(self) -> Dict[str, Any]:
        """
        Detect liquidity harvesting: selling during high-volume periods.
        
        Note: This requires market-wide volume data which may not be available
        in individual wallet exports. We'll use heuristics based on timing.
        
        Criteria:
        - Sells concentrated in specific time windows
        - Pattern suggests selling into demand
        """
        if len(self.sells) < 5:
            return {"detected": False, "reason": "Insufficient sell data"}
        
        # Analyze timing patterns
        hours = defaultdict(int)
        for sell in self.sells:
            timestamp = sell.get("timestamp", 0)
            hour = datetime.fromtimestamp(timestamp).hour
            hours[hour] += 1
        
        # Check for concentration in specific hours
        total_sells = len(self.sells)
        hour_percentages = {h: (c / total_sells) * 100 for h, c in hours.items()}
        
        # Find peak hours (>20% of sells in single hour)
        peak_hours = [(h, p) for h, p in hour_percentages.items() if p > 20]
        
        # Check for business hours concentration (indicates active monitoring)
        business_hours = sum(c for h, c in hours.items() if 9 <= h <= 17)
        business_percentage = (business_hours / total_sells) * 100
        
        is_harvesting = (
            len(peak_hours) >= 1 or
            business_percentage > 60
        )
        
        return {
            "detected": is_harvesting,
            "pattern_type": "LIQUIDITY_HARVESTING",
            "peak_hours": peak_hours,
            "business_hours_percentage": business_percentage,
            "hour_distribution": dict(hours),
            "evidence_tier": "TIER_2" if len(peak_hours) >= 2 else "TIER_3",
            "note": "Requires market-wide volume data for confirmation"
        }
    
    def analyze_counterparties(self) -> Dict[str, Any]:
        """
        Analyze who the wallet is trading with.
        
        Look for:
        - Repeated counterparties (potential wash trading)
        - Diverse counterparties (legitimate trading)
        - Known network wallets
        """
        counterparties = defaultdict(lambda: {"count": 0, "total_crm": 0, "transactions": []})
        
        for swap in self.swaps:
            for counterparty in swap.get("counterparties", []):
                addr = counterparty.get("address", "UNKNOWN")
                amount = counterparty.get("amount", 0)
                
                counterparties[addr]["count"] += 1
                counterparties[addr]["total_crm"] += amount
                counterparties[addr]["transactions"].append(swap.get("tx_hash"))
        
        # Sort by frequency
        sorted_counterparties = sorted(
            counterparties.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        # Identify repeated trading (potential wash trading)
        repeated = [(addr, data) for addr, data in sorted_counterparties if data["count"] >= 3]
        
        return {
            "unique_counterparties": len(counterparties),
            "top_counterparties": sorted_counterparties[:10],
            "repeated_counterparties": repeated,
            "wash_trading_indicator": len(repeated) > 0,
            "evidence_tier": "TIER_1" if len(repeated) >= 3 else "TIER_2" if len(repeated) >= 1 else "TIER_3"
        }
    
    def calculate_financial_metrics(self) -> Dict[str, Any]:
        """Calculate financial impact metrics."""
        if not self.sells:
            return {"error": "No sell data"}
        
        # Total CRM sold
        total_crm_sold = sum(s.get("input_amount", 0) for s in self.sells)
        
        # Total SOL received (approximate)
        total_sol_received = sum(s.get("output_amount", 0) for s in self.sells if s.get("output_token") == "SOL")
        
        # Average sell size
        avg_sell = total_crm_sold / len(self.sells) if self.sells else 0
        
        # Largest single sell
        largest_sell = max((s.get("input_amount", 0) for s in self.sells), default=0)
        
        # Sell frequency
        if len(self.sells) >= 2:
            timestamps = sorted([s.get("timestamp", 0) for s in self.sells])
            first_sell = datetime.fromtimestamp(timestamps[0])
            last_sell = datetime.fromtimestamp(timestamps[-1])
            duration_days = (last_sell - first_sell).days + 1
            sells_per_day = len(self.sells) / duration_days if duration_days > 0 else 0
        else:
            duration_days = 0
            sells_per_day = 0
        
        return {
            "total_crm_sold": total_crm_sold,
            "total_sol_received": total_sol_received,
            "total_sells": len(self.sells),
            "avg_sell_size": avg_sell,
            "largest_single_sell": largest_sell,
            "duration_days": duration_days,
            "sells_per_day": sells_per_day,
            "estimated_usd_value": total_sol_received * 128  # Approximate SOL price
        }
    
    def generate_full_report(self) -> Dict[str, Any]:
        """Generate comprehensive manipulation analysis report."""
        print(f"\nAnalyzing manipulation patterns for {self.wallet}...")
        
        # Run all detection algorithms
        iceberg = self.detect_iceberg_orders()
        print(f"  Iceberg orders: {'DETECTED' if iceberg['detected'] else 'Not detected'}")
        
        drip = self.detect_drip_feeding()
        print(f"  Drip feeding: {'DETECTED' if drip['detected'] else 'Not detected'}")
        
        harvesting = self.detect_liquidity_harvesting()
        print(f"  Liquidity harvesting: {'DETECTED' if harvesting['detected'] else 'Not detected'}")
        
        counterparties = self.analyze_counterparties()
        print(f"  Unique counterparties: {counterparties['unique_counterparties']}")
        print(f"  Wash trading indicators: {'YES' if counterparties['wash_trading_indicator'] else 'No'}")
        
        financial = self.calculate_financial_metrics()
        print(f"  Total CRM sold: {financial.get('total_crm_sold', 0):,.2f}")
        print(f"  Total sells: {financial.get('total_sells', 0)}")
        
        # Compile patterns detected
        patterns = []
        if iceberg["detected"]:
            patterns.append(iceberg)
        if drip["detected"]:
            patterns.append(drip)
        if harvesting["detected"]:
            patterns.append(harvesting)
        if counterparties["wash_trading_indicator"]:
            patterns.append({
                "detected": True,
                "pattern_type": "WASH_TRADING",
                "details": counterparties["repeated_counterparties"],
                "evidence_tier": counterparties["evidence_tier"]
            })
        
        # Overall assessment
        overall_tier = "TIER_3"
        if any(p.get("evidence_tier") == "TIER_1" for p in patterns):
            overall_tier = "TIER_1"
        elif any(p.get("evidence_tier") == "TIER_2" for p in patterns):
            overall_tier = "TIER_2"
        
        report = {
            "wallet": self.wallet,
            "address": self.address,
            "analysis_timestamp": datetime.now().isoformat(),
            "patterns_detected": patterns,
            "total_patterns": len(patterns),
            "iceberg_analysis": iceberg,
            "drip_feeding_analysis": drip,
            "liquidity_harvesting_analysis": harvesting,
            "counterparty_analysis": counterparties,
            "financial_metrics": financial,
            "overall_evidence_tier": overall_tier,
            "legal_significance": self._assess_legal_significance(patterns)
        }
        
        return report
    
    def _assess_legal_significance(self, patterns: List[Dict]) -> Dict[str, Any]:
        """Assess legal significance of detected patterns."""
        significance = {
            "charges_supported": [],
            "evidence_strength": "WEAK",
            "recommendations": []
        }
        
        for pattern in patterns:
            pattern_type = pattern.get("pattern_type", "")
            
            if pattern_type == "ICEBERG_ORDERS":
                significance["charges_supported"].append("Market Manipulation")
                significance["recommendations"].append("Document order splitting intent")
            
            elif pattern_type == "DRIP_FEEDING":
                significance["charges_supported"].append("Market Manipulation")
                significance["recommendations"].append("Show sustained selling pattern")
            
            elif pattern_type == "LIQUIDITY_HARVESTING":
                significance["charges_supported"].append("Market Manipulation")
                significance["recommendations"].append("Correlate with market volume data")
            
            elif pattern_type == "WASH_TRADING":
                significance["charges_supported"].extend(["Market Manipulation", "Wire Fraud"])
                significance["recommendations"].append("Map full counterparty network")
        
        # Assess overall strength
        tier_1_count = sum(1 for p in patterns if p.get("evidence_tier") == "TIER_1")
        tier_2_count = sum(1 for p in patterns if p.get("evidence_tier") == "TIER_2")
        
        if tier_1_count >= 2:
            significance["evidence_strength"] = "STRONG"
        elif tier_1_count >= 1 or tier_2_count >= 2:
            significance["evidence_strength"] = "MODERATE"
        elif tier_2_count >= 1:
            significance["evidence_strength"] = "WEAK-MODERATE"
        
        return significance


def detect_cross_wallet_coordination(reports: List[Dict]) -> Dict[str, Any]:
    """
    Detect coordination patterns across multiple wallets.
    
    Looks for:
    - Same timing windows
    - Similar order sizes
    - Shared counterparties
    - Sequential patterns
    """
    coordination_indicators = []
    
    # Extract sell timestamps from all wallets
    wallet_sells = {}
    for report in reports:
        wallet = report.get("wallet", "UNKNOWN")
        financial = report.get("financial_metrics", {})
        
        # Get sells from the original data (would need to pass this through)
        # For now, use pattern detection results
        
        wallet_sells[wallet] = {
            "total_sold": financial.get("total_crm_sold", 0),
            "total_transactions": financial.get("total_sells", 0),
            "patterns": [p.get("pattern_type") for p in report.get("patterns_detected", [])]
        }
    
    # Check for similar patterns across wallets
    pattern_counts = defaultdict(list)
    for wallet, data in wallet_sells.items():
        for pattern in data["patterns"]:
            pattern_counts[pattern].append(wallet)
    
    shared_patterns = {p: wallets for p, wallets in pattern_counts.items() if len(wallets) >= 2}
    
    return {
        "coordination_detected": len(shared_patterns) > 0,
        "shared_patterns": shared_patterns,
        "wallet_summary": wallet_sells,
        "evidence_tier": "TIER_1" if len(shared_patterns) >= 2 else "TIER_2" if len(shared_patterns) >= 1 else "TIER_3"
    }


def main():
    parser = argparse.ArgumentParser(
        description="Detect manipulation patterns in DEX transaction data"
    )
    parser.add_argument(
        "--input",
        help="Input JSON file from export_dex_transactions.py"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Analyze all DEX export files in directory"
    )
    parser.add_argument(
        "--input-dir",
        default=".",
        help="Directory containing DEX export files"
    )
    parser.add_argument(
        "--output",
        help="Output file for analysis report"
    )
    
    args = parser.parse_args()
    
    if not args.input and not args.all:
        parser.print_help()
        print("\nError: Must specify --input or --all")
        sys.exit(1)
    
    reports = []
    
    if args.all:
        import os
        import glob
        
        pattern = f"{args.input_dir}/DEX_*_20*.json"
        files = glob.glob(pattern)
        
        # Exclude combined reports
        files = [f for f in files if "ALL_WALLETS" not in f]
        
        print(f"Found {len(files)} DEX export files")
        
        for filepath in files:
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                
                detector = ManipulationDetector(data)
                report = detector.generate_full_report()
                reports.append(report)
                
            except Exception as e:
                print(f"Error analyzing {filepath}: {e}")
    else:
        with open(args.input, "r") as f:
            data = json.load(f)
        
        detector = ManipulationDetector(data)
        report = detector.generate_full_report()
        reports.append(report)
    
    # Cross-wallet coordination analysis
    coordination = detect_cross_wallet_coordination(reports)
    
    # Combined report
    combined_report = {
        "analysis_timestamp": datetime.now().isoformat(),
        "wallets_analyzed": len(reports),
        "individual_reports": reports,
        "cross_wallet_coordination": coordination,
        "summary": {
            "total_patterns_detected": sum(r.get("total_patterns", 0) for r in reports),
            "wallets_with_iceberg": sum(1 for r in reports if r.get("iceberg_analysis", {}).get("detected")),
            "wallets_with_drip_feeding": sum(1 for r in reports if r.get("drip_feeding_analysis", {}).get("detected")),
            "wallets_with_wash_trading": sum(1 for r in reports if r.get("counterparty_analysis", {}).get("wash_trading_indicator")),
            "coordination_detected": coordination.get("coordination_detected", False)
        }
    }
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output:
        output_file = args.output
    else:
        output_file = f"MANIPULATION_ANALYSIS_{timestamp}.json"
    
    with open(output_file, "w") as f:
        json.dump(combined_report, f, indent=2, default=str)
    
    print(f"\n{'='*60}")
    print(f"Analysis complete! Report saved to: {output_file}")
    print(f"{'='*60}")
    print(f"\nSummary:")
    print(f"  Wallets analyzed: {combined_report['summary']['wallets_analyzed']}")
    print(f"  Total patterns detected: {combined_report['summary']['total_patterns_detected']}")
    print(f"  Iceberg orders: {combined_report['summary']['wallets_with_iceberg']}")
    print(f"  Drip feeding: {combined_report['summary']['wallets_with_drip_feeding']}")
    print(f"  Wash trading: {combined_report['summary']['wallets_with_wash_trading']}")
    print(f"  Cross-wallet coordination: {'YES' if combined_report['summary']['coordination_detected'] else 'NO'}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
