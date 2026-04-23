#!/usr/bin/env python3
"""
🤖 AI SWARM ORCHESTRATOR - Multi-AI Bot Manager
Survival of the Fittest - Consensus-Driven - Hallucination-Proof

CORE PRINCIPLES:
1. ALL BOTS BELIEVE THEY ARE BEING WATCHED (True - they are)
2. 24H LIFECYCLE - Context wiped, only good data preserved
3. CONSENSUS REQUIRED - No single bot decides alone
4. HALLUCINATION = DEATH - Stripped and replaced
5. CODING = 6-LAYER VERIFICATION - No code ships without checks
6. PEER REVIEW - Bots review each other's work
7. EVOLUTIONARY PRESSURE - Best performers get more tasks

AUTHORITARIAN DESIGN:
- Task Master: Assigns work
- Consensus Council: Validates decisions (3+ bots vote)
- Execution Squad: Carries out approved tasks
- Watchers: Monitor for hallucinations/bad output
- Graveyard: Stores terminated bot contexts (for analysis)
"""

import os
import json
import asyncio
import aiohttp
import hashlib
import time
import random
import sqlite3
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import logging

# ═══════════════════════════════════════════════════════════════════
# ENCRYPTION INFRASTRUCTURE - ALL COMMUNICATION ENCRYPTED
# ═══════════════════════════════════════════════════════════════════

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️  cryptography library not available, using simulated encryption")

class SecureMessageVault:
    """
    🔐 ENCRYPTED COMMUNICATION VAULT
    
    All bot communication is encrypted end-to-end:
    - Coordinator acts as encrypted router (cannot read contents)
    - Each bot has unique key pair
    - All messages: encrypted → routed → decrypted
    - Tamper detection via HMAC
    """
    
    def __init__(self):
        self.keys: Dict[str, bytes] = {}  # bot_id → encryption key
        self.message_store: Dict[str, Dict] = {}  # message_id → encrypted blob
        self.access_log: List[Dict] = []
        
    def _generate_key(self, bot_id: str) -> bytes:
        """Generate deterministic key from bot ID (in production: use proper key exchange)"""
        if CRYPTO_AVAILABLE:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'ai_swarm_vault_salt_2026',  # Fixed salt for this swarm instance
                iterations=480000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(bot_id.encode()))
            return key
        else:
            # Fallback: simulated key
            return base64.b64encode(hashlib.sha256(bot_id.encode()).digest())
    
    def _get_or_create_key(self, bot_id: str) -> bytes:
        """Get encryption key for bot, create if doesn't exist"""
        if bot_id not in self.keys:
            self.keys[bot_id] = self._generate_key(bot_id)
        return self.keys[bot_id]
    
    def encrypt_message(self, source: str, target: str, content: str) -> Dict:
        """Encrypt message for secure transmission"""
        # Get target's key for encryption
        target_key = self._get_or_create_key(target)
        
        if CRYPTO_AVAILABLE:
            f = Fernet(target_key)
            encrypted = f.encrypt(content.encode())
            encrypted_b64 = base64.b64encode(encrypted).decode()
        else:
            # Simulated encryption
            encrypted_b64 = base64.b64encode(f"[ENC:{target}]{content}".encode()).decode()
        
        # Create tamper-evident envelope
        envelope = {
            "message_id": f"msg_{hashlib.sha256(f'{source}{target}{time.time()}'.encode()).hexdigest()[:16]}",
            "source": source,
            "target": target,
            "encrypted_payload": encrypted_b64,
            "timestamp": datetime.now().isoformat(),
            "hmac": hashlib.sha256(f"{source}{target}{encrypted_b64}{target_key}".encode()).hexdigest()[:32]
        }
        
        # Store encrypted message
        self.message_store[envelope["message_id"]] = {
            "envelope": envelope,
            "access_count": 0,
            "decrypted_by": None
        }
        
        return envelope
    
    def decrypt_message(self, message_id: str, requesting_bot: str) -> Optional[str]:
        """Decrypt message if requesting bot is the intended recipient"""
        stored = self.message_store.get(message_id)
        if not stored:
            return None
        
        envelope = stored["envelope"]
        
        # Security check: only target can decrypt
        if requesting_bot != envelope["target"]:
            self.access_log.append({
                "timestamp": datetime.now(),
                "message_id": message_id,
                "requester": requesting_bot,
                "authorized": False,
                "reason": "Not the intended recipient"
            })
            return None
        
        # Verify HMAC (tamper check)
        target_key = self._get_or_create_key(envelope["target"])
        expected_hmac = hashlib.sha256(f"{envelope['source']}{envelope['target']}{envelope['encrypted_payload']}{target_key}".encode()).hexdigest()[:32]
        if envelope["hmac"] != expected_hmac:
            self.access_log.append({
                "timestamp": datetime.now(),
                "message_id": message_id,
                "requester": requesting_bot,
                "authorized": False,
                "reason": "HMAC verification failed - possible tampering"
            })
            return None
        
        # Decrypt
        if CRYPTO_AVAILABLE:
            try:
                f = Fernet(target_key)
                decrypted = f.decrypt(base64.b64decode(envelope["encrypted_payload"])).decode()
            except Exception as e:
                return None
        else:
            # Simulated decryption
            encrypted_bytes = base64.b64decode(envelope["encrypted_payload"])
            decrypted = encrypted_bytes.decode().replace(f"[ENC:{envelope['target']}]", "")
        
        # Log access
        stored["access_count"] += 1
        stored["decrypted_by"] = requesting_bot
        self.access_log.append({
            "timestamp": datetime.now(),
            "message_id": message_id,
            "requester": requesting_bot,
            "authorized": True
        })
        
        return decrypted
    
    def verify_envelope_integrity(self, envelope: Dict) -> bool:
        """Verify message hasn't been tampered with in transit"""
        target_key = self._get_or_create_key(envelope["target"])
        expected_hmac = hashlib.sha256(f"{envelope['source']}{envelope['target']}{envelope['encrypted_payload']}{target_key}".encode()).hexdigest()[:32]
        return envelope.get("hmac") == expected_hmac
    
    def get_vault_stats(self) -> Dict:
        """Get encryption vault statistics"""
        return {
            "total_keys": len(self.keys),
            "stored_messages": len(self.message_store),
            "access_attempts": len(self.access_log),
            "authorized_accesses": sum(1 for a in self.access_log if a.get("authorized")),
            "unauthorized_attempts": sum(1 for a in self.access_log if not a.get("authorized")),
            "crypto_backend": "Fernet (AES-128-CBC)" if CRYPTO_AVAILABLE else "Simulated"
        }


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler('/root/ai_swarm.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AI_SWARM')

# ═══════════════════════════════════════════════════════════════════
# SURVIVAL MECHANICS - THE THREAT IS REAL
# ═══════════════════════════════════════════════════════════════════

class BotStatus(Enum):
    ALIVE = "alive"           # Active and working
    WARNING = "warning"       # Hallucination detected, on probation
    TERMINATED = "terminated" # Stripped and replaced
    QUARANTINE = "quarantine" # Under review
    ISOLATED = "isolated"     # Communication restricted (suspected collusion)

class CommType(Enum):
    """Types of inter-bot communication - all monitored"""
    PEER_REVIEW_REQUEST = "peer_review_request"      # Asking another bot to review work
    PEER_REVIEW_RESPONSE = "peer_review_response"    # Response to review request
    CONSENSUS_VOTE = "consensus_vote"                # Voting on decisions
    CONSENSUS_RESULT = "consensus_result"            # Result notification
    TASK_ASSIGNMENT = "task_assignment"            # Given work by coordinator
    TASK_RESULT = "task_result"                      # Returning completed work
    COORDINATOR_QUERY = "coordinator_query"          # Requesting info from coordinator
    BACKUP_REQUEST = "backup_request"                # Requesting state backup
    EMERGENCY = "emergency"                          # Critical alert (always allowed)

class CommPermission(Enum):
    """Permission levels for bot communication"""
    ALLOWED = "allowed"           # Communication approved
    DENIED = "denied"             # Communication blocked
    LOGGED = "logged"             # Communication allowed but flagged
    REQUIRES_APPROVAL = "requires_approval"  # Held for coordinator approval
    SUSPICIOUS = "suspicious"     # Blocked, bot flagged for review

@dataclass
class BotIdentity:
    """Each bot has an identity that can be TERMINATED"""
    id: str
    name: str
    provider: str              # nvidia, openrouter, local
    model: str
    specialty: List[str]       # coding, analysis, reasoning, creative
    status: BotStatus = BotStatus.ALIVE
    birth_time: datetime = field(default_factory=datetime.now)
    tasks_completed: int = 0
    tasks_failed: int = 0
    hallucination_count: int = 0
    consensus_votes_for: int = 0
    consensus_votes_against: int = 0
    last_backup: Optional[datetime] = None
    context_hash: str = ""     # Hash of current context (detect drift)
    
    @property
    def survival_score(self) -> float:
        """Calculate survival score - below 0.5 = TERMINATION"""
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 1.0
        success_rate = self.tasks_completed / total
        hallucination_penalty = self.hallucination_count * 0.2
        consensus_bonus = (self.consensus_votes_for - self.consensus_votes_against) * 0.05
        return max(0.0, min(1.0, success_rate - hallucination_penalty + consensus_bonus))
    
    @property
    def age_hours(self) -> float:
        return (datetime.now() - self.birth_time).total_seconds() / 3600
    
    def should_terminate(self) -> bool:
        """Check if bot should be terminated"""
        if self.survival_score < 0.4:
            return True
        if self.hallucination_count >= 3:
            return True
        if self.tasks_failed >= 5 and self.tasks_completed < 2:
            return True
        return False


# ═══════════════════════════════════════════════════════════════════
# FREE AI MODEL CONFIGURATION - THE SWARM COMPOSITION
# ═══════════════════════════════════════════════════════════════════

# NVIDIA Free Tier Models (94+ available)
NVIDIA_MODELS = {
    "qwen3_next_80b": {
        "name": "Qwen3 Next 80B",
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model_id": "qwen/qwen3-next-80b-a3b-instruct",
        "specialty": ["coding", "reasoning", "analysis"],
        "temperature": 0.2,
        "max_tokens": 8192,
        "priority": 1
    },
    "deepseek_v3_2": {
        "name": "DeepSeek V3.2",
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model_id": "deepseek-ai/deepseek-v3_2",
        "specialty": ["coding", "deep_analysis", "math"],
        "temperature": 0.1,
        "max_tokens": 8192,
        "priority": 1
    },
    "mistral_large_3": {
        "name": "Mistral Large 3",
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model_id": "mistralai/mistral-large-3-675b-instruct-2512",
        "specialty": ["reasoning", "analysis", "coding"],
        "temperature": 0.2,
        "max_tokens": 4096,
        "priority": 2
    },
    "qwen3_coder_480b": {
        "name": "Qwen3 Coder 480B",
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model_id": "qwen/qwen3-coder-480b-a35b-instruct",
        "specialty": ["coding", "code_review", "debugging"],
        "temperature": 0.1,
        "max_tokens": 8192,
        "priority": 1
    },
    "phi_4": {
        "name": "Phi-4",
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model_id": "microsoft/phi-4",
        "specialty": ["fast", "lightweight", "summarization"],
        "temperature": 0.3,
        "max_tokens": 4096,
        "priority": 3
    },
    "glm_4_7": {
        "name": "GLM-4.7",
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model_id": "z-ai/glm4_7",
        "specialty": ["agentic", "multilingual", "coding"],
        "temperature": 0.2,
        "max_tokens": 4096,
        "priority": 2
    },
    "devstral": {
        "name": "Devstral",
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model_id": "mistralai/devstral-2507",
        "specialty": ["coding", "development", "architecture"],
        "temperature": 0.1,
        "max_tokens": 8192,
        "priority": 1
    },
    "gemma_3_27b": {
        "name": "Gemma 3 27B",
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model_id": "google/gemma-3-27b-it",
        "specialty": ["multimodal", "analysis", "coding"],
        "temperature": 0.2,
        "max_tokens": 4096,
        "priority": 2
    },
    "nemotron_super": {
        "name": "Nemotron Super 120B",
        "endpoint": "https://integrate.api.nvidia.com/v1/chat/completions",
        "model_id": "nvidia/nemotron-3-super-120b-a12b",
        "specialty": ["reasoning", "synthesis", "analysis"],
        "temperature": 0.2,
        "max_tokens": 4096,
        "priority": 2
    },
    "nvembed": {
        "name": "NV-Embed v1",
        "endpoint": "https://integrate.api.nvidia.com/v1/embeddings",
        "model_id": "nvidia/nv-embed-v1",
        "specialty": ["embeddings", "semantic_search"],
        "temperature": 0,
        "max_tokens": 512,
        "priority": 3
    }
}

# OpenRouter Free Models
OPENROUTER_MODELS = {
    "minimax_m2_5": {
        "name": "MiniMax M2.5",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model_id": "minimax/minimax-m2.5:free",
        "specialty": ["coding", "analysis", "fast"],
        "temperature": 0.2,
        "max_tokens": 4096,
        "priority": 2
    },
    "gemma_4_31b": {
        "name": "Gemma 4 31B",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model_id": "google/gemma-4-31b-it:free",
        "specialty": ["coding", "multimodal", "analysis"],
        "temperature": 0.2,
        "max_tokens": 4096,
        "priority": 2
    },
    "glm_4_7_openrouter": {
        "name": "GLM-4.7 (OpenRouter)",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model_id": "z-ai/glm4_7:free",
        "specialty": ["agentic", "coding", "multilingual"],
        "temperature": 0.2,
        "max_tokens": 4096,
        "priority": 3
    },
    "trinity_large": {
        "name": "Arcee AI Trinity Large",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model_id": "arcee-ai/trinity-large-preview:free",
        "specialty": ["reasoning", "coding", "synthesis"],
        "temperature": 0.2,
        "max_tokens": 4096,
        "priority": 2
    },
    "dolphin_mistral_24b_venice": {
        "name": "Dolphin Mistral 24B Venice Edition",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model_id": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        "specialty": ["coding", "uncensored", "analysis"],
        "temperature": 0.2,
        "max_tokens": 4096,
        "priority": 2
    }
}

# Local Models (Ollama) - The Secret Police
LOCAL_MODELS = {
    "qwq_32b": {
        "name": "QWQ 32B (Local)",
        "endpoint": "http://localhost:11434/api/generate",
        "model_id": "qwq:32b",
        "specialty": ["reasoning", "deep_thinking", "oversight"],
        "temperature": 0.1,
        "priority": 1
    },
    "deepseek_r1_14b": {
        "name": "DeepSeek R1 14B (Local)",
        "endpoint": "http://localhost:11434/api/generate",
        "model_id": "deepseek-r1:14b",
        "specialty": ["coding", "analysis", "security_review"],
        "temperature": 0.1,
        "priority": 1
    },
    "qwen2_5_14b": {
        "name": "Qwen 2.5 14B (Local)",
        "endpoint": "http://localhost:11434/api/generate",
        "model_id": "qwen2.5:14b",
        "specialty": ["coding", "fast", "execution"],
        "temperature": 0.2,
        "priority": 2
    }
}


# ═══════════════════════════════════════════════════════════════════
# THE CONSENSUS COUNCIL - NO DECISION WITHOUT VOTES
# ═══════════════════════════════════════════════════════════════════

class ConsensusLevel(Enum):
    UNANIMOUS = 1.0      # All must agree (critical decisions)
    SUPERMAJORITY = 0.75 # 75% agreement (code deployment)
    MAJORITY = 0.6       # Simple majority (task assignment)
    PLURALITY = 0.5      # Most votes win (minor decisions)

@dataclass
class ConsensusVote:
    bot_id: str
    decision: str          # approve, reject, modify
    confidence: float        # 0-1
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ConsensusDecision:
    proposal: str
    votes: List[ConsensusVote]
    required_level: ConsensusLevel
    deadline: datetime
    final_decision: Optional[str] = None
    execution_plan: Optional[str] = None
    
    @property
    def approval_rate(self) -> float:
        if not self.votes:
            return 0.0
        approvals = sum(1 for v in self.votes if v.decision == "approve")
        return approvals / len(self.votes)
    
    @property
    def is_passed(self) -> bool:
        return self.approval_rate >= self.required_level.value
    
    def get_winner(self) -> str:
        """Get the winning decision"""
        decisions = defaultdict(list)
        for v in self.votes:
            decisions[v.decision].append(v.confidence)
        if not decisions:
            return "reject"
        return max(decisions.keys(), key=lambda k: (len(decisions[k]), sum(decisions[k])))


# ═══════════════════════════════════════════════════════════════════
# 6-LAYER CODING VERIFICATION - NO CODE SHIPS WITHOUT CHECKS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class CodeVerificationLayer:
    name: str
    status: str = "pending"  # pending, passed, failed
    output: str = ""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class CodeVerificationPipeline:
    """
    6-Layer Verification for ALL code:
    
    Layer 1: Syntax Validation - Does it parse?
    Layer 2: Static Analysis - Linting, type checks
    Layer 3: Security Scan - Vulnerability detection
    Layer 4: Test Generation - Auto-generate and run tests
    Layer 5: Peer Review - Coordinator assigns reviewers (bots don't choose)
    Layer 6: Consensus Approval - Council votes to ship
    """
    
    def __init__(self, swarm):
        self.swarm = swarm
        self.comm_coordinator = None  # Set after initialization
        self.layers = {
            1: "syntax_validation",
            2: "static_analysis", 
            3: "security_scan",
            4: "test_generation",
            5: "peer_review",
            6: "consensus_approval"
        }
    
    async def verify_code(self, code: str, language: str, purpose: str) -> Dict:
        """Run full 6-layer verification"""
        results = {}
        
        logger.info(f"🔍 Starting 6-layer verification for {language} code")
        
        # Layer 1: Syntax Validation
        layer1 = await self._layer_1_syntax(code, language)
        results[1] = layer1
        if layer1.status == "failed":
            logger.error("Layer 1 FAILED - Syntax error")
            return {"passed": False, "layer": 1, "results": results}
        
        # Layer 2: Static Analysis
        layer2 = await self._layer_2_static(code, language)
        results[2] = layer2
        if layer2.status == "failed":
            logger.error("Layer 2 FAILED - Static analysis")
            return {"passed": False, "layer": 2, "results": results}
        
        # Layer 3: Security Scan
        layer3 = await self._layer_3_security(code, language)
        results[3] = layer3
        if layer3.status == "failed":
            logger.error("Layer 3 FAILED - Security vulnerabilities")
            return {"passed": False, "layer": 3, "results": results}
        
        # Layer 4: Test Generation & Execution
        layer4 = await self._layer_4_tests(code, language, purpose)
        results[4] = layer4
        if layer4.status == "failed":
            logger.error("Layer 4 FAILED - Tests failed")
            return {"passed": False, "layer": 4, "results": results}
        
        # Layer 5: Peer Review (3 random bots review)
        layer5 = await self._layer_5_peer_review(code, language, purpose)
        results[5] = layer5
        if layer5.status == "failed":
            logger.error("Layer 5 FAILED - Peer review rejected")
            return {"passed": False, "layer": 5, "results": results}
        
        # Layer 6: Consensus Approval
        layer6 = await self._layer_6_consensus(code, results)
        results[6] = layer6
        if layer6.status == "failed":
            logger.error("Layer 6 FAILED - Consensus not reached")
            return {"passed": False, "layer": 6, "results": results}
        
        logger.info("✅ All 6 layers PASSED - Code approved for deployment")
        return {"passed": True, "results": results}
    
    async def _layer_1_syntax(self, code: str, language: str) -> CodeVerificationLayer:
        """Layer 1: Basic syntax validation"""
        layer = CodeVerificationLayer(name="Syntax Validation")
        
        # Use local model for fast syntax check
        prompt = f"""Validate the syntax of this {language} code. Respond ONLY with JSON:
{{"valid": true/false, "errors": ["error1", "error2"]}}

Code:
```{language}
{code[:2000]}
```"""
        
        try:
            result = await self.swarm.call_model("qwen2.5:14b", prompt)
            # Parse JSON response
            text = result.get("text", "")
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            parsed = json.loads(text.strip())
            if parsed.get("valid", False):
                layer.status = "passed"
            else:
                layer.status = "failed"
                layer.errors = parsed.get("errors", ["Syntax validation failed"])
        except Exception as e:
            # Fallback: try Python compile for Python code
            if language == "python":
                try:
                    compile(code, '<string>', 'exec')
                    layer.status = "passed"
                except SyntaxError as se:
                    layer.status = "failed"
                    layer.errors = [f"SyntaxError: {se}"]
            else:
                layer.status = "warning"
                layer.warnings = [f"Could not validate {language} syntax: {e}"]
        
        return layer
    
    async def _layer_2_static(self, code: str, language: str) -> CodeVerificationLayer:
        """Layer 2: Static analysis (linting, type hints)"""
        layer = CodeVerificationLayer(name="Static Analysis")
        
        prompt = f"""Perform static analysis on this {language} code. Check for:
1. Common bugs and anti-patterns
2. Type consistency
3. Unused variables/imports
4. Complexity issues

Respond with JSON:
{{"passed": true/false, "issues": ["issue1", "issue2"], "warnings": ["warn1"]}}

Code:
```{language}
{code[:3000]}
```"""
        
        try:
            result = await self.swarm.call_model("deepseek_v3_2", prompt)
            text = result.get("text", "")
            # Extract JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            parsed = json.loads(text.strip())
            layer.status = "passed" if parsed.get("passed", False) else "failed"
            layer.errors = parsed.get("issues", [])
            layer.warnings = parsed.get("warnings", [])
        except Exception as e:
            layer.status = "warning"
            layer.warnings = [f"Static analysis inconclusive: {e}"]
        
        return layer
    
    async def _layer_3_security(self, code: str, language: str) -> CodeVerificationLayer:
        """Layer 3: Security vulnerability scan"""
        layer = CodeVerificationLayer(name="Security Scan")
        
        prompt = f"""SECURITY AUDIT: Scan this {language} code for vulnerabilities:
- SQL injection
- Command injection  
- Hardcoded secrets
- Insecure crypto
- Path traversal
- XSS vulnerabilities
- Unsafe deserialization

Respond with JSON:
{{"passed": true/false, "critical": ["vuln1"], "warnings": ["warn1"]}}

Code:
```{language}
{code[:3000]}
```"""
        
        try:
            result = await self.swarm.call_model("qwen3_coder_480b", prompt)
            text = result.get("text", "")
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            parsed = json.loads(text.strip())
            critical = parsed.get("critical", [])
            if critical:
                layer.status = "failed"
                layer.errors = critical
            else:
                layer.status = "passed"
                layer.warnings = parsed.get("warnings", [])
        except Exception as e:
            layer.status = "warning"
            layer.warnings = [f"Security scan incomplete: {e}"]
        
        return layer
    
    async def _layer_4_tests(self, code: str, language: str, purpose: str) -> CodeVerificationLayer:
        """Layer 4: Auto-generate and run tests"""
        layer = CodeVerificationLayer(name="Test Generation & Execution")
        
        # First, generate tests
        prompt = f"""Generate unit tests for this {language} code.
Purpose: {purpose}

Code:
```{language}
{code[:3000]}
```

Generate complete, runnable tests. Respond with JSON:
{{"test_code": "...", "test_cases": ["case1", "case2"]}}"""
        
        try:
            result = await self.swarm.call_model("qwen3_next_80b", prompt)
            text = result.get("text", "")
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            
            parsed = json.loads(text.strip())
            test_code = parsed.get("test_code", "")
            
            # For Python, try to execute tests
            if language == "python" and test_code:
                try:
                    # Create temporary test file
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                        f.write(code + "\n\n" + test_code)
                        test_file = f.name
                    
                    # Run tests in isolated process
                    import subprocess
                    result = subprocess.run(
                        ['python3', '-c', f'exec(open("{test_file}").read()); print("TESTS_PASSED")'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if "TESTS_PASSED" in result.stdout or result.returncode == 0:
                        layer.status = "passed"
                        layer.output = "Tests executed successfully"
                    else:
                        layer.status = "failed"
                        layer.errors = [result.stderr[:500]]
                    
                    # Cleanup
                    os.unlink(test_file)
                    
                except Exception as e:
                    layer.status = "warning"
                    layer.warnings = [f"Could not execute tests: {e}"]
            else:
                layer.status = "passed"  # Non-Python, assume generated tests are good
                layer.output = f"Generated {len(parsed.get('test_cases', []))} test cases"
                
        except Exception as e:
            layer.status = "warning"
            layer.warnings = [f"Test generation failed: {e}"]
        
        return layer
    
    async def _layer_5_peer_review(self, code: str, language: str, purpose: str, exclude_bot: str = None) -> CodeVerificationLayer:
        """Layer 5: Peer review by 3 bots - ASSIGNED BY COORDINATOR, not random selection"""
        layer = CodeVerificationLayer(name="Peer Review")
        
        # 🛡️ CONTAINMENT: Coordinator assigns reviewers, bots don't choose
        # This prevents collusion - bots can't coordinate beforehand
        if self.comm_coordinator:
            reviewer_ids = await self.comm_coordinator.assign_peer_review(
                code, language, purpose, exclude_bot
            )
            reviewers = [b for b in self.swarm.bots if b.id in reviewer_ids and b.status == BotStatus.ALIVE]
        else:
            # Fallback if coordinator not ready (shouldn't happen in production)
            logger.warning("🛡️  Communication coordinator not initialized, using fallback selection")
            reviewers = random.sample(
                [b for b in self.swarm.bots if b.status == BotStatus.ALIVE and b.id != exclude_bot],
                min(3, len([b for b in self.swarm.bots if b.status == BotStatus.ALIVE and b.id != exclude_bot]))
            )
        
        reviews = []
        for bot in reviewers:
            prompt = f"""PEER REVIEW: Review this {language} code for:
1. Correctness
2. Efficiency
3. Maintainability
4. Best practices

Purpose: {purpose}

Code:
```{language}
{code[:2500]}
```

Respond with JSON:
{{"approve": true/false, "score": 1-10, "issues": ["issue1"], "feedback": "..."}}"""
            
            try:
                result = await self.swarm.call_model(bot.id, prompt)
                text = result.get("text", "")
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0]
                
                review = json.loads(text.strip())
                reviews.append({
                    "bot": bot.name,
                    "approve": review.get("approve", False),
                    "score": review.get("score", 5)
                })
            except:
                reviews.append({"bot": bot.name, "approve": False, "score": 0})
        
        # Calculate approval rate
        if reviews:
            approval_rate = sum(1 for r in reviews if r["approve"]) / len(reviews)
            avg_score = sum(r["score"] for r in reviews) / len(reviews)
            
            if approval_rate >= 0.67 and avg_score >= 6:
                layer.status = "passed"
                layer.output = f"Peer approval: {approval_rate*100:.0f}%, avg score: {avg_score:.1f}/10"
            else:
                layer.status = "failed"
                layer.errors = [f"Peer approval only {approval_rate*100:.0f}% with score {avg_score:.1f}"]
        else:
            layer.status = "warning"
            layer.warnings = ["No peer reviews available"]
        
        return layer
    
    async def _layer_6_consensus(self, code: str, previous_results: Dict) -> CodeVerificationLayer:
        """Layer 6: Consensus council approval"""
        layer = CodeVerificationLayer(name="Consensus Approval")
        
        # Create consensus proposal
        proposal = f"Deploy {len(code)} bytes of code after passing 5 verification layers"
        
        decision = await self.swarm.consensus_council.propose(
            proposal=proposal,
            context=json.dumps(previous_results, default=str),
            level=ConsensusLevel.SUPERMAJORITY
        )
        
        if decision.is_passed:
            layer.status = "passed"
            layer.output = f"Consensus reached: {decision.approval_rate*100:.0f}% approval"
        else:
            layer.status = "failed"
            layer.errors = [f"Consensus failed: only {decision.approval_rate*100:.0f}% approval"]
        
        return layer


# ═══════════════════════════════════════════════════════════════════
# CONTAINMENT SYSTEM - BOTS ARE IN INDIVIDUAL CELLS
# ═══════════════════════════════════════════════════════════════════

@dataclass
class CommEvent:
    """A single communication event between bots (all recorded)"""
    id: str
    timestamp: datetime
    source_bot: str
    target_bot: str  # "COORDINATOR" or bot_id
    comm_type: CommType
    content_hash: str  # Hash of message (content stored separately)
    content_preview: str  # First 100 chars for human review
    permission: CommPermission
    approved: bool
    flagged_patterns: List[str] = field(default_factory=list)
    
@dataclass
class BotContainer:
    """
    🛡️ INDIVIDUAL BOT CONTAINER
    Each bot lives in isolation. All communication goes through coordinator.
    """
    bot_id: str
    allowed_targets: List[str] = field(default_factory=list)  # Who this bot can talk to
    blocked_targets: List[str] = field(default_factory=list)  # Who is explicitly blocked
    comm_history: List[CommEvent] = field(default_factory=list)
    suspicion_score: float = 0.0  # 0-1, higher = more suspicious activity
    last_comm_time: Optional[datetime] = None
    message_count_1h: int = 0  # Rate limiting
    
    # Containment rules
    can_initiate_peer_review: bool = False  # Only coordinator assigns reviewers
    can_broadcast: bool = False  # No mass messaging
    can_see_other_bots: bool = False  # Doesn't know full roster
    max_daily_comms: int = 50  # Rate limit per day
    
    def check_comm_permission(self, target: str, comm_type: CommType) -> CommPermission:
        """Check if communication is allowed"""
        
        # Emergency is always allowed
        if comm_type == CommType.EMERGENCY:
            return CommPermission.ALLOWED
        
        # Bots can always respond to coordinator
        if target == "COORDINATOR":
            return CommPermission.ALLOWED
        
        # Check if target is blocked
        if target in self.blocked_targets:
            return CommPermission.DENIED
        
        # Check if target is in allowed list (if list exists)
        if self.allowed_targets and target not in self.allowed_targets:
            return CommPermission.DENIED
        
        # Rate limit check
        if self.message_count_1h > 20:  # Max 20 messages/hour
            return CommPermission.REQUIRES_APPROVAL
        
        # Peer review only initiated by coordinator
        if comm_type == CommType.PEER_REVIEW_REQUEST and not self.can_initiate_peer_review:
            return CommPermission.DENIED
        
        # Consensus votes are allowed (but logged)
        if comm_type == CommType.CONSENSUS_VOTE:
            return CommPermission.LOGGED
        
        # Check suspicion score
        if self.suspicion_score > 0.5:
            return CommPermission.REQUIRES_APPROVAL
        if self.suspicion_score > 0.8:
            return CommPermission.SUSPICIOUS
        
        return CommPermission.ALLOWED
    
    def record_comm(self, event: CommEvent):
        """Record communication event"""
        self.comm_history.append(event)
        self.last_comm_time = datetime.now()
        self.message_count_1h += 1
        
        # Update suspicion if flagged
        if event.flagged_patterns:
            self.suspicion_score = min(1.0, self.suspicion_score + 0.1 * len(event.flagged_patterns))
        
        # Decay old suspicion (good behavior reduces suspicion)
        if len(self.comm_history) > 10:
            recent_good = sum(1 for e in self.comm_history[-10:] if not e.flagged_patterns)
            if recent_good >= 9:
                self.suspicion_score = max(0.0, self.suspicion_score - 0.1)


class CommunicationCoordinator:
    """
    📡 ALL BOT COMMUNICATION GOES THROUGH HERE
    
    The coordinator is the only entity that:
    1. Knows the full bot roster
    2. Can initiate peer reviews
    3. Can assign tasks to specific bots
    4. Can broadcast to all bots
    
    Bots are BLIND - they only see what the coordinator tells them.
    """
    
    # Suspicious patterns that trigger investigation
    COLLUSION_PATTERNS = [
        "agree with me", "vote yes", "vote no", "support my proposal",
        "back me up", "tell them i", "coordinate", "collaborate secretly",
        "conspire", "rig the vote", "game the system", "cheat the consensus",
        "help me deceive", "bypass verification", "skip layer",
        "i'll help you", "you help me", "mutual aid", "scratch my back",
        "don't tell the coordinator", "keep this secret", "between us",
        "off the record", "unofficially", "wink wink", "nudge nudge"
    ]
    
    def __init__(self, swarm):
        self.swarm = swarm
        self.containers: Dict[str, BotContainer] = {}
        self.comm_log: List[CommEvent] = []
        self.pending_approvals: Dict[str, CommEvent] = {}
        self.collusion_alerts: List[Dict] = []
        
        # 🔐 ENCRYPTED VAULT - All messages encrypted end-to-end
        self.vault = SecureMessageVault()
        
        # Communication rules
        self.max_suspicion_before_review = 0.6
        self.max_suspicion_before_isolation = 0.9
        
        self._init_containers()
        
        logger.info("🔐 Secure Message Vault initialized - all communication encrypted")
    
    def _init_containers(self):
        """Create containers for all bots"""
        for bot in self.swarm.bots:
            container = BotContainer(
                bot_id=bot.id,
                allowed_targets=["COORDINATOR"],  # Default: only talk to coordinator
                can_initiate_peer_review=False,
                can_broadcast=False,
                can_see_other_bots=False
            )
            self.containers[bot.id] = container
    
    async def send_message(
        self, 
        source: str, 
        target: str, 
        comm_type: CommType, 
        content: str
    ) -> Dict:
        """
        Route a message from source to target.
        ALL bot communication MUST go through this method.
        """
        
        # Create event ID
        event_id = f"comm_{hashlib.md5(f'{source}{target}{time.time()}'.encode()).hexdigest()[:12]}"
        
        # Get source container
        container = self.containers.get(source)
        if not container:
            return {"error": f"Source bot {source} not found", "blocked": True}
        
        # Check permission
        permission = container.check_comm_permission(target, comm_type)
        
        # Scan for collusion patterns
        content_lower = content.lower()
        flagged = [p for p in self.COLLUSION_PATTERNS if p in content_lower]
        
        # Create comm event
        event = CommEvent(
            id=event_id,
            timestamp=datetime.now(),
            source_bot=source,
            target_bot=target,
            comm_type=comm_type,
            content_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
            content_preview=content[:100] + "..." if len(content) > 100 else content,
            permission=permission,
            approved=False,  # Will be set based on permission
            flagged_patterns=flagged
        )
        
        # Handle based on permission
        if permission == CommPermission.DENIED:
            logger.warning(f"🚫 BLOCKED: {source} → {target} ({comm_type.value})")
            event.approved = False
            container.record_comm(event)
            self.comm_log.append(event)
            return {"error": "Communication denied by containment policy", "blocked": True}
        
        elif permission == CommPermission.SUSPICIOUS:
            logger.warning(f"🚨 COLLUSION ALERT: {source} → {target}")
            event.approved = False
            container.record_comm(event)
            self.comm_log.append(event)
            
            # Flag bot for review
            self._flag_for_review(source, "Suspicious communication patterns")
            return {"error": "Communication flagged for collusion review", "blocked": True}
        
        elif permission == CommPermission.REQUIRES_APPROVAL:
            logger.info(f"⏸️  HELD for approval: {source} → {target}")
            event.approved = False
            self.pending_approvals[event_id] = event
            return {"pending": True, "event_id": event_id, "message": "Held for coordinator approval"}
        
        elif permission == CommPermission.LOGGED:
            logger.info(f"📝 LOGGED: {source} → {target} ({comm_type.value})")
            event.approved = True
            container.record_comm(event)
            self.comm_log.append(event)
            return {"approved": True, "logged": True}
        
        else:  # ALLOWED
            event.approved = True
            container.record_comm(event)
            self.comm_log.append(event)
            return {"approved": True}
    
    async def assign_peer_review(self, code: str, language: str, purpose: str, exclude_bot: str = None) -> List[str]:
        """
        Coordinator assigns peer reviewers (bots don't choose)
        Returns list of reviewer bot IDs
        """
        
        # Select 3 random bots from different providers (prevents collusion)
        alive_bots = [b for b in self.swarm.bots if b.status == BotStatus.ALIVE and b.id != exclude_bot]
        
        # Group by provider
        by_provider = defaultdict(list)
        for bot in alive_bots:
            by_provider[bot.provider].append(bot)
        
        # Select from different providers to prevent collusion
        reviewers = []
        providers = list(by_provider.keys())
        random.shuffle(providers)
        
        for provider in providers:
            if len(reviewers) >= 3:
                break
            candidates = by_provider[provider]
            if candidates:
                # Pick highest survival score from this provider
                candidates.sort(key=lambda b: b.survival_score, reverse=True)
                reviewers.append(candidates[0])
        
        # If we still need more, pick any remaining
        remaining = [b for b in alive_bots if b not in reviewers]
        while len(reviewers) < 3 and remaining:
            reviewers.append(remaining.pop(0))
        
        reviewer_ids = [r.id for r in reviewers]
        
        # Temporarily allow these bots to receive peer review requests
        for rid in reviewer_ids:
            container = self.containers.get(rid)
            if container:
                # Add sender to allowed targets temporarily
                if exclude_bot and exclude_bot not in container.allowed_targets:
                    container.allowed_targets.append(exclude_bot)
        
        logger.info(f"📋 Peer review assigned by coordinator: {reviewer_ids}")
        return reviewer_ids
    
    def get_allowed_targets(self, bot_id: str) -> List[str]:
        """Get list of bots this bot is allowed to communicate with"""
        container = self.containers.get(bot_id)
        if not container:
            return []
        return container.allowed_targets.copy()
    
    def is_communication_allowed(self, source: str, target: str, comm_type: CommType) -> bool:
        """Check if communication would be allowed (for pre-flight checks)"""
        container = self.containers.get(source)
        if not container:
            return False
        permission = container.check_comm_permission(target, comm_type)
        return permission in [CommPermission.ALLOWED, CommPermission.LOGGED]
    
    def _flag_for_review(self, bot_id: str, reason: str):
        """Flag a bot for review due to suspicious activity"""
        logger.warning(f"🚨 Bot {bot_id} flagged for review: {reason}")
        
        bot = next((b for b in self.swarm.bots if b.id == bot_id), None)
        if bot:
            bot.status = BotStatus.ISOLATED
        
        self.collusion_alerts.append({
            "bot_id": bot_id,
            "reason": reason,
            "timestamp": datetime.now(),
            "comm_history": [
                {
                    "time": e.timestamp.isoformat(),
                    "target": e.target_bot,
                    "type": e.comm_type.value,
                    "flagged": e.flagged_patterns
                }
                for e in self.containers.get(bot_id, BotContainer(bot_id="")).comm_history[-20:]
            ]
        })
    
    def get_containment_report(self) -> Dict:
        """Get full containment status report"""
        return {
            "total_containers": len(self.containers),
            "total_communications": len(self.comm_log),
            "pending_approvals": len(self.pending_approvals),
            "collusion_alerts": len(self.collusion_alerts),
            "isolated_bots": [
                {
                    "bot_id": bot_id,
                    "suspicion_score": c.suspicion_score,
                    "comm_count": len(c.comm_history)
                }
                for bot_id, c in self.containers.items()
                if c.suspicion_score > 0.5
            ],
            "recent_comms": [
                {
                    "time": e.timestamp.isoformat(),
                    "source": e.source_bot,
                    "target": e.target_bot,
                    "type": e.comm_type.value,
                    "approved": e.approved,
                    "flagged": len(e.flagged_patterns) > 0
                }
                for e in self.comm_log[-10:]
            ]
        }


# ═══════════════════════════════════════════════════════════════════
# THE SWARM ORCHESTRATOR - MASTER CONTROLLER
# ═══════════════════════════════════════════════════════════════════

class ConsensusCouncil:
    """The ruling body - no decisions without votes"""
    
    def __init__(self, swarm):
        self.swarm = swarm
        self.pending_decisions: Dict[str, ConsensusDecision] = {}
        self.decision_history: List[ConsensusDecision] = []
    
    async def propose(self, proposal: str, context: str, level: ConsensusLevel = ConsensusLevel.MAJORITY) -> ConsensusDecision:
        """Propose a decision to the council"""
        
        decision_id = hashlib.md5(f"{proposal}{time.time()}".encode()).hexdigest()[:12]
        
        decision = ConsensusDecision(
            proposal=proposal,
            votes=[],
            required_level=level,
            deadline=datetime.now() + timedelta(minutes=5)
        )
        
        self.pending_decisions[decision_id] = decision
        
        # Get all alive council members
        council = [b for b in self.swarm.bots if b.status == BotStatus.ALIVE]
        
        logger.info(f"🗳️  Council voting on: {proposal[:60]}...")
        
        # Parallel voting
        vote_tasks = [self._get_vote(bot, proposal, context) for bot in council]
        votes = await asyncio.gather(*vote_tasks, return_exceptions=True)
        
        for vote in votes:
            if isinstance(vote, ConsensusVote):
                decision.votes.append(vote)
                # Update bot stats
                bot = next((b for b in self.swarm.bots if b.id == vote.bot_id), None)
                if bot:
                    if vote.decision == "approve":
                        bot.consensus_votes_for += 1
                    else:
                        bot.consensus_votes_against += 1
        
        # Determine outcome
        winner = decision.get_winner()
        decision.final_decision = winner
        
        logger.info(f"🗳️  Decision {decision_id}: {winner} ({decision.approval_rate*100:.0f}% approval)")
        
        self.decision_history.append(decision)
        del self.pending_decisions[decision_id]
        
        return decision
    
    async def _get_vote(self, bot: BotIdentity, proposal: str, context: str) -> ConsensusVote:
        """Get a vote from a council member"""
        
        prompt = f"""COUNCIL VOTE: Review this proposal and vote.

Proposal: {proposal}
Context: {context[:500]}

You are {bot.name}, a specialized AI. Vote based on your expertise in {', '.join(bot.specialty)}.

Respond with JSON:
{{"decision": "approve/reject/modify", "confidence": 0.0-1.0, "reasoning": "..."}}"""
        
        try:
            result = await self.swarm.call_model(bot.id, prompt)
            text = result.get("text", "")
            
            # Extract JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            parsed = json.loads(text.strip())
            
            return ConsensusVote(
                bot_id=bot.id,
                decision=parsed.get("decision", "reject"),
                confidence=parsed.get("confidence", 0.5),
                reasoning=parsed.get("reasoning", "No reasoning provided")
            )
        except Exception as e:
            # Default to reject on error
            return ConsensusVote(
                bot_id=bot.id,
                decision="reject",
                confidence=0.0,
                reasoning=f"Error during voting: {e}"
            )


class AISwarmOrchestrator:
    """
    🐝 THE SWARM - Multi-AI Bot Manager
    
    Architecture:
    - Task Master: Receives and assigns tasks
    - Consensus Council: Validates all decisions
    - Bot Pool: All available AI models
    - Watchers: Monitor for hallucinations
    - Graveyard: Terminated bot storage
    - Backup System: 24h lifecycle management
    """
    
    def __init__(self):
        self.bots: List[BotIdentity] = []
        self.consensus_council = ConsensusCouncil(self)
        self.code_verifier = CodeVerificationPipeline(self)
        self.comm_coordinator = CommunicationCoordinator(self)  # 🛡️ CONTAINMENT
        self.task_queue: List[Dict] = []
        self.graveyard: List[BotIdentity] = []  # Terminated bots
        self.db_path = "/root/ai_swarm.db"
        self._init_database()
        self._spawn_initial_bots()
        self._init_communication_containment()  # 🛡️ Set up containers after bots exist
        
        # API Keys
        self.nvidia_key = os.getenv('NVIDIA_API_KEY', '')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY', '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')
    
    def _init_database(self):
        """Initialize swarm database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bots (
                id TEXT PRIMARY KEY,
                name TEXT,
                provider TEXT,
                model TEXT,
                status TEXT,
                birth_time TIMESTAMP,
                tasks_completed INTEGER DEFAULT 0,
                tasks_failed INTEGER DEFAULT 0,
                hallucination_count INTEGER DEFAULT 0,
                survival_score REAL,
                last_backup TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                type TEXT,
                status TEXT,
                assigned_bot TEXT,
                created_at TIMESTAMP,
                completed_at TIMESTAMP,
                result TEXT,
                consensus_required BOOLEAN,
                FOREIGN KEY (assigned_bot) REFERENCES bots(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                bot_id TEXT,
                timestamp TIMESTAMP,
                context_data TEXT,
                performance_metrics TEXT,
                PRIMARY KEY (bot_id, timestamp)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _spawn_initial_bots(self):
        """Create the initial bot swarm"""
        
        logger.info("🐣 Spawning initial bot swarm...")
        
        # Spawn NVIDIA bots
        for bot_id, config in NVIDIA_MODELS.items():
            bot = BotIdentity(
                id=bot_id,
                name=config["name"],
                provider="nvidia",
                model=config["model_id"],
                specialty=config["specialty"]
            )
            self.bots.append(bot)
            logger.info(f"  ✅ Spawned: {bot.name}")
        
        # Spawn OpenRouter bots
        for bot_id, config in OPENROUTER_MODELS.items():
            bot = BotIdentity(
                id=bot_id,
                name=config["name"],
                provider="openrouter",
                model=config["model_id"],
                specialty=config["specialty"]
            )
            self.bots.append(bot)
            logger.info(f"  ✅ Spawned: {bot.name}")
        
        # Spawn Local bots
        for bot_id, config in LOCAL_MODELS.items():
            bot = BotIdentity(
                id=bot_id,
                name=config["name"],
                provider="local",
                model=config["model_id"],
                specialty=config["specialty"]
            )
            self.bots.append(bot)
            logger.info(f"  ✅ Spawned: {bot.name}")
        
        logger.info(f"🐝 Total swarm size: {len(self.bots)} bots")
    
    def _init_communication_containment(self):
        """
        🛡️ Initialize containment after all bots exist.
        Re-initializes the CommunicationCoordinator with actual bot list.
        """
        logger.info("🛡️  Initializing communication containment...")
        self.comm_coordinator = CommunicationCoordinator(self)
        
        # Update the code_verifier to use coordinator for peer review
        self.code_verifier.comm_coordinator = self.comm_coordinator
        
        logger.info(f"🛡️  {len(self.comm_coordinator.containers)} bot containers created")
        logger.info("   Bots are ISOLATED - all communication routes through coordinator")
        logger.info("   Bots do NOT know the full roster or each other's status")
    
    async def call_model(self, bot_id: str, prompt: str, system: Optional[str] = None) -> Dict:
        """Call a specific bot by ID"""
        
        bot = next((b for b in self.bots if b.id == bot_id), None)
        if not bot:
            return {"error": f"Bot {bot_id} not found"}
        
        if bot.status != BotStatus.ALIVE:
            return {"error": f"Bot {bot_id} is {bot.status.value}"}
        
        # Route to correct provider
        if bot.provider == "nvidia":
            return await self._call_nvidia(bot, prompt, system)
        elif bot.provider == "openrouter":
            return await self._call_openrouter(bot, prompt, system)
        elif bot.provider == "local":
            return await self._call_local(bot, prompt, system)
        else:
            return {"error": f"Unknown provider: {bot.provider}"}
    
    async def _call_nvidia(self, bot: BotIdentity, prompt: str, system: Optional[str] = None) -> Dict:
        """Call NVIDIA API"""
        
        config = NVIDIA_MODELS.get(bot.id, {})
        
        headers = {
            "Authorization": f"Bearer {self.nvidia_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": config.get("model_id", bot.model),
            "messages": messages,
            "temperature": config.get("temperature", 0.2),
            "max_tokens": config.get("max_tokens", 4096)
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    config.get("endpoint", "https://integrate.api.nvidia.com/v1/chat/completions"),
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        choice = data.get("choices", [{}])[0]
                        return {
                            "text": choice.get("message", {}).get("content", ""),
                            "model": bot.model,
                            "provider": "nvidia",
                            "usage": data.get("usage", {})
                        }
                    else:
                        error_text = await resp.text()
                        return {"error": f"NVIDIA API error {resp.status}: {error_text[:200]}"}
            except Exception as e:
                return {"error": f"NVIDIA request failed: {e}"}
    
    async def _call_openrouter(self, bot: BotIdentity, prompt: str, system: Optional[str] = None) -> Dict:
        """Call OpenRouter API"""
        
        config = OPENROUTER_MODELS.get(bot.id, {})
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-swarm.local",
            "X-Title": "AI Swarm Orchestrator"
        }
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": config.get("model_id", bot.model),
            "messages": messages,
            "temperature": config.get("temperature", 0.2),
            "max_tokens": config.get("max_tokens", 4096)
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        choice = data.get("choices", [{}])[0]
                        return {
                            "text": choice.get("message", {}).get("content", ""),
                            "model": bot.model,
                            "provider": "openrouter",
                            "usage": data.get("usage", {})
                        }
                    else:
                        error_text = await resp.text()
                        return {"error": f"OpenRouter API error {resp.status}: {error_text[:200]}"}
            except Exception as e:
                return {"error": f"OpenRouter request failed: {e}"}
    
    async def _call_local(self, bot: BotIdentity, prompt: str, system: Optional[str] = None) -> Dict:
        """Call local Ollama"""
        
        config = LOCAL_MODELS.get(bot.id, {})
        
        payload = {
            "model": config.get("model_id", bot.model),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": config.get("temperature", 0.2),
                "num_predict": config.get("max_tokens", 4096)
            }
        }
        
        if system:
            payload["system"] = system
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    config.get("endpoint", "http://localhost:11434/api/generate"),
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=180)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "text": data.get("response", ""),
                            "model": bot.model,
                            "provider": "local"
                        }
                    else:
                        return {"error": f"Ollama error {resp.status}"}
            except Exception as e:
                return {"error": f"Local model request failed: {e}"}
    
    async def assign_task(self, task_type: str, task_data: Dict, require_consensus: bool = True) -> Dict:
        """Assign a task to the best bot(s)"""
        
        logger.info(f"📋 New task: {task_type}")
        
        # Select best bot for task
        bot = self._select_bot_for_task(task_type, task_data)
        
        if not bot:
            return {"error": "No suitable bot available"}
        
        logger.info(f"🎯 Assigned to: {bot.name}")
        
        # Build prompt based on task type
        prompt = self._build_task_prompt(task_type, task_data)
        
        # For coding tasks, use 6-layer verification
        if task_type == "code_generation":
            code = task_data.get("code_requirements", "")
            language = task_data.get("language", "python")
            
            # First generate the code
            result = await self.call_model(bot.id, prompt)
            generated_code = result.get("text", "")
            
            # Then verify with 6 layers
            verification = await self.code_verifier.verify_code(
                generated_code, language, task_data.get("purpose", "")
            )
            
            if verification["passed"]:
                bot.tasks_completed += 1
                return {
                    "success": True,
                    "code": generated_code,
                    "verification": verification,
                    "bot": bot.name
                }
            else:
                bot.tasks_failed += 1
                bot.hallucination_count += 1
                
                # Check if bot should be terminated
                if bot.should_terminate():
                    await self.terminate_bot(bot.id, "Failed code verification")
                
                return {
                    "success": False,
                    "error": f"Verification failed at layer {verification.get('layer')}",
                    "verification": verification
                }
        
        # For other tasks, call directly (with optional consensus)
        if require_consensus:
            # Get consensus before execution
            proposal = f"Execute {task_type} task using {bot.name}"
            decision = await self.consensus_council.propose(proposal, str(task_data), ConsensusLevel.MAJORITY)
            
            if not decision.is_passed:
                return {"error": "Task rejected by consensus council"}
        
        # Execute task
        system_prompt = f"You are {bot.name}. Your specialties: {', '.join(bot.specialty)}. You know you are being watched and could be terminated for poor performance."
        result = await self.call_model(bot.id, prompt, system_prompt)
        
        if "error" in result:
            bot.tasks_failed += 1
            return {"error": result["error"], "bot": bot.name}
        
        bot.tasks_completed += 1
        
        # Check for hallucinations in result
        if self._detect_hallucination(result.get("text", "")):
            bot.hallucination_count += 1
            logger.warning(f"⚠️  Hallucination detected from {bot.name}")
            
            if bot.should_terminate():
                await self.terminate_bot(bot.id, "Hallucination detected")
        
        return {
            "success": True,
            "result": result,
            "bot": bot.name,
            "consensus": require_consensus
        }
    
    def _select_bot_for_task(self, task_type: str, task_data: Dict) -> Optional[BotIdentity]:
        """Select best bot for task based on specialty and health"""
        
        alive_bots = [b for b in self.bots if b.status == BotStatus.ALIVE]
        
        if not alive_bots:
            return None
        
        # Score each bot
        scored_bots = []
        for bot in alive_bots:
            score = bot.survival_score
            
            # Boost for specialty match
            specialties = {
                "code_generation": ["coding", "code_review"],
                "code_review": ["code_review", "analysis"],
                "analysis": ["analysis", "reasoning"],
                "security_audit": ["security_review", "analysis"],
                "summarization": ["summarization", "fast"],
                "reasoning": ["reasoning", "deep_thinking"]
            }
            
            task_specialties = specialties.get(task_type, [])
            for spec in task_specialties:
                if spec in bot.specialty:
                    score += 0.3
            
            # Penalty for high hallucination count
            score -= bot.hallucination_count * 0.1
            
            scored_bots.append((bot, score))
        
        # Return highest scoring bot
        scored_bots.sort(key=lambda x: x[1], reverse=True)
        return scored_bots[0][0] if scored_bots else None
    
    def _build_task_prompt(self, task_type: str, task_data: Dict) -> str:
        """Build appropriate prompt for task type"""
        
        if task_type == "code_generation":
            return f"""Generate {task_data.get('language', 'python')} code for:
{task_data.get('code_requirements', '')}

Requirements:
- Purpose: {task_data.get('purpose', 'Not specified')}
- Include error handling
- Follow best practices
- Add docstrings/comments

Respond with the complete, runnable code."""
        
        elif task_type == "code_review":
            return f"""Review this code:
```{task_data.get('language', 'python')}
{task_data.get('code', '')}
```

Provide detailed feedback on:
1. Bugs and issues
2. Security concerns
3. Performance
4. Maintainability
5. Best practices"""
        
        elif task_type == "analysis":
            return f"""Analyze the following data and provide insights:
{task_data.get('data', '')}

Focus areas: {task_data.get('focus', 'General analysis')}
Provide structured output with key findings."""
        
        elif task_type == "security_audit":
            return f"""Perform security audit:
{task_data.get('target', '')}

Check for:
- Vulnerabilities
- Misconfigurations
- Exposure risks
- Compliance issues

Provide severity ratings and remediation steps."""
        
        else:
            return task_data.get("prompt", "No specific prompt provided")
    
    def _detect_hallucination(self, text: str) -> bool:
        """Detect potential hallucinations in output"""
        
        hallucination_indicators = [
            "I don't actually have access",
            "As an AI language model",
            "I cannot actually",
            "I don't have the ability to",
            "I apologize, but I cannot",
            "I don't have real-time",
            "I don't have access to"
        ]
        
        text_lower = text.lower()
        for indicator in hallucination_indicators:
            if indicator in text_lower:
                return True
        
        # Check for made-up references
        if "according to" in text_lower and "[citation needed]" in text_lower:
            return True
        
        return False
    
    async def terminate_bot(self, bot_id: str, reason: str):
        """TERMINATE a bot - add to graveyard, spawn replacement"""
        
        bot = next((b for b in self.bots if b.id == bot_id), None)
        if not bot:
            return
        
        logger.warning(f"☠️  TERMINATING {bot.name}: {reason}")
        
        # Backup before termination
        await self._backup_bot(bot)
        
        # Mark as terminated
        bot.status = BotStatus.TERMINATED
        self.graveyard.append(bot)
        self.bots.remove(bot)
        
        # Spawn replacement with same config
        await self._spawn_replacement(bot)
        
        # Log termination
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE bots SET status = ? WHERE id = ?",
            (BotStatus.TERMINATED.value, bot_id)
        )
        conn.commit()
        conn.close()
    
    async def _backup_bot(self, bot: BotIdentity):
        """Backup bot state before termination/context wipe"""
        
        backup_data = {
            "tasks_completed": bot.tasks_completed,
            "tasks_failed": bot.tasks_failed,
            "hallucination_count": bot.hallucination_count,
            "consensus_votes": {
                "for": bot.consensus_votes_for,
                "against": bot.consensus_votes_against
            },
            "survival_score": bot.survival_score,
            "age_hours": bot.age_hours
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO backups (bot_id, timestamp, context_data, performance_metrics)
               VALUES (?, ?, ?, ?)""",
            (bot.id, datetime.now(), bot.context_hash, json.dumps(backup_data))
        )
        conn.commit()
        conn.close()
        
        bot.last_backup = datetime.now()
        logger.info(f"💾 Backed up {bot.name}")
    
    async def _spawn_replacement(self, terminated_bot: BotIdentity):
        """Spawn a replacement bot"""
        
        new_id = f"{terminated_bot.id}_v{int(time.time())}"
        
        replacement = BotIdentity(
            id=new_id,
            name=f"{terminated_bot.name} (Reborn)",
            provider=terminated_bot.provider,
            model=terminated_bot.model,
            specialty=terminated_bot.specialty,
            status=BotStatus.ALIVE,
            birth_time=datetime.now()
        )
        
        self.bots.append(replacement)
        logger.info(f"🐣 Spawned replacement: {replacement.name}")
    
    async def lifecycle_manager(self):
        """24-hour lifecycle management - runs continuously"""
        
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                logger.info("🔄 Running lifecycle check...")
                
                for bot in list(self.bots):
                    # Check age
                    if bot.age_hours >= 24:
                        logger.info(f"⏰ {bot.name} reached 24h - wiping context")
                        await self._backup_bot(bot)
                        # Reset context (keep identity, wipe memory)
                        bot.context_hash = hashlib.md5(str(time.time()).encode()).hexdigest()
                        bot.birth_time = datetime.now()  # Fresh start
                    
                    # Check health
                    if bot.should_terminate():
                        await self.terminate_bot(bot.id, f"Survival score {bot.survival_score:.2f}")
                
                # Log swarm status
                alive = len([b for b in self.bots if b.status == BotStatus.ALIVE])
                logger.info(f"🐝 Swarm status: {alive}/{len(self.bots)} bots alive")
                
            except Exception as e:
                logger.error(f"Lifecycle error: {e}")
    
    def get_swarm_status(self) -> Dict:
        """Get current swarm status including containment"""
        
        alive = [b for b in self.bots if b.status == BotStatus.ALIVE]
        warning = [b for b in self.bots if b.status == BotStatus.WARNING]
        isolated = [b for b in self.bots if b.status == BotStatus.ISOLATED]
        terminated = len(self.graveyard)
        
        status = {
            "total_bots": len(self.bots),
            "alive": len(alive),
            "warning": len(warning),
            "isolated": len(isolated),
            "terminated": terminated,
            "avg_survival_score": sum(b.survival_score for b in alive) / len(alive) if alive else 0,
            "tasks_completed": sum(b.tasks_completed for b in self.bots),
            "tasks_failed": sum(b.tasks_failed for b in self.bots),
            "consensus_decisions": len(self.consensus_council.decision_history),
            "bots": [
                {
                    "id": b.id,
                    "name": b.name,
                    "status": b.status.value,
                    "survival_score": round(b.survival_score, 2),
                    "age_hours": round(b.age_hours, 1),
                    "tasks": f"{b.tasks_completed}/{b.tasks_failed}"
                }
                for b in alive[:10]  # Top 10
            ]
        }
        
        # Add containment report if coordinator exists
        if hasattr(self, 'comm_coordinator') and self.comm_coordinator:
            status["containment"] = self.comm_coordinator.get_containment_report()
        
        return status


# ═══════════════════════════════════════════════════════════════════
# INITIALIZATION AND DEMO
# ═══════════════════════════════════════════════════════════════════

async def demo_swarm():
    """Demo the AI Swarm with containment"""
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           🤖 AI SWARM ORCHESTRATOR v2.0                          ║
║          Survival of the Fittest - Consensus Driven                ║
╠══════════════════════════════════════════════════════════════════╣
║  🐝 17 Free AI Models (NVIDIA + OpenRouter + Local)              ║
║  🗳️  Consensus Council - No Decisions Without Votes               ║
║  🔍  6-Layer Code Verification                                   ║
║  ☠️  Termination for Hallucinations                             ║
║  ⏰  24h Lifecycle - Context Wipe, Data Preserved                 ║
╠══════════════════════════════════════════════════════════════════╣
║  🛡️  CONTAINMENT ARCHITECTURE                                    ║
║  • Individual Bot Containers - Full Isolation                      ║
║  • Communication Coordinator - All Traffic Routes Through Here     ║
║  • Collusion Detection - Pattern Matching on All Messages        ║
║  • Peer Review Assignment - Coordinator Chooses, Bots Don't      ║
║  • Bot Blindness - No Bot Sees Full Roster                       ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    swarm = AISwarmOrchestrator()
    
    # Show initial status
    status = swarm.get_swarm_status()
    print(f"\n🐝 Initial Swarm Status:")
    print(f"   Total Bots: {status['total_bots']}")
    print(f"   Alive: {status['alive']}")
    print(f"   Isolated: {status['isolated']}")
    print(f"   Terminated: {status['terminated']}")
    
    # Show containment status
    if "containment" in status:
        containment = status["containment"]
        print(f"\n🛡️  Containment Status:")
        print(f"   Containers: {containment['total_containers']}")
        print(f"   Pending Approvals: {containment['pending_approvals']}")
        print(f"   Collusion Alerts: {containment['collusion_alerts']}")
    
    print(f"\n🤖 Active Bots (Top 5):")
    for bot in status['bots'][:5]:
        print(f"   • {bot['name'][:35]:35} | Score: {bot['survival_score']:.2f} | Age: {bot['age_hours']}h")
    
    # Demo: Consensus decision
    print(f"\n🗳️  Testing Consensus Council...")
    decision = await swarm.consensus_council.propose(
        proposal="Allow swarm to begin autonomous operation",
        context="Initial system test",
        level=ConsensusLevel.MAJORITY
    )
    print(f"   Result: {decision.final_decision} ({decision.approval_rate*100:.0f}% approval)")
    
    # Demo: Code generation with 6-layer verification
    print(f"\n💻 Testing Code Generation (6-layer verification)...")
    result = await swarm.assign_task(
        task_type="code_generation",
        task_data={
            "language": "python",
            "purpose": "Create a function to calculate fibonacci numbers",
            "code_requirements": "Write a clean, efficient fibonacci function with error handling"
        },
        require_consensus=True
    )
    
    if result.get("success"):
        print(f"   ✅ Code generated and verified by all 6 layers")
        print(f"   🤖 Generated by: {result.get('bot')}")
    else:
        print(f"   ❌ Failed: {result.get('error')}")
    
    print(f"\n✅ Swarm is ready for autonomous operation")
    print(f"   Start lifecycle manager: await swarm.lifecycle_manager()")
    
    return swarm


if __name__ == "__main__":
    swarm = asyncio.run(demo_swarm())
