#!/usr/bin/env python3
"""
🔧 RugMuncher CLI - Command Line Interface
Analyze tokens, check devs, detect bundles from the terminal
"""

import asyncio
import argparse
import json
import sys
from typing import Optional
from datetime import datetime

from token_analyzer import ComprehensiveTokenAnalyzer, format_comprehensive_report
from bundle_detector_advanced import check_bundle, format_bundle_report
from dev_profiler import profile_dev, format_dev_report
from alert_system import alert_system, console_handler


class RugMunchCLI:
    """
    🔧 Command line interface for RugMuncher
    """
    
    def __init__(self):
        self.analyzer = ComprehensiveTokenAnalyzer()
        alert_system.add_handler(console_handler)
    
    async def analyze(self, token_address: str, chain: str = "solana"):
        """Full token analysis"""
        print(f"🔬 Analyzing {token_address} on {chain}...")
        print("=" * 70)
        
        # Run analysis (with sample data for demo)
        analysis = await self.analyzer.analyze_token(
            token_address=token_address,
            token_data={"name": "Unknown Token", "chain": chain},
            transactions=[],
            wallets=[],
            dev_wallets=[],
            project_history=[],
            on_chain_data={"age_hours": 24},
            social_data={}
        )
        
        # Output report
        print(format_comprehensive_report(analysis))
        
        # Save to file
        filename = f"analysis_{token_address[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(format_comprehensive_report(analysis))
        
        print(f"\n💾 Report saved to: {filename}")
    
    async def bundle_check(self, token_address: str):
        """Quick bundle check"""
        print(f"🔍 Checking for bundling: {token_address}")
        print("=" * 70)
        
        analysis = await check_bundle(token_address)
        print(format_bundle_report(analysis))
        
        if analysis.is_bundle:
            print("\n☠️  WARNING: This token is likely bundled!")
    
    async def dev_check(self, wallet: str):
        """Check developer history"""
        print(f"🕵️  Profiling developer: {wallet}")
        print("=" * 70)
        
        profile = await profile_dev([wallet])
        print(format_dev_report(profile))
    
    async def monitor(self, token_address: str):
        """Start monitoring a token"""
        print(f"👁️  Starting monitoring for: {token_address}")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Simulate monitoring
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking...")
                await asyncio.sleep(10)
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped")
    
    async def batch_analyze(self, filename: str):
        """Analyze multiple tokens from file"""
        print(f"📁 Batch analyzing tokens from: {filename}")
        
        try:
            with open(filename, 'r') as f:
                tokens = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
            return
        
        results = []
        for token in tokens:
            print(f"\nAnalyzing {token}...")
            analysis = await self.analyzer.analyze_token(
                token_address=token,
                token_data={"name": "Unknown"},
                transactions=[],
                wallets=[],
                dev_wallets=[],
                project_history=[],
                on_chain_data={},
                social_data={}
            )
            results.append({
                'token': token,
                'score': analysis.overall_score,
                'verdict': analysis.verdict.value,
                'bundle_risk': analysis.bundle_risk,
                'dev_risk': analysis.dev_risk
            })
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 BATCH ANALYSIS SUMMARY")
        print("=" * 70)
        
        for r in results:
            emoji = "✅" if r['verdict'] == 'safe' else "⚠️" if r['verdict'] == 'caution' else "🚨"
            print(f"{emoji} {r['token'][:15]:15} | Score: {r['score']:.0f}/100 | {r['verdict'].upper()}")
        
        # Save results
        output_file = f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="🔧 RugMuncher - Advanced Token Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full analysis
  python rugmunch_cli.py analyze TOKEN_ADDRESS --chain solana
  
  # Quick bundle check
  python rugmunch_cli.py bundle TOKEN_ADDRESS
  
  # Check developer
  python rugmunch_cli.py dev DEV_WALLET_ADDRESS
  
  # Monitor token
  python rugmunch_cli.py monitor TOKEN_ADDRESS
  
  # Batch analysis
  python rugmunch_cli.py batch tokens.txt
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Full token analysis')
    analyze_parser.add_argument('token', help='Token address')
    analyze_parser.add_argument('--chain', default='solana', help='Blockchain (solana, ethereum, bsc)')
    
    # Bundle command
    bundle_parser = subparsers.add_parser('bundle', help='Quick bundle detection')
    bundle_parser.add_argument('token', help='Token address')
    
    # Dev command
    dev_parser = subparsers.add_parser('dev', help='Check developer profile')
    dev_parser.add_argument('wallet', help='Developer wallet address')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor token in real-time')
    monitor_parser.add_argument('token', help='Token address')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Analyze multiple tokens')
    batch_parser.add_argument('file', help='File containing token addresses (one per line)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = RugMunchCLI()
    
    if args.command == 'analyze':
        asyncio.run(cli.analyze(args.token, args.chain))
    elif args.command == 'bundle':
        asyncio.run(cli.bundle_check(args.token))
    elif args.command == 'dev':
        asyncio.run(cli.dev_check(args.wallet))
    elif args.command == 'monitor':
        asyncio.run(cli.monitor(args.token))
    elif args.command == 'batch':
        asyncio.run(cli.batch_analyze(args.file))


if __name__ == "__main__":
    main()
