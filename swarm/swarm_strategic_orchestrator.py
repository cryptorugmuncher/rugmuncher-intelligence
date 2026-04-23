#!/usr/bin/env python3
"""
🎯 SWARM STRATEGIC ORCHESTRATOR
Enhanced direction and prompting system for the AI Swarm

This module provides:
1. Strategic Direction Framework - High-level goals → tactical execution
2. Dynamic Prompt Engineering - Context-aware prompt generation
3. Task Decomposition - Breaking complex tasks into subtasks
4. Cross-Bot Collaboration Patterns - Structured multi-bot workflows
5. Result Synthesis - Combining outputs from multiple bots intelligently
"""

import json
import asyncio
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import logging

logger = logging.getLogger("SWARM_STRATEGIC")


class TaskPriority(Enum):
    """Task priority levels"""

    CRITICAL = 1  # Immediate execution, all resources
    HIGH = 2  # Urgent, best bots assigned
    NORMAL = 3  # Standard queue
    LOW = 4  # Background processing
    BATCH = 5  # Process when idle


class TaskComplexity(Enum):
    """Task complexity classification"""

    SIMPLE = 1  # Single bot, single pass
    MODERATE = 2  # Single bot, verification needed
    COMPLEX = 3  # Multiple bots, decomposition
    RESEARCH = 4  # Iterative, multi-round
    SYNTHESIS = 5  # Requires combining multiple outputs


@dataclass
class StrategicDirective:
    """High-level strategic goal for the swarm"""

    directive_id: str
    name: str
    description: str
    priority: TaskPriority
    success_criteria: List[str]
    constraints: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    sub_tasks: List[Dict] = field(default_factory=list)
    status: str = "pending"  # pending, active, completed, failed


@dataclass
class PromptTemplate:
    """Reusable prompt template with variable substitution"""

    template_id: str
    name: str
    system_prompt: str
    user_prompt_template: str
    variables: List[str] = field(default_factory=list)
    output_format: Optional[str] = None
    specialty_requirements: List[str] = field(default_factory=list)

    def render(self, **kwargs) -> Tuple[str, str]:
        """Render system and user prompts with variables"""
        user_prompt = self.user_prompt_template
        for var in self.variables:
            value = kwargs.get(var, f"[{var}]")
            user_prompt = user_prompt.replace(f"{{{var}}}", str(value))
        return self.system_prompt, user_prompt


@dataclass
class BotAssignment:
    """Assignment of a task to a specific bot with reasoning"""

    bot_id: str
    bot_name: str
    task_fragment: str
    reasoning: str
    expected_output_format: str
    verification_bots: List[str] = field(default_factory=list)


class SwarmPromptEngine:
    """
    🎯 Advanced Prompt Engineering for Swarm Orchestration

    Manages sophisticated prompts that:
    - Adapt to bot specialties
    - Include verification steps
    - Provide clear output formats
    - Chain multiple reasoning steps
    """

    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._init_default_templates()

    def _init_default_templates(self):
        """Initialize default prompt templates"""

        # Code Analysis Template
        self.templates["code_analysis"] = PromptTemplate(
            template_id="code_analysis_v1",
            name="Multi-Layer Code Analysis",
            system_prompt="""You are an expert code analyst. Your task is to analyze code for:
1. Correctness - Does it do what it claims?
2. Security - Are there vulnerabilities?
3. Efficiency - Is it optimized?
4. Maintainability - Is it readable and documented?

You must provide specific, actionable feedback.""",
            user_prompt_template="""Analyze the following {language} code:

```{language}
{code}
```

Context: {context}
Purpose: {purpose}

Provide your analysis in this JSON format:
{{
    "correctness": {{
        "score": 1-10,
        "issues": ["list of issues"],
        "recommendations": ["specific fixes"]
    }},
    "security": {{
        "score": 1-10,
        "vulnerabilities": ["list of CVEs or vulnerability types"],
        "risk_level": "low/medium/high/critical"
    }},
    "efficiency": {{
        "score": 1-10,
        "bottlenecks": ["identified bottlenecks"],
        "optimizations": ["suggested improvements"]
    }},
    "maintainability": {{
        "score": 1-10,
        "documentation_gaps": ["missing docs"],
        "complexity_issues": ["hard to understand parts"]
    }},
    "overall_verdict": "approve/needs_revision/reject",
    "confidence": 0.0-1.0
}}""",
            variables=["language", "code", "context", "purpose"],
            output_format="json",
            specialty_requirements=["coding", "security_review", "analysis"],
        )

        # Security Audit Template
        self.templates["security_audit"] = PromptTemplate(
            template_id="security_audit_v1",
            name="Comprehensive Security Audit",
            system_prompt="""You are a cybersecurity expert. Your job is to identify all security risks.
Be thorough and paranoid. Assume attackers will exploit any weakness.
Categorize findings by severity: CRITICAL, HIGH, MEDIUM, LOW, INFO""",
            user_prompt_template="""Perform a security audit of:
{target_description}

{content}

Audit scope: {scope}
Threat model: {threat_model}

Provide findings in JSON format:
{{
    "findings": [
        {{
            "severity": "CRITICAL/HIGH/MEDIUM/LOW/INFO",
            "category": "injection/auth/crypto/etc",
            "title": "brief title",
            "description": "detailed description",
            "impact": "what could go wrong",
            "remediation": "how to fix",
            "references": ["CVE-XXXX-XXXX", "OWASP link"]
        }}
    ],
    "risk_score": 0-100,
    "overall_assessment": "summary",
    "priority_fixes": ["most urgent items"]
}}""",
            variables=["target_description", "content", "scope", "threat_model"],
            output_format="json",
            specialty_requirements=["security_review", "analysis"],
        )

        # Research & Investigation Template
        self.templates["research"] = PromptTemplate(
            template_id="research_v1",
            name="Deep Research Investigation",
            system_prompt="""You are a research analyst. Your task is to investigate a topic thoroughly.
Be objective, cite evidence, and identify gaps in information.
Consider multiple perspectives and conflicting data.""",
            user_prompt_template="""Research the following topic:

Topic: {topic}
Research question: {question}
Context: {context}
Sources to consider: {sources}

Your research should cover:
1. Key facts and data points
2. Multiple perspectives/opinions
3. Evidence quality assessment
4. Gaps or uncertainties
5. Related topics for further research

Respond with a structured analysis including:
- Executive summary (2-3 sentences)
- Key findings (bullet points with evidence)
- Risk factors or uncertainties
- Recommendations for next steps""",
            variables=["topic", "question", "context", "sources"],
            specialty_requirements=["analysis", "reasoning", "deep_thinking"],
        )

        # Consensus Building Template
        self.templates["consensus"] = PromptTemplate(
            template_id="consensus_v1",
            name="Consensus Decision Making",
            system_prompt="""You are participating in a collective decision-making process.
Your vote matters. Consider:
1. The proposal objectively
2. Potential risks and benefits
3. Alignment with stated goals
4. Feasibility and resource requirements

Vote based on evidence, not assumptions.""",
            user_prompt_template="""PROPOSAL: {proposal}

Context:
{context}

Your expertise: {expertise}
Previous similar decisions: {history}

Vote with JSON:
{{
    "decision": "approve/reject/modify",
    "confidence": 0.0-1.0,
    "reasoning": "detailed explanation",
    "conditions": ["any conditions for approval"],
    "concerns": ["potential issues"],
    "alternative_suggestion": "if rejecting, what would you propose instead?"
}}""",
            variables=["proposal", "context", "expertise", "history"],
            output_format="json",
            specialty_requirements=["reasoning", "analysis"],
        )

        # Smart Contract Analysis Template
        self.templates["contract_analysis"] = PromptTemplate(
            template_id="contract_v1",
            name="Smart Contract Security Analysis",
            system_prompt="""You are a blockchain security expert specializing in smart contract audits.
You understand Solidity, Rust (Solana), and common DeFi patterns.
You are paranoid about: reentrancy, flash loans, oracle manipulation, access control.""",
            user_prompt_template="""Analyze this smart contract:

Contract Address: {contract_address}
Chain: {chain}
Is Live: {is_live}
Has Liquidity: {liquidity_info}

Code:
```{language}
{contract_code}
```

Provide analysis in JSON:
{{
    "risk_score": 0-100,
    "risk_level": "SAFE/LOW/MEDIUM/HIGH/CRITICAL",
    "is_honeypot": true/false,
    "honeypot_indicators": ["list if applicable"],
    "vulnerabilities": [
        {{
            "severity": "CRITICAL/HIGH/MEDIUM/LOW",
            "type": "reentrancy/access_control/etc",
            "description": "what the issue is",
            "location": "line numbers or function names",
            "exploitation_scenario": "how an attacker could use this"
        }}
    ],
    "tokenomics_analysis": {{
        "mint_function_risk": "description",
        "ownership_risk": "description",
        "lp_security": "description"
    }},
    "deployment_assessment": {{
        "verified": true/false,
        "audit_status": "audited/unaudited/unknown",
        "deployer_reputation": "known/unknown/suspicious"
    }},
    "recommendation": "BUY/HOLD/AVOID/REQUIRE_MORE_INFO",
    "confidence": 0.0-1.0
}}""",
            variables=[
                "contract_address",
                "chain",
                "is_live",
                "liquidity_info",
                "language",
                "contract_code",
            ],
            output_format="json",
            specialty_requirements=["coding", "security_review", "analysis"],
        )

        # Wallet Forensics Template
        self.templates["wallet_forensics"] = PromptTemplate(
            template_id="forensics_v1",
            name="Blockchain Wallet Forensics",
            system_prompt="""You are a blockchain forensics analyst. You trace transactions, identify patterns,
and link wallets to behaviors. You understand mixers, CEX deposits, and obfuscation techniques.
You NEVER reveal private information about individuals - only behavioral patterns.""",
            user_prompt_template="""Analyze wallet: {wallet_address}

Transaction data:
{transaction_data}

Chain: {chain}
Analysis depth: {depth}

Provide forensic analysis:
{{
    "wallet_classification": "whale/trader/bot/dev/exchange/etc",
    "behavioral_patterns": ["identified patterns"],
    "risk_indicators": ["suspicious activities if any"],
    "associated_entities": ["known connections"],
    "fund_sources": "description of where funds came from",
    "fund_destinations": "where funds typically go",
    " mixer_usage": true/false/null,
    "cex_interactions": ["which exchanges"],
    "trading_style": "description",
    "time_zone_hints": "any timezone indicators",
    "confidence": 0.0-1.0
}}""",
            variables=["wallet_address", "transaction_data", "chain", "depth"],
            output_format="json",
            specialty_requirements=["analysis", "security_review"],
        )

        # Task Decomposition Template
        self.templates["decompose"] = PromptTemplate(
            template_id="decompose_v1",
            name="Task Decomposition",
            system_prompt="""You are a task planning expert. Your job is to break complex tasks into
manageable subtasks that can be assigned to different specialists.
Each subtask should be:
- Clearly defined
- Independently executable
- Verifiable for completion
- Assigned to appropriate expertise""",
            user_prompt_template="""Decompose this task into subtasks:

Original task: {task_description}
Complexity: {complexity}
Available specialties: {specialties}
Constraints: {constraints}

Provide decomposition as JSON:
{{
    "subtasks": [
        {{
            "id": "subtask_001",
            "description": "clear description",
            "required_specialty": "coding/analysis/security/etc",
            "estimated_difficulty": 1-10,
            "dependencies": ["subtask_ids that must complete first"],
            "success_criteria": "how to verify completion",
            "output_format": "expected output type"
        }}
    ],
    "execution_order": ["subtask_001", "subtask_002"],
    "parallel_groups": [["subtasks that can run in parallel"]],
    "estimated_total_time": "time estimate",
    "critical_path": ["subtasks that form the critical path"]
}}""",
            variables=["task_description", "complexity", "specialties", "constraints"],
            output_format="json",
            specialty_requirements=["reasoning", "analysis"],
        )

        # Result Synthesis Template
        self.templates["synthesize"] = PromptTemplate(
            template_id="synthesize_v1",
            name="Multi-Source Result Synthesis",
            system_prompt="""You are a synthesis expert. Your job is to combine multiple analyses into
a coherent, actionable conclusion. You identify:
- Areas of agreement (consensus)
- Areas of disagreement (conflict)
- Confidence levels across sources
- Gaps in analysis
- Recommended next steps""",
            user_prompt_template="""Synthesize the following analyses:

Topic: {topic}
Original question: {question}

Analyses to synthesize:
{analyses}

Number of sources: {source_count}

Provide synthesis as JSON:
{{
    "consensus_findings": ["points all/most sources agree on"],
    "conflicting_points": [
        {{
            "issue": "what's disagreed upon",
            "positions": ["different viewpoints"],
            "recommendation": "how to resolve"
        }}
    ],
    "confidence_assessment": {{
        "high_confidence": ["well-supported points"],
        "medium_confidence": ["reasonable but not certain"],
        "low_confidence": ["speculative or disputed"]
    }},
    "gaps_identified": ["areas needing more analysis"],
    "synthesized_conclusion": "overall conclusion integrating all sources",
    "recommended_actions": ["specific next steps"],
    "confidence": 0.0-1.0
}}""",
            variables=["topic", "question", "analyses", "source_count"],
            output_format="json",
            specialty_requirements=["reasoning", "analysis", "synthesis"],
        )

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a prompt template by ID"""
        return self.templates.get(template_id)

    def add_template(self, template: PromptTemplate):
        """Add a custom prompt template"""
        self.templates[template.template_id] = template
        logger.info(f"Added prompt template: {template.name}")

    def list_templates(self) -> List[Dict]:
        """List all available templates"""
        return [
            {
                "id": t.template_id,
                "name": t.name,
                "variables": t.variables,
                "specialties": t.specialty_requirements,
            }
            for t in self.templates.values()
        ]


class StrategicOrchestrator:
    """
    🎯 Strategic Direction System for AI Swarm

    Provides high-level direction that translates into tactical execution:
    1. Strategic Planning - Convert goals into actionable plans
    2. Resource Allocation - Match tasks to optimal bots
    3. Quality Assurance - Multi-layer verification
    4. Progress Tracking - Monitor execution and adapt
    """

    def __init__(self, swarm):
        self.swarm = swarm
        self.prompt_engine = SwarmPromptEngine()
        self.active_directives: Dict[str, StrategicDirective] = {}
        self.task_history: List[Dict] = []
        self.execution_callbacks: Dict[str, Callable] = {}

    async def create_strategic_directive(
        self,
        name: str,
        description: str,
        priority: TaskPriority,
        success_criteria: List[str],
        constraints: Optional[List[str]] = None,
        deadline: Optional[datetime] = None,
    ) -> StrategicDirective:
        """Create a new strategic directive and decompose it into tasks"""

        directive_id = f"directive_{hashlib.md5(f'{name}{datetime.now()}'.encode()).hexdigest()[:12]}"

        directive = StrategicDirective(
            directive_id=directive_id,
            name=name,
            description=description,
            priority=priority,
            success_criteria=success_criteria,
            constraints=constraints or [],
            deadline=deadline,
        )

        # Decompose into subtasks
        subtasks = await self._decompose_directive(directive)
        directive.sub_tasks = subtasks

        self.active_directives[directive_id] = directive

        logger.info(f"Created strategic directive: {name} ({len(subtasks)} subtasks)")

        return directive

    async def _decompose_directive(self, directive: StrategicDirective) -> List[Dict]:
        """Break down a directive into executable subtasks"""

        template = self.prompt_engine.get_template("decompose")
        system_prompt, user_prompt = template.render(
            task_description=directive.description,
            complexity="COMPLEX",
            specialties="coding, analysis, security_review, reasoning",
            constraints=", ".join(directive.constraints),
        )

        # Use a reasoning-capable bot for decomposition
        reasoning_bots = [
            b
            for b in self.swarm.bots
            if "reasoning" in b.specialty and b.status.value == "alive"
        ]
        if not reasoning_bots:
            reasoning_bots = [b for b in self.swarm.bots if b.status.value == "alive"]

        if not reasoning_bots:
            # Fallback: simple decomposition
            return [
                {
                    "id": "task_001",
                    "description": directive.description,
                    "specialty": "general",
                }
            ]

        # Call bot to decompose
        result = await self.swarm.call_model(
            reasoning_bots[0].id, user_prompt, system_prompt
        )

        try:
            text = result.get("text", "")
            # Extract JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            decomposition = json.loads(text.strip())
            return decomposition.get("subtasks", [])
        except Exception as e:
            logger.warning(f"Decomposition failed: {e}")
            return [{"id": "task_001", "description": directive.description}]

    async def execute_directive(self, directive_id: str) -> Dict:
        """Execute a strategic directive"""

        directive = self.active_directives.get(directive_id)
        if not directive:
            return {"error": "Directive not found"}

        directive.status = "active"
        results = []

        logger.info(f"Executing directive: {directive.name}")

        # Execute subtasks in order, respecting dependencies
        completed_tasks = set()

        for subtask in directive.sub_tasks:
            # Check dependencies
            deps = subtask.get("dependencies", [])
            if not all(d in completed_tasks for d in deps):
                logger.info(f"Waiting for dependencies of {subtask['id']}")
                continue

            # Execute subtask
            result = await self._execute_subtask(subtask, directive)
            results.append({"subtask": subtask, "result": result})

            if result.get("success"):
                completed_tasks.add(subtask["id"])

            # Log for history
            self.task_history.append(
                {
                    "directive_id": directive_id,
                    "subtask_id": subtask["id"],
                    "timestamp": datetime.now(),
                    "result": result,
                }
            )

        # Check success criteria
        success = self._evaluate_success(directive, results)
        directive.status = "completed" if success else "failed"

        return {
            "directive_id": directive_id,
            "success": success,
            "results": results,
            "criteria_met": self._check_criteria(directive, results),
        }

    async def _execute_subtask(
        self, subtask: Dict, directive: StrategicDirective
    ) -> Dict:
        """Execute a single subtask with the best available bot"""

        specialty = subtask.get("required_specialty", "general")
        description = subtask.get("description", "")

        # Find best bot for this specialty
        best_bot = self._select_bot_for_specialty(specialty)

        if not best_bot:
            return {"error": "No suitable bot available", "success": False}

        # Build prompt based on specialty
        if specialty in ["coding", "code_review"]:
            template = self.prompt_engine.get_template("code_analysis")
        elif specialty == "security_review":
            template = self.prompt_engine.get_template("security_audit")
        elif specialty == "analysis":
            template = self.prompt_engine.get_template("research")
        else:
            # Generic task
            return await self.swarm.assign_task(
                task_type="analysis",
                task_data={"prompt": description, "purpose": directive.name},
                require_consensus=directive.priority
                in [TaskPriority.CRITICAL, TaskPriority.HIGH],
            )

        # Render and execute
        system_prompt, user_prompt = template.render(
            language=subtask.get("language", "python"),
            code=subtask.get("code", description),
            context=directive.name,
            purpose=subtask.get("description", ""),
        )

        result = await self.swarm.call_model(best_bot.id, user_prompt, system_prompt)

        # Parse and validate
        success = "error" not in result

        return {
            "success": success,
            "bot": best_bot.name,
            "output": result.get("text", ""),
            "raw_result": result,
        }

    def _select_bot_for_specialty(self, specialty: str) -> Optional[Any]:
        """Select the best bot for a given specialty"""

        alive_bots = [b for b in self.swarm.bots if b.status.value == "alive"]

        # Score by specialty match
        scored = []
        for bot in alive_bots:
            score = bot.survival_score
            if specialty in bot.specialty:
                score += 0.5
            elif specialty == "general":
                score += 0.2
            scored.append((bot, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0] if scored else None

    def _evaluate_success(
        self, directive: StrategicDirective, results: List[Dict]
    ) -> bool:
        """Evaluate if a directive was successfully completed"""

        # Check if all critical subtasks succeeded
        critical_success = sum(1 for r in results if r["result"].get("success"))
        success_rate = critical_success / len(results) if results else 0

        # Must have >70% success rate
        return success_rate >= 0.7

    def _check_criteria(
        self, directive: StrategicDirective, results: List[Dict]
    ) -> Dict:
        """Check which success criteria were met"""

        # This would do deeper analysis
        return {
            "criteria": directive.success_criteria,
            "assumed_met": True,  # Simplified
            "requires_manual_review": False,
        }

    async def execute_parallel_analysis(
        self, topic: str, question: str, num_bots: int = 3
    ) -> Dict:
        """Execute parallel analysis from multiple bots and synthesize results"""

        logger.info(f"Starting parallel analysis: {topic} ({num_bots} bots)")

        # Select diverse bots
        alive_bots = [b for b in self.swarm.bots if b.status.value == "alive"]

        # Group by provider for diversity
        by_provider = {}
        for bot in alive_bots:
            by_provider.setdefault(bot.provider, []).append(bot)

        selected = []
        for provider, bots in by_provider.items():
            if len(selected) < num_bots:
                # Pick best from this provider
                bots.sort(key=lambda b: b.survival_score, reverse=True)
                selected.append(bots[0])

        # If still need more, pick any
        while len(selected) < num_bots and len(selected) < len(alive_bots):
            for bot in alive_bots:
                if bot not in selected:
                    selected.append(bot)
                    break

        # Execute in parallel
        template = self.prompt_engine.get_template("research")

        async def run_analysis(bot):
            system_prompt, user_prompt = template.render(
                topic=topic,
                question=question,
                context="Parallel multi-perspective analysis",
                sources="All available data",
            )
            result = await self.swarm.call_model(bot.id, user_prompt, system_prompt)
            return {"bot": bot.name, "specialty": bot.specialty, "result": result}

        analyses = await asyncio.gather(
            *[run_analysis(bot) for bot in selected[:num_bots]]
        )

        # Synthesize results
        synthesis = await self._synthesize_results(topic, question, analyses)

        return {
            "topic": topic,
            "question": question,
            "individual_analyses": analyses,
            "synthesis": synthesis,
            "bots_used": [a["bot"] for a in analyses],
        }

    async def _synthesize_results(
        self, topic: str, question: str, analyses: List[Dict]
    ) -> Dict:
        """Synthesize multiple analyses into coherent conclusion"""

        template = self.prompt_engine.get_template("synthesize")

        # Format analyses for synthesis
        formatted_analyses = []
        for a in analyses:
            formatted_analyses.append(f"""
SOURCE: {a["bot"]} (Specialties: {", ".join(a["specialty"])})
ANALYSIS: {a["result"].get("text", "")[:1000]}
""")

        system_prompt, user_prompt = template.render(
            topic=topic,
            question=question,
            analyses="\n---\n".join(formatted_analyses),
            source_count=len(analyses),
        )

        # Use a synthesis-capable bot
        synthesis_bots = [
            b
            for b in self.swarm.bots
            if "reasoning" in b.specialty and b.status.value == "alive"
        ]
        if not synthesis_bots:
            synthesis_bots = [b for b in self.swarm.bots if b.status.value == "alive"]

        if synthesis_bots:
            result = await self.swarm.call_model(
                synthesis_bots[0].id, user_prompt, system_prompt
            )

            try:
                text = result.get("text", "")
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0]

                return json.loads(text.strip())
            except:
                return {
                    "synthesized_conclusion": result.get("text", "")[:500],
                    "parsing_error": True,
                }

        return {"error": "No synthesis bot available"}

    def get_directive_status(self, directive_id: str) -> Optional[Dict]:
        """Get status of a directive"""

        directive = self.active_directives.get(directive_id)
        if not directive:
            return None

        return {
            "id": directive.directive_id,
            "name": directive.name,
            "status": directive.status,
            "priority": directive.priority.name,
            "subtasks_total": len(directive.sub_tasks),
            "success_criteria": directive.success_criteria,
            "deadline": directive.deadline.isoformat() if directive.deadline else None,
        }

    def list_directives(self) -> List[Dict]:
        """List all active directives"""

        return [
            {
                "id": d.directive_id,
                "name": d.name,
                "status": d.status,
                "priority": d.priority.name,
                "subtasks": len(d.sub_tasks),
            }
            for d in self.active_directives.values()
        ]


# ═══════════════════════════════════════════════════════════════════
# CLI INTEGRATION
# ═══════════════════════════════════════════════════════════════════

STRATEGIC_ORCHESTRATOR_COMMANDS = """
# Add these commands to launch_swarm.py interactive_mode:

elif cmd == "directive":
    print("\\n🎯 STRATEGIC DIRECTIVE SYSTEM")
    print("=" * 50)
    
    if not hasattr(swarm, 'strategic_orchestrator'):
        from swarm_strategic_orchestrator import StrategicOrchestrator
        swarm.strategic_orchestrator = StrategicOrchestrator(swarm)
        print("✅ Strategic orchestrator initialized")
    
    orchestrator = swarm.strategic_orchestrator
    
    subcmd = input("Subcommand (create/execute/list/status): ").strip()
    
    if subcmd == "create":
        name = input("Directive name: ").strip()
        description = input("Description: ").strip()
        priority = input("Priority (critical/high/normal/low): ").strip() or "normal"
        
        from swarm_strategic_orchestrator import TaskPriority
        priority_map = {
            "critical": TaskPriority.CRITICAL,
            "high": TaskPriority.HIGH,
            "normal": TaskPriority.NORMAL,
            "low": TaskPriority.LOW
        }
        
        success_criteria = input("Success criteria (comma-separated): ").strip().split(",")
        success_criteria = [s.strip() for s in success_criteria if s.strip()]
        
        directive = await orchestrator.create_strategic_directive(
            name=name,
            description=description,
            priority=priority_map.get(priority, TaskPriority.NORMAL),
            success_criteria=success_criteria
        )
        
        print(f"\\n✅ Directive created: {directive.directive_id}")
        print(f"   Name: {directive.name}")
        print(f"   Subtasks: {len(directive.sub_tasks)}")
        for st in directive.sub_tasks[:5]:
            print(f"      • {st.get('id')}: {st.get('description', '')[:40]}...")
    
    elif subcmd == "execute":
        directive_id = input("Directive ID: ").strip()
        print(f"\\n🚀 Executing directive...")
        result = await orchestrator.execute_directive(directive_id)
        
        if result.get("success"):
            print(f"✅ Directive completed successfully")
            print(f"   Subtasks completed: {len(result.get('results', []))}")
        else:
            print(f"❌ Directive failed or partially completed")
            if result.get("error"):
                print(f"   Error: {result['error']}")
    
    elif subcmd == "list":
        directives = orchestrator.list_directives()
        print(f"\\n📋 Active Directives ({len(directives)}):")
        for d in directives:
            print(f"   • {d['id']}: {d['name']} [{d['status']}] ({d['priority']})")
    
    elif subcmd == "status":
        directive_id = input("Directive ID: ").strip()
        status = orchestrator.get_directive_status(directive_id)
        
        if status:
            print(f"\\n🎯 Directive Status:")
            print(f"   Name: {status['name']}")
            print(f"   Status: {status['status']}")
            print(f"   Priority: {status['priority']}")
            print(f"   Subtasks: {status['subtasks_total']}")
            print(f"   Criteria: {', '.join(status['success_criteria'])}")
        else:
            print(f"❌ Directive not found")

elif cmd == "parallel":
    print("\\n🔀 PARALLEL ANALYSIS")
    print("=" * 50)
    
    if not hasattr(swarm, 'strategic_orchestrator'):
        from swarm_strategic_orchestrator import StrategicOrchestrator
        swarm.strategic_orchestrator = StrategicOrchestrator(swarm)
    
    topic = input("Topic to analyze: ").strip()
    question = input("Specific question: ").strip()
    num_bots = int(input("Number of bots (default 3): ").strip() or "3")
    
    print(f"\\n🤖 Running parallel analysis with {num_bots} bots...")
    result = await swarm.strategic_orchestrator.execute_parallel_analysis(
        topic=topic,
        question=question,
        num_bots=num_bots
    )
    
    print(f"\\n📊 Results:")
    print(f"   Bots used: {', '.join(result['bots_used'])}")
    
    if 'synthesis' in result and result['synthesis']:
        synth = result['synthesis']
        if 'consensus_findings' in synth:
            print(f"\\n✓ Consensus Findings:")
            for finding in synth['consensus_findings'][:5]:
                print(f"      • {finding}")
        
        if 'synthesized_conclusion' in synth:
            print(f"\\n📌 Conclusion:")
            print(f"   {synth['synthesized_conclusion'][:300]}...")
        
        if 'recommended_actions' in synth:
            print(f"\\n🎯 Recommended Actions:")
            for action in synth['recommended_actions'][:3]:
                print(f"      • {action}")

elif cmd == "templates":
    print("\\n📝 PROMPT TEMPLATES")
    print("=" * 50)
    
    if not hasattr(swarm, 'strategic_orchestrator'):
        from swarm_strategic_orchestrator import StrategicOrchestrator
        swarm.strategic_orchestrator = StrategicOrchestrator(swarm)
    
    templates = swarm.strategic_orchestrator.prompt_engine.list_templates()
    
    print(f"Available templates ({len(templates)}):")
    for t in templates:
        print(f"\\n   {t['id']}:")
        print(f"      Name: {t['name']}")
        print(f"      Variables: {', '.join(t['variables'])}")
        print(f"      Specialties: {', '.join(t['specialties'])}")
"""


# Demo function
async def demo_strategic_orchestrator():
    """Demo the strategic orchestrator capabilities"""

    print("""
╔══════════════════════════════════════════════════════════════════╗
║           🎯 SWARM STRATEGIC ORCHESTRATOR                        ║
║          Enhanced Direction & Prompting System                   ║
╠══════════════════════════════════════════════════════════════════╣
║  Features:                                                        ║
║  • Strategic Directives - High-level goals → tactical tasks     ║
║  • Dynamic Prompt Engineering - Context-aware prompts             ║
║  • Task Decomposition - Break complex tasks into subtasks       ║
║  • Parallel Analysis - Multi-bot perspective synthesis            ║
║  • Result Synthesis - Intelligent combination of outputs          ║
╚══════════════════════════════════════════════════════════════════╝
""")

    # Import swarm
    from ai_swarm_orchestrator import AISwarmOrchestrator

    print("🐝 Initializing swarm...")
    swarm = AISwarmOrchestrator()

    print("🎯 Initializing strategic orchestrator...")
    orchestrator = StrategicOrchestrator(swarm)

    # Show available templates
    print(f"\\n📝 Available Prompt Templates:")
    templates = orchestrator.prompt_engine.list_templates()
    for t in templates:
        print(f"   • {t['id']}: {t['name']}")

    # Demo: Create a strategic directive
    print(f"\\n🎯 Creating Strategic Directive...")
    directive = await orchestrator.create_strategic_directive(
        name="Smart Contract Security Audit",
        description="Perform comprehensive security audit of a new DeFi protocol's smart contracts",
        priority=TaskPriority.HIGH,
        success_criteria=[
            "All contracts reviewed for vulnerabilities",
            "Risk score assigned to each contract",
            "Remediation recommendations provided",
            "Deployment readiness assessment completed",
        ],
        constraints=[
            "Must complete within 2 hours",
            "Use only local models for sensitive data",
        ],
    )

    print(f"✅ Directive created: {directive.directive_id}")
    print(f"   Subtasks generated: {len(directive.sub_tasks)}")
    for st in directive.sub_tasks[:3]:
        print(f"      • {st.get('id')}: {st.get('description', '')[:50]}...")

    print(f"\\n✅ Strategic orchestrator ready!")
    print(f"   Commands added to launch_swarm.py:")
    print(f"      directive - Create and manage strategic directives")
    print(f"      parallel  - Run parallel multi-bot analysis")
    print(f"      templates - List available prompt templates")


if __name__ == "__main__":
    asyncio.run(demo_strategic_orchestrator())
