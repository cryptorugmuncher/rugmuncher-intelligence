#!/usr/bin/env python3
"""
🚀 AI SWARM LAUNCHER
Start the multi-AI bot swarm with all survival mechanics enabled
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, "/root")

from ai_swarm_orchestrator import AISwarmOrchestrator, demo_swarm, ConsensusLevel


def check_api_keys():
    """Verify API keys are set"""
    nvidia_key = os.getenv("NVIDIA_API_KEY", "")
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")

    print("🔑 API Key Status:")
    print(
        f"   NVIDIA: {'✅ Set' if nvidia_key and nvidia_key.startswith('nvapi-') else '❌ Missing'}"
    )
    print(f"   OpenRouter: {'✅ Set' if openrouter_key else '❌ Missing'}")

    if not nvidia_key or not nvidia_key.startswith("nvapi-"):
        print("\n⚠️  Set NVIDIA_API_KEY:")
        print("   export NVIDIA_API_KEY=nvapi-xxxxx")

    if not openrouter_key:
        print("\n⚠️  Set OPENROUTER_API_KEY:")
        print("   export OPENROUTER_API_KEY=sk-or-v1-xxxxx")

    return bool(nvidia_key and openrouter_key)


async def interactive_mode(swarm):
    """Interactive swarm control"""

    print("""
╔══════════════════════════════════════════════════════════════════╗
║           🎮 INTERACTIVE SWARM CONTROL                           ║
╠══════════════════════════════════════════════════════════════════╣
║  Commands:                                                        ║
║    status     - Show swarm status                                 ║
║    bots       - List all bots with survival scores                ║
║    task       - Assign a task to the swarm                      ║
║    code       - Generate code with 6-layer verification         ║
║    consensus  - Run a consensus vote                              ║
║    terminate  - Terminate a poorly performing bot               ║
║    backup     - Force backup all bots                           ║
║    graveyard  - View terminated bots                              ║
║    help       - Show this help                                    ║
║    quit       - Exit (swarm continues in background)            ║
╚══════════════════════════════════════════════════════════════════╝
""")

    while True:
        try:
            cmd = input("\n🐝 swarm> ").strip().lower()

            if cmd == "quit":
                print("👋 Exiting interactive mode. Swarm continues in background.")
                break

            elif cmd == "status":
                status = swarm.get_swarm_status()
                print(f"\n🐝 Swarm Status:")
                print(
                    f"   Total: {status['total_bots']} | Alive: {status['alive']} | Terminated: {status['terminated']}"
                )
                print(f"   Avg Survival Score: {status['avg_survival_score']:.2f}")
                print(
                    f"   Tasks: {status['tasks_completed']} completed, {status['tasks_failed']} failed"
                )
                print(f"   Consensus Decisions: {status['consensus_decisions']}")

            elif cmd == "bots":
                status = swarm.get_swarm_status()
                print(f"\n🤖 Bot Status (Top 10):")
                for bot in status["bots"]:
                    status_emoji = (
                        "🟢"
                        if bot["status"] == "alive"
                        else "🟡"
                        if bot["status"] == "warning"
                        else "☠️"
                    )
                    print(
                        f"   {status_emoji} {bot['name'][:30]:30} | Score: {bot['survival_score']:.2f} | Age: {bot['age_hours']}h | Tasks: {bot['tasks']}"
                    )

            elif cmd == "task":
                task_type = input(
                    "Task type (code_generation/code_review/analysis): "
                ).strip()
                task_prompt = input("Task description: ").strip()

                result = await swarm.assign_task(
                    task_type=task_type,
                    task_data={"prompt": task_prompt, "purpose": task_prompt},
                    require_consensus=True,
                )

                if result.get("success"):
                    print(f"\n✅ Task completed by {result.get('bot')}")
                    print(
                        f"Result: {result.get('result', {}).get('text', '')[:200]}..."
                    )
                else:
                    print(f"\n❌ Task failed: {result.get('error')}")

            elif cmd == "code":
                language = (
                    input("Language (python/javascript/etc): ").strip() or "python"
                )
                purpose = input("What should the code do? ").strip()

                print(f"\n🔨 Generating {language} code with 6-layer verification...")
                print("   Layer 1: Syntax validation")
                print("   Layer 2: Static analysis")
                print("   Layer 3: Security scan")
                print("   Layer 4: Test generation")
                print("   Layer 5: Peer review")
                print("   Layer 6: Consensus approval")

                result = await swarm.assign_task(
                    task_type="code_generation",
                    task_data={
                        "language": language,
                        "purpose": purpose,
                        "code_requirements": purpose,
                    },
                    require_consensus=True,
                )

                if result.get("success"):
                    print(f"\n✅ ALL 6 LAYERS PASSED")
                    print(f"🤖 Generated by: {result.get('bot')}")
                    print(f"\n--- CODE ---")
                    print(result.get("code", "")[:500])
                    if len(result.get("code", "")) > 500:
                        print("... (truncated)")
                else:
                    print(f"\n❌ FAILED at Layer {result.get('layer')}")
                    print(f"Error: {result.get('error')}")

            elif cmd == "consensus":
                proposal = input("Proposal to vote on: ").strip()

                print(f"\n🗳️  Calling Consensus Council...")
                decision = await swarm.consensus_council.propose(
                    proposal=proposal,
                    context="Manual consensus request",
                    level=ConsensusLevel.MAJORITY,
                )

                print(f"\nDecision: {decision.final_decision.upper()}")
                print(f"Approval Rate: {decision.approval_rate * 100:.1f}%")
                print(f"Total Votes: {len(decision.votes)}")

                if decision.votes:
                    print(f"\nVote breakdown:")
                    for v in decision.votes[:5]:
                        emoji = "✅" if v.decision == "approve" else "❌"
                        print(
                            f"   {emoji} {v.bot_id[:20]:20} | {v.decision} | {v.confidence * 100:.0f}%"
                        )

            elif cmd == "terminate":
                bot_id = input("Bot ID to terminate: ").strip()
                reason = (
                    input("Reason for termination: ").strip() or "Manual termination"
                )

                confirm = input(
                    f"☠️  Are you sure you want to terminate {bot_id}? (yes/no): "
                ).strip()
                if confirm.lower() == "yes":
                    await swarm.terminate_bot(bot_id, reason)
                    print(f"☠️  {bot_id} has been terminated")
                else:
                    print("Termination cancelled")

            elif cmd == "backup":
                print("💾 Forcing backup of all bots...")
                for bot in swarm.bots:
                    if bot.status.value == "alive":
                        await swarm._backup_bot(bot)
                print("✅ All bots backed up")

            elif cmd == "graveyard":
                if swarm.graveyard:
                    print(f"\n☠️  Graveyard ({len(swarm.graveyard)} terminated bots):")
                    for bot in swarm.graveyard:
                        print(
                            f"   • {bot.name} | Score: {bot.survival_score:.2f} | Hallucinations: {bot.hallucination_count}"
                        )
                else:
                    print("\n✨ No bots in graveyard (all are alive!)")

            elif cmd == "containment":
                print("\n🛡️  Containment Status:")
                if swarm.comm_coordinator:
                    report = swarm.comm_coordinator.get_containment_report()
                    print(f"   Active Containers: {report['total_containers']}")
                    print(f"   Communications Logged: {report['total_communications']}")
                    print(f"   Pending Approvals: {report['pending_approvals']}")
                    print(f"   Collusion Alerts: {report['collusion_alerts']}")

                    if report["isolated_bots"]:
                        print(f"\n   ⚠️  Isolated Bots:")
                        for info in report["isolated_bots"]:
                            print(
                                f"      • {info['bot_id'][:25]:25} | Suspicion: {info['suspicion_score']:.2f}"
                            )

                    if report["recent_comms"]:
                        print(f"\n   📡 Recent Communications:")
                        for comm in report["recent_comms"][-5:]:
                            emoji = (
                                "🚫"
                                if not comm["approved"]
                                else "✅"
                                if not comm["flagged"]
                                else "⚠️"
                            )
                            print(
                                f"      {emoji} {comm['source'][:15]:15} → {comm['target'][:15]:15} ({comm['type']})"
                            )
                else:
                    print("   ⚠️  Communication coordinator not initialized")

            elif cmd == "isolate":
                bot_id = input("Bot ID to isolate: ").strip()
                bot = next((b for b in swarm.bots if b.id == bot_id), None)
                if bot:
                    bot.status = swarm.BotStatus.ISOLATED
                    print(f"🛡️  {bot.name} has been ISOLATED - communication restricted")
                    print("   Bot can only communicate with coordinator")
                else:
                    print(f"❌ Bot {bot_id} not found")

            elif cmd == "release":
                bot_id = input("Bot ID to release: ").strip()
                bot = next((b for b in swarm.bots if b.id == bot_id), None)
                if bot and bot.status.value == "isolated":
                    bot.status = swarm.BotStatus.ALIVE
                    # Reset suspicion in container
                    if bot_id in swarm.comm_coordinator.containers:
                        swarm.comm_coordinator.containers[bot_id].suspicion_score = 0.0
                    print(f"✅ {bot.name} has been RELEASED from isolation")
                else:
                    print(f"❌ Bot {bot_id} not found or not isolated")

            elif cmd == "test_comm":
                source = input("Source bot ID: ").strip()
                target = input("Target bot ID (or 'COORDINATOR'): ").strip()
                msg_type = (
                    input(
                        "Message type (peer_review/consensus/task/emergency): "
                    ).strip()
                    or "task"
                )
                msg = input("Message content: ").strip() or "Test message"

                from ai_swarm_orchestrator import CommType

                comm_type = getattr(CommType, msg_type.upper(), CommType.TASK_RESULT)

                result = await swarm.comm_coordinator.send_message(
                    source, target, comm_type, msg
                )

                if result.get("blocked"):
                    print(f"\n🚫 COMMUNICATION BLOCKED")
                    print(f"   Reason: {result.get('error', 'Containment policy')}")
                elif result.get("pending"):
                    print(f"\n⏸️  COMMUNICATION HELD FOR APPROVAL")
                    print(f"   Event ID: {result.get('event_id')}")
                elif result.get("flagged"):
                    print(f"\n⚠️  COMMUNICATION ALLOWED BUT FLAGGED")
                    print(f"   Patterns: {result.get('flagged')}")
                else:
                    print(f"\n✅ COMMUNICATION APPROVED")

            elif cmd == "crypto_train":
                print("\n🎓 CRYPTO SCAM DETECTION TRAINING")
                print("=" * 50)

                # Import training module
                from crypto_training_module import (
                    SwarmCryptoTrainingIntegration,
                    TrainingLevel,
                )

                integration = SwarmCryptoTrainingIntegration(swarm)

                # Interactive parameter collection
                level_str = (
                    input(
                        "Level (beginner/intermediate/advanced/expert/master/progressive) [progressive]: "
                    ).strip()
                    or "progressive"
                )
                duration_str = input("Duration in minutes [60]: ").strip() or "60"
                duration = int(duration_str)

                level_map = {
                    "beginner": TrainingLevel.BEGINNER,
                    "intermediate": TrainingLevel.INTERMEDIATE,
                    "advanced": TrainingLevel.ADVANCED,
                    "expert": TrainingLevel.EXPERT,
                    "master": TrainingLevel.MASTER,
                }

                print(f"Level: {level_str}, Duration: {duration}min")
                print(
                    f"Bots available: {len(swarm.bots) if hasattr(swarm, 'bots') else 0}"
                )

                result = await integration.start_crypto_training(duration)

                if "error" in result:
                    print(f"❌ {result['error']}")
                else:
                    print(f"\n✅ Training Initiated: {result['training_session_id']}")
                    print(f"   Total tasks assigned: {result['total_tasks']}")
                    print(f"   Rounds: {len(result['rounds'])}")
                    print(f"   Containment: {result['containment_architecture']}")

                    for i, round_data in enumerate(result["rounds"]):
                        print(f"\n   Round {i + 1} ({round_data['level']}):")
                        print(f"     Tasks: {round_data['tasks_assigned']}")
                        print(
                            f"     Cross-provider reviews: {round_data['cross_provider_reviews']}"
                        )

            elif cmd == "wallet_forensics":
                print("\n🔍 WALLET FORENSICS TRAINING")
                print("=" * 50)

                from crypto_training_module import CryptoTrainingDataManager

                data_manager = CryptoTrainingDataManager()
                case = data_manager.get_wallet_forensics_case()

                print(f"Case ID: {case['case_id']}")
                print(f"Difficulty: {case['difficulty']}")
                print(f"Wallets to analyze: {case['contracts_analyzed']}")
                print(f"Expected pattern: {case['expected_pattern']}")
                print(f"\nRed flags: {', '.join(case['red_flags'])}")

                # Find analysis-capable bots
                analysis_bots = []
                if hasattr(swarm, "bots"):
                    for bot_id in swarm.bots.keys():
                        if any(
                            x in bot_id.lower() for x in ["deepseek", "mistral", "qwen"]
                        ):
                            analysis_bots.append(bot_id)

                if analysis_bots:
                    print(f"\nAssigning to: {analysis_bots[0]}")
                    # Would call: await swarm.assign_task(analysis_bots[0], task_data)
                else:
                    print("\n⚠️ No analysis bots available")

            elif cmd == "pattern_drill":
                print("\n🎯 SCAM PATTERN DRILL")
                print("=" * 50)

                import random
                from crypto_training_module import CryptoTrainingDataManager

                data_manager = CryptoTrainingDataManager()

                print("\nAvailable patterns:")
                for i, p in enumerate(data_manager.scam_patterns, 1):
                    severity_icon = (
                        "🔴"
                        if p.severity == "CRITICAL"
                        else "🟠"
                        if p.severity == "HIGH"
                        else "🟡"
                    )
                    print(f"  {i}. {p.pattern_id}: {severity_icon} {p.name}")

                # Random drill
                pattern = random.choice(data_manager.scam_patterns)
                print(f"\n{'=' * 50}")
                print(f"🧩 IDENTIFY THIS PATTERN:")
                print(f"{'=' * 50}")
                print(f"Indicators:")
                for ind in pattern.indicators[:3]:
                    print(f"  • {ind}")

                answer = (
                    input("\nYour answer (pattern ID, e.g., RP001): ").strip().upper()
                )

                if answer == pattern.pattern_id:
                    print(f"✅ CORRECT! {pattern.pattern_id}: {pattern.name}")
                    print(f"   {pattern.description}")
                else:
                    print(f"❌ WRONG. Answer: {pattern.pattern_id}")
                    print(f"   {pattern.description}")
                    print(f"   Indicators: {', '.join(pattern.indicators)}")

            elif cmd == "directive":
                print("\n🎯 STRATEGIC DIRECTIVE SYSTEM")
                print("=" * 50)

                if not hasattr(swarm, "strategic_orchestrator"):
                    from swarm_strategic_orchestrator import StrategicOrchestrator

                    swarm.strategic_orchestrator = StrategicOrchestrator(swarm)
                    print("✅ Strategic orchestrator initialized")

                orchestrator = swarm.strategic_orchestrator

                subcmd = input(
                    "Subcommand (create/execute/list/status/parallel): "
                ).strip()

                if subcmd == "create":
                    name = input("Directive name: ").strip()
                    description = input("Description: ").strip()
                    priority = (
                        input("Priority (critical/high/normal/low): ").strip()
                        or "normal"
                    )

                    from swarm_strategic_orchestrator import TaskPriority

                    priority_map = {
                        "critical": TaskPriority.CRITICAL,
                        "high": TaskPriority.HIGH,
                        "normal": TaskPriority.NORMAL,
                        "low": TaskPriority.LOW,
                    }

                    success_criteria = (
                        input("Success criteria (comma-separated): ").strip().split(",")
                    )
                    success_criteria = [
                        s.strip() for s in success_criteria if s.strip()
                    ]

                    directive = await orchestrator.create_strategic_directive(
                        name=name,
                        description=description,
                        priority=priority_map.get(priority, TaskPriority.NORMAL),
                        success_criteria=success_criteria,
                    )

                    print(f"\n✅ Directive created: {directive.directive_id}")
                    print(f"   Name: {directive.name}")
                    print(f"   Subtasks: {len(directive.sub_tasks)}")
                    for st in directive.sub_tasks[:5]:
                        print(
                            f"      • {st.get('id')}: {st.get('description', '')[:40]}..."
                        )

                elif subcmd == "execute":
                    directive_id = input("Directive ID: ").strip()
                    print(f"\n🚀 Executing directive...")
                    result = await orchestrator.execute_directive(directive_id)

                    if result.get("success"):
                        print(f"✅ Directive completed successfully")
                        print(
                            f"   Subtasks completed: {len(result.get('results', []))}"
                        )
                    else:
                        print(f"❌ Directive failed or partially completed")
                        if result.get("error"):
                            print(f"   Error: {result['error']}")

                elif subcmd == "list":
                    directives = orchestrator.list_directives()
                    print(f"\n📋 Active Directives ({len(directives)}):")
                    for d in directives:
                        print(
                            f"   • {d['id']}: {d['name']} [{d['status']}] ({d['priority']})"
                        )

                elif subcmd == "status":
                    directive_id = input("Directive ID: ").strip()
                    status = orchestrator.get_directive_status(directive_id)

                    if status:
                        print(f"\n🎯 Directive Status:")
                        print(f"   Name: {status['name']}")
                        print(f"   Status: {status['status']}")
                        print(f"   Priority: {status['priority']}")
                        print(f"   Subtasks: {status['subtasks_total']}")
                        print(f"   Criteria: {', '.join(status['success_criteria'])}")
                    else:
                        print(f"❌ Directive not found")

                elif subcmd == "parallel":
                    topic = input("Topic to analyze: ").strip()
                    question = input("Specific question: ").strip()
                    num_bots = int(input("Number of bots (default 3): ").strip() or "3")

                    print(f"\n🤖 Running parallel analysis with {num_bots} bots...")
                    result = await orchestrator.execute_parallel_analysis(
                        topic=topic, question=question, num_bots=num_bots
                    )

                    print(f"\n📊 Results:")
                    print(f"   Bots used: {', '.join(result['bots_used'])}")

                    if "synthesis" in result and result["synthesis"]:
                        synth = result["synthesis"]
                        if "consensus_findings" in synth:
                            print(f"\n✓ Consensus Findings:")
                            for finding in synth["consensus_findings"][:5]:
                                print(f"      • {finding}")

                        if "synthesized_conclusion" in synth:
                            print(f"\n📌 Conclusion:")
                            print(f"   {synth['synthesized_conclusion'][:300]}...")

                        if "recommended_actions" in synth:
                            print(f"\n🎯 Recommended Actions:")
                            for action in synth["recommended_actions"][:3]:
                                print(f"      • {action}")

            elif cmd == "templates":
                print("\n📝 PROMPT TEMPLATES")
                print("=" * 50)

                if not hasattr(swarm, "strategic_orchestrator"):
                    from swarm_strategic_orchestrator import StrategicOrchestrator

                    swarm.strategic_orchestrator = StrategicOrchestrator(swarm)

                templates = swarm.strategic_orchestrator.prompt_engine.list_templates()

                print(f"Available templates ({len(templates)}):")
                for t in templates:
                    print(f"\n   {t['id']}:")
                    print(f"      Name: {t['name']}")
                    print(f"      Variables: {', '.join(t['variables'])}")
                    print(f"      Specialties: {', '.join(t['specialties'])}")

            elif cmd == "expertise":
                print("\n🎓 EXPERTISE-AWARE EXECUTION")
                print("=" * 50)

                if not hasattr(swarm, "enhanced_orchestrator"):
                    from swarm_enhanced_orchestrator import EnhancedSwarmOrchestrator

                    swarm.enhanced_orchestrator = EnhancedSwarmOrchestrator(swarm)
                    print("✅ Enhanced orchestrator initialized")

                print("Available expertise areas:")
                print("   • contract_audit")
                print("   • wallet_analysis")
                print("   • scam_detection")
                print("   • social_analysis")
                print("   • fund_tracing")
                print("   • forensic_accounting")
                print("   • pattern_analysis")
                print("   • code_generation")
                print("   • security_audit")

                task_type = input("\nTask type: ").strip()
                description = input("Task description: ").strip()

                print(f"\n🎯 Executing with expertise-aware routing...")
                result = await swarm.enhanced_orchestrator.execute_with_expertise(
                    task_type=task_type,
                    task_data={"description": description, "prompt": description},
                    require_consensus=True,
                )

                if result.get("success"):
                    print(f"✅ Task completed successfully")
                    print(f"   Bot: {result.get('bot', 'N/A')}")
                    print(f"   Expertise: {result.get('expertise', 'N/A')}")
                    if "synthesis" in result:
                        print(f"   Parallel analysis performed")
                else:
                    print(f"❌ Task failed: {result.get('error', 'Unknown error')}")

            elif cmd == "help":
                print("""
Commands:
  status         - Show swarm status
  bots           - List all bots with survival scores
  task           - Assign a task to the swarm
  code           - Generate code with 6-layer verification
  consensus      - Run a consensus vote
  terminate      - Terminate a poorly performing bot
  backup         - Force backup all bots
  graveyard      - View terminated bots
  containment    - View containment status (isolated bots, comm logs)
  isolate        - Manually isolate a bot (restrict communication)
  release        - Release an isolated bot
  test_comm      - Test communication between bots
  
  🎯 STRATEGIC ORCHESTRATION:
  directive      - Create and manage strategic directives
  templates      - List available prompt templates
  parallel       - Run parallel multi-bot analysis
  expertise      - Execute with expertise-aware routing
  
  🎓 TRAINING & DEVELOPMENT:
  crypto_train   - Start crypto scam detection training
  wallet_forensics - Train on wallet analysis cases
  pattern_drill  - Quick scam pattern identification drill
  
  help           - Show this help
  quit           - Exit (swarm continues in background)
""")

            else:
                print(f"Unknown command: {cmd}. Type 'help' for available commands.")

        except KeyboardInterrupt:
            print("\n\n👋 Use 'quit' to exit properly")
        except Exception as e:
            print(f"Error: {e}")


async def main():
    parser = argparse.ArgumentParser(description="AI Swarm Orchestrator")
    parser.add_argument("--demo", action="store_true", help="Run demo and exit")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )
    parser.add_argument(
        "--lifecycle", action="store_true", help="Start lifecycle manager"
    )
    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════════════╗
║           🤖 AI SWARM ORCHESTRATOR                               ║
║           Multi-AI Bot Manager with Survival Mechanics           ║
╚══════════════════════════════════════════════════════════════════╝
""")

    # Check API keys
    if not check_api_keys():
        print("\n⚠️  Some API keys are missing. Swarm will run with limited capacity.")

    # Initialize swarm
    print("\n🐝 Initializing AI Swarm...")
    swarm = AISwarmOrchestrator()

    # Start lifecycle manager in background if requested
    if args.lifecycle:
        print("⏰ Starting lifecycle manager (24h context wipe, survival checks)...")
        asyncio.create_task(swarm.lifecycle_manager())

    if args.demo:
        print("\n🎬 Running demo...")
        await demo_swarm()
    elif args.interactive:
        await interactive_mode(swarm)
    else:
        # Default: show status and enter interactive mode
        status = swarm.get_swarm_status()
        print(f"\n🐝 Swarm initialized with {status['alive']} active bots")
        print("   Run with --lifecycle to enable 24h survival mechanics")
        print("   Entering interactive mode (type 'quit' to exit)...\n")
        await interactive_mode(swarm)


if __name__ == "__main__":
    asyncio.run(main())
