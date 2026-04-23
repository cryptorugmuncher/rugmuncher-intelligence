#!/usr/bin/env python3
"""
🎓 ENHANCED SWARM ORCHESTRATOR
Integrates specialized training modules with strategic direction

This module bridges:
- SpecializedTrainingOrchestrator (training modules)
- StrategicOrchestrator (direction & prompting)
- AISwarmOrchestrator (base swarm management)

Provides:
1. Expertise-Aware Task Routing - Match tasks to trained expertise
2. Training-Driven Prompting - Use training content in prompts
3. Progressive Skill Building - Adaptive difficulty
4. Cross-Domain Synthesis - Combine multiple expertise areas
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger("ENHANCED_ORCHESTRATOR")


@dataclass
class ExpertiseTaskMapping:
    """Maps task types to required expertise"""

    task_type: str
    primary_expertise: str
    secondary_expertise: List[str]
    minimum_skill_level: str
    verification_required: bool = True
    parallel_analysis: bool = False


@dataclass
class TrainingEnhancedPrompt:
    """Prompt enhanced with training module content"""

    base_prompt: str
    expertise_context: str
    training_examples: List[Dict]
    red_flags: List[str]
    verification_checklist: List[str]
    output_format: str


class EnhancedSwarmOrchestrator:
    """
    🎓 Enhanced Orchestrator with Training Integration

    Combines strategic direction with specialized training to provide
    expert-level execution across all domains.
    """

    def __init__(self, swarm):
        self.swarm = swarm
        self.expertise_mappings: Dict[str, ExpertiseTaskMapping] = {}
        self.active_trainings: Dict[str, Any] = {}
        self.task_expertise_cache: Dict[str, Dict] = {}

        # Initialize components
        self._init_strategic_orchestrator()
        self._init_training_orchestrator()
        self._init_expertise_mappings()

    def _init_strategic_orchestrator(self):
        """Initialize strategic orchestrator for direction"""
        try:
            from swarm_strategic_orchestrator import StrategicOrchestrator

            self.strategic = StrategicOrchestrator(self.swarm)
            logger.info("Strategic orchestrator initialized")
        except Exception as e:
            logger.warning(f"Strategic orchestrator not available: {e}")
            self.strategic = None

    def _init_training_orchestrator(self):
        """Initialize training orchestrator for expertise"""
        try:
            from swarm_specialized_training import (
                SpecializedTrainingOrchestrator,
                ExpertiseArea,
            )

            self.training = SpecializedTrainingOrchestrator()
            self.ExpertiseArea = ExpertiseArea
            logger.info("Training orchestrator initialized")
        except Exception as e:
            logger.warning(f"Training orchestrator not available: {e}")
            self.training = None

    def _init_expertise_mappings(self):
        """Initialize task-to-expertise mappings"""

        self.expertise_mappings = {
            # Crypto/Blockchain Analysis
            "contract_audit": ExpertiseTaskMapping(
                task_type="contract_audit",
                primary_expertise="scam_detection",
                secondary_expertise=["pattern_recognition", "forensic_accounting"],
                minimum_skill_level="EXPERT",
                verification_required=True,
                parallel_analysis=True,
            ),
            "wallet_analysis": ExpertiseTaskMapping(
                task_type="wallet_analysis",
                primary_expertise="fund_tracing",
                secondary_expertise=["forensic_accounting", "pattern_recognition"],
                minimum_skill_level="EXPERT",
                verification_required=True,
                parallel_analysis=False,
            ),
            "scam_detection": ExpertiseTaskMapping(
                task_type="scam_detection",
                primary_expertise="scam_detection",
                secondary_expertise=["social_manipulation", "pattern_recognition"],
                minimum_skill_level="PROFICIENT",
                verification_required=True,
                parallel_analysis=True,
            ),
            "social_analysis": ExpertiseTaskMapping(
                task_type="social_analysis",
                primary_expertise="social_manipulation",
                secondary_expertise=["psychological_profiling", "pattern_recognition"],
                minimum_skill_level="PROFICIENT",
                verification_required=True,
                parallel_analysis=True,
            ),
            "fund_tracing": ExpertiseTaskMapping(
                task_type="fund_tracing",
                primary_expertise="fund_tracing",
                secondary_expertise=["forensic_accounting"],
                minimum_skill_level="MASTER",
                verification_required=True,
                parallel_analysis=True,
            ),
            "forensic_accounting": ExpertiseTaskMapping(
                task_type="forensic_accounting",
                primary_expertise="forensic_accounting",
                secondary_expertise=["fund_tracing"],
                minimum_skill_level="EXPERT",
                verification_required=True,
                parallel_analysis=False,
            ),
            # General Development
            "code_generation": ExpertiseTaskMapping(
                task_type="code_generation",
                primary_expertise="coding",
                secondary_expertise=["analysis", "reasoning"],
                minimum_skill_level="PROFICIENT",
                verification_required=True,
                parallel_analysis=False,
            ),
            "security_audit": ExpertiseTaskMapping(
                task_type="security_audit",
                primary_expertise="security_review",
                secondary_expertise=["analysis", "coding"],
                minimum_skill_level="EXPERT",
                verification_required=True,
                parallel_analysis=True,
            ),
            "pattern_analysis": ExpertiseTaskMapping(
                task_type="pattern_analysis",
                primary_expertise="pattern_recognition",
                secondary_expertise=["analysis", "reasoning"],
                minimum_skill_level="EXPERT",
                verification_required=True,
                parallel_analysis=True,
            ),
        }

        logger.info(f"Initialized {len(self.expertise_mappings)} expertise mappings")

    async def execute_with_expertise(
        self, task_type: str, task_data: Dict, require_consensus: bool = True
    ) -> Dict:
        """
        Execute a task with expertise-aware routing and training-enhanced prompting
        """

        # Get expertise mapping
        mapping = self.expertise_mappings.get(task_type)

        if not mapping or not self.training:
            # Fallback to standard execution
            return await self.swarm.assign_task(task_type, task_data, require_consensus)

        logger.info(f"Executing {task_type} with expertise-aware routing")

        # Step 1: Select bots with appropriate expertise
        selected_bots = self._select_bots_for_expertise(mapping)

        if not selected_bots:
            logger.warning(
                f"No bots available for {mapping.primary_expertise}, using fallback"
            )
            return await self.swarm.assign_task(task_type, task_data, require_consensus)

        # Step 2: Build training-enhanced prompt
        enhanced_prompt = self._build_training_enhanced_prompt(
            mapping.primary_expertise, task_type, task_data
        )

        # Step 3: Execute based on configuration
        if mapping.parallel_analysis and len(selected_bots) >= 2:
            return await self._execute_parallel_with_expertise(
                selected_bots, enhanced_prompt, task_data, mapping
            )
        else:
            return await self._execute_single_with_expertise(
                selected_bots[0], enhanced_prompt, task_data, mapping
            )

    def _select_bots_for_expertise(self, mapping: ExpertiseTaskMapping) -> List[Any]:
        """Select bots based on required expertise"""

        alive_bots = [b for b in self.swarm.bots if b.status.value == "alive"]

        # Score bots by expertise match
        scored_bots = []
        for bot in alive_bots:
            score = bot.survival_score

            # Primary expertise match
            if mapping.primary_expertise.replace("_", "") in [
                s.replace("_", "") for s in bot.specialty
            ]:
                score += 0.8

            # Secondary expertise match
            for sec in mapping.secondary_expertise:
                if sec.replace("_", "") in [s.replace("_", "") for s in bot.specialty]:
                    score += 0.3

            scored_bots.append((bot, score))

        # Sort by score
        scored_bots.sort(key=lambda x: x[1], reverse=True)

        # Return top bots (diversified by provider if possible)
        selected = []
        providers_used = set()

        for bot, score in scored_bots:
            if len(selected) >= 3:
                break

            # Prefer diverse providers for parallel analysis
            if mapping.parallel_analysis and bot.provider in providers_used:
                continue

            selected.append(bot)
            providers_used.add(bot.provider)

        # If parallel needed but only have one, still use it
        if not selected and scored_bots:
            selected = [scored_bots[0][0]]

        return selected

    def _build_training_enhanced_prompt(
        self, expertise: str, task_type: str, task_data: Dict
    ) -> TrainingEnhancedPrompt:
        """Build a prompt enhanced with training module content"""

        if not self.training:
            return TrainingEnhancedPrompt(
                base_prompt=str(task_data),
                expertise_context="",
                training_examples=[],
                red_flags=[],
                verification_checklist=[],
                output_format="json",
            )

        # Map expertise string to ExpertiseArea
        expertise_map = {
            "scam_detection": self.ExpertiseArea.SCAM_DETECTION,
            "social_manipulation": self.ExpertiseArea.SOCIAL_MANIPULATION,
            "forensic_accounting": self.ExpertiseArea.FORENSIC_ACCOUNTING,
            "fund_tracing": self.ExpertiseArea.FUND_TRACING,
            "pattern_recognition": self.ExpertiseArea.PATTERN_RECOGNITION,
        }

        exp_area = expertise_map.get(expertise)

        if not exp_area or exp_area not in self.training.modules:
            return TrainingEnhancedPrompt(
                base_prompt=str(task_data),
                expertise_context=f"Task: {task_type}. Analyze carefully.",
                training_examples=[],
                red_flags=[],
                verification_checklist=[
                    "Check for obvious errors",
                    "Verify completeness",
                ],
                output_format="json",
            )

        # Get training module
        module = self.training.modules[exp_area]

        # Extract relevant content from training module
        expertise_context = f"""You are an expert in {module.name} (Level: {module.level.name}).
Your training includes {module.estimated_hours} hours of specialized education.

Training units:
"""
        for unit in module.training_units[:3]:
            expertise_context += f"- {unit['unit_id']}: {unit['name']}\n"

        expertise_context += "\nAssessment criteria:\n"
        for k, v in module.assessment_criteria.items():
            expertise_context += f"- {k}: {v}\n"

        # Extract red flags and indicators
        red_flags = []
        for unit in module.training_units:
            if "red_flags" in unit:
                red_flags.extend(unit["red_flags"][:5])
            if "bot_indicators" in unit:
                red_flags.extend(unit["bot_indicators"][:5])
            if "warning_signs" in unit:
                red_flags.extend(unit["warning_signs"][:5])

        # Get practice case examples
        training_examples = module.training_units[:2] if module.training_units else []

        # Build verification checklist
        min_acc = module.assessment_criteria.get("min_accuracy", 0.9)
        verification_checklist = [
            f"Meet minimum accuracy: {min_acc * 100:.0f}%",
            "Confidence threshold must be exceeded",
            "All key indicators must be checked",
        ]

        return TrainingEnhancedPrompt(
            base_prompt=str(task_data),
            expertise_context=expertise_context,
            training_examples=training_examples,
            red_flags=red_flags[:15],
            verification_checklist=verification_checklist,
            output_format="json",
        )

    async def _execute_single_with_expertise(
        self,
        bot,
        enhanced_prompt: TrainingEnhancedPrompt,
        task_data: Dict,
        mapping: ExpertiseTaskMapping,
    ) -> Dict:
        """Execute task with a single expert bot"""

        # Build final prompt
        system_prompt = enhanced_prompt.expertise_context + "\n\n"
        system_prompt += "You must meet these verification criteria:\n"
        for v in enhanced_prompt.verification_checklist:
            system_prompt += f"- {v}\n"

        system_prompt += "\nKey indicators to check:\n"
        for r in enhanced_prompt.red_flags[:10]:
            system_prompt += f"- {r}\n"

        system_prompt += "\nOutput must be valid JSON."

        desc = task_data.get(
            "description", task_data.get("prompt", "Analyze and provide results")
        )
        data_str = json.dumps(task_data, indent=2, default=str)[:3000]

        user_prompt = f"""TASK: {desc}

DATA:
{data_str}

Provide your analysis in JSON format with confidence scores and detailed findings."""

        # Execute
        result = await self.swarm.call_model(bot.id, user_prompt, system_prompt)

        # Parse and verify
        parsed_result = self._parse_expertise_result(result)

        # Update bot stats
        if parsed_result.get("success"):
            bot.tasks_completed += 1
        else:
            bot.tasks_failed += 1

        return {
            "success": parsed_result.get("success", False),
            "bot": bot.name,
            "expertise": mapping.primary_expertise,
            "result": parsed_result,
            "raw_output": result.get("text", "")[:500],
            "verification_applied": True,
        }

    async def _execute_parallel_with_expertise(
        self,
        bots: List[Any],
        enhanced_prompt: TrainingEnhancedPrompt,
        task_data: Dict,
        mapping: ExpertiseTaskMapping,
    ) -> Dict:
        """Execute task with multiple expert bots in parallel and synthesize"""

        logger.info(f"Executing parallel analysis with {len(bots)} bots")

        # Execute all in parallel
        async def run_bot(bot):
            result = await self._execute_single_with_expertise(
                bot, enhanced_prompt, task_data, mapping
            )
            return {"bot": bot.name, "provider": bot.provider, **result}

        results = await asyncio.gather(*[run_bot(bot) for bot in bots])

        # Synthesize results
        synthesis = self._synthesize_expertise_results(results, mapping)

        return {
            "success": synthesis.get("consensus_reached", False),
            "parallel_analysis": True,
            "bots_used": [r["bot"] for r in results],
            "individual_results": results,
            "synthesis": synthesis,
            "expertise": mapping.primary_expertise,
        }

    def _parse_expertise_result(self, result: Dict) -> Dict:
        """Parse and validate an expertise result"""

        text = result.get("text", "")

        try:
            # Extract JSON
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0]
            else:
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1:
                    json_str = text[start : end + 1]
                else:
                    json_str = text

            parsed = json.loads(json_str.strip())

            has_confidence = "confidence" in parsed or "risk_score" in parsed
            has_findings = (
                "findings" in parsed
                or "vulnerabilities" in parsed
                or "analysis" in parsed
            )

            return {
                "success": True,
                "parsed": parsed,
                "has_confidence": has_confidence,
                "has_findings": has_findings,
                "confidence": parsed.get(
                    "confidence", parsed.get("risk_score", 0) / 100
                ),
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON parsing failed: {e}",
                "raw": text[:300],
            }

    def _synthesize_expertise_results(
        self, results: List[Dict], mapping: ExpertiseTaskMapping
    ) -> Dict:
        """Synthesize results from multiple expert bots"""

        successes = sum(1 for r in results if r.get("success"))
        consensus_rate = successes / len(results) if results else 0

        # Collect all findings
        all_findings = []
        for r in results:
            if r.get("result", {}).get("parsed"):
                parsed = r["result"]["parsed"]
                if "findings" in parsed:
                    all_findings.extend(parsed["findings"])
                elif "vulnerabilities" in parsed:
                    all_findings.extend(parsed["vulnerabilities"])

        return {
            "consensus_reached": consensus_rate >= 0.67,
            "consensus_rate": consensus_rate,
            "total_bots": len(results),
            "successful_parses": successes,
            "all_findings": all_findings[:20],
            "primary_expertise": mapping.primary_expertise,
        }


# Demo function
async def demo_enhanced_orchestrator():
    """Demo the enhanced orchestrator"""

    print("""
╔══════════════════════════════════════════════════════════════════╗
║           🎓 ENHANCED SWARM ORCHESTRATOR                         ║
║     Training-Integrated Expertise-Aware Execution              ║
╠══════════════════════════════════════════════════════════════════╣
║  Features:                                                        ║
║  • Expertise-Aware Task Routing                                  ║
║  • Training-Enhanced Prompting                                    ║
║  • Parallel Multi-Bot Analysis                                    ║
║  • Result Synthesis                                               ║
╚══════════════════════════════════════════════════════════════════╝
""")

    from ai_swarm_orchestrator import AISwarmOrchestrator

    print("Initializing swarm...")
    swarm = AISwarmOrchestrator()

    print("Initializing enhanced orchestrator...")
    orchestrator = EnhancedSwarmOrchestrator(swarm)

    print(f"\nExpertise mappings available: {len(orchestrator.expertise_mappings)}")
    for task_type, mapping in orchestrator.expertise_mappings.items():
        print(f"   • {task_type}: {mapping.primary_expertise}")

    print("\nEnhanced orchestrator ready!")


if __name__ == "__main__":
    asyncio.run(demo_enhanced_orchestrator())
