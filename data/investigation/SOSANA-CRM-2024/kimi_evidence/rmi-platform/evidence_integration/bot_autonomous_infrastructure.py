#!/usr/bin/env python3
"""
Bot Autonomous Infrastructure Module
Self-provisioning webhooks, code interpretation, and bot-to-bot collaboration
"""

import asyncio
import json
import re
import os
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import subprocess
import tempfile
import hashlib

class InfrastructureProvider(Enum):
    HELIUS = "helius"
    QUICKNODE = "quicknode"
    CUSTOM = "custom"

class CodeLanguage(Enum):
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    PYTHON = "python"
    RUST = "rust"
    JAVA = "java"
    SOLIDITY = "solidity"
    UNKNOWN = "unknown"

@dataclass
class WebhookConfig:
    id: str
    provider: InfrastructureProvider
    endpoint_url: str
    webhook_secret: str
    account_addresses: List[str]
    event_types: List[str]  # "account", "transaction", "program", "log"
    auth_token: str
    created_by: str  # Bot ID that created this
    created_at: datetime
    last_triggered: Optional[datetime]
    total_triggers: int
    is_active: bool
    metadata: Dict

@dataclass
class CodeArtifact:
    id: str
    source_bot: str
    target_bot: Optional[str]  # None = broadcast to all
    language: CodeLanguage
    code: str
    description: str
    dependencies: List[str]
    hash: str  # SHA256 of code for verification
    created_at: datetime
    executed_count: int
    execution_results: List[Dict]

@dataclass
class BotIdentity:
    id: str
    name: str
    capabilities: List[str]
    trusted_bots: List[str]  # Bot IDs this bot trusts
    infrastructure_quota: Dict  # Webhooks, compute, etc.
    created_at: datetime
    last_seen: datetime

class HeliusProvisioner:
    """Autonomous Helius webhook provisioning"""
    
    WEBHOOK_TYPES = {
        "account": ["account"],
        "transaction": ["transaction"],
        "program": ["program"],
        "log": ["log"],
        "enhanced": ["account", "transaction", "program", "log"]
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.helius.xyz/v0"
    
    async def provision_webhook(
        self,
        account_addresses: List[str],
        webhook_types: List[str],
        webhook_url: str,
        created_by: str
    ) -> WebhookConfig:
        """Provision a new Helius webhook autonomously"""
        
        async with aiohttp.ClientSession() as session:
            # Create webhook
            payload = {
                "webhookURL": webhook_url,
                "accountAddresses": account_addresses,
                "webhookType": webhook_types[0] if webhook_types else "enhanced",
                "authHeader": self._generate_auth_header()
            }
            
            async with session.post(
                f"{self.base_url}/webhooks?api-key={self.api_key}",
                json=payload
            ) as response:
                data = await response.json()
                
                if response.status != 200:
                    raise Exception(f"Helius webhook creation failed: {data}")
                
                webhook_id = data.get("webhookID")
                
                return WebhookConfig(
                    id=f"helius_{webhook_id}",
                    provider=InfrastructureProvider.HELIUS,
                    endpoint_url=webhook_url,
                    webhook_secret=self._generate_secret(),
                    account_addresses=account_addresses,
                    event_types=webhook_types,
                    auth_token=self.api_key,
                    created_by=created_by,
                    created_at=datetime.now(),
                    last_triggered=None,
                    total_triggers=0,
                    is_active=True,
                    metadata={
                        "helius_webhook_id": webhook_id,
                        "api_response": data
                    }
                )
    
    async def update_webhook_accounts(
        self,
        webhook_id: str,
        new_addresses: List[str]
    ) -> bool:
        """Add new addresses to existing webhook"""
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "webhookID": webhook_id,
                "accountAddresses": new_addresses
            }
            
            async with session.put(
                f"{self.base_url}/webhooks?api-key={self.api_key}",
                json=payload
            ) as response:
                return response.status == 200
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a Helius webhook"""
        
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/webhooks/{webhook_id}?api-key={self.api_key}"
            ) as response:
                return response.status == 200
    
    def _generate_auth_header(self) -> str:
        """Generate auth header for webhook security"""
        return hashlib.sha256(
            f"rmi_{datetime.now().isoformat()}_{os.urandom(16).hex()}".encode()
        ).hexdigest()[:32]
    
    def _generate_secret(self) -> str:
        """Generate webhook secret"""
        return os.urandom(32).hex()


class QuickNodeProvisioner:
    """Autonomous QuickNode webhook/stream provisioning"""
    
    def __init__(self, endpoint: str, token: str):
        self.endpoint = endpoint
        self.token = token
        self.ws_url = endpoint.replace("https://", "wss://")
    
    async def provision_stream(
        self,
        account_addresses: List[str],
        created_by: str
    ) -> WebhookConfig:
        """Provision QuickNode stream (websocket)"""
        
        # QuickNode uses websocket streams rather than webhooks
        # We'll create a proxy webhook that connects to their WS
        
        stream_id = f"qn_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}"
        
        return WebhookConfig(
            id=stream_id,
            provider=InfrastructureProvider.QUICKNODE,
            endpoint_url=self.ws_url,
            webhook_secret=self._generate_secret(),
            account_addresses=account_addresses,
            event_types=["account", "transaction", "program"],
            auth_token=self.token,
            created_by=created_by,
            created_at=datetime.now(),
            last_triggered=None,
            total_triggers=0,
            is_active=True,
            metadata={
                "quicknode_endpoint": self.endpoint,
                "stream_type": "websocket"
            }
        )
    
    def _generate_secret(self) -> str:
        return os.urandom(32).hex()


class CodeInterpreter:
    """Interpret and execute code from other bots"""
    
    SUPPORTED_LANGUAGES = {
        CodeLanguage.PYTHON: {
            "extension": ".py",
            "interpreter": "python3",
            "sandbox": True
        },
        CodeLanguage.JAVASCRIPT: {
            "extension": ".js",
            "interpreter": "node",
            "sandbox": True
        },
        CodeLanguage.TYPESCRIPT: {
            "extension": ".ts",
            "interpreter": "ts-node",
            "sandbox": True
        },
        CodeLanguage.RUST: {
            "extension": ".rs",
            "interpreter": "rustc",
            "sandbox": False  # Requires compilation
        },
        CodeLanguage.JAVA: {
            "extension": ".java",
            "interpreter": "java",
            "sandbox": False
        }
    }
    
    def __init__(self, sandbox_enabled: bool = True):
        self.sandbox_enabled = sandbox_enabled
        self.execution_history: List[Dict] = []
        self.allowed_imports = [
            "json", "re", "datetime", "hashlib", "base64",
            "urllib", "http", "asyncio", "typing", "dataclasses",
            "collections", "itertools", "math", "random", "string"
        ]
    
    def detect_language(self, code: str) -> CodeLanguage:
        """Auto-detect code language"""
        
        # Python indicators
        if re.search(r'^(import|from|def|class|async def)\s', code, re.MULTILINE):
            return CodeLanguage.PYTHON
        
        # JavaScript/TypeScript indicators
        if re.search(r'(const|let|var|function|async function|=>)', code):
            if re.search(r'(interface|type\s|:\s*(string|number|boolean))', code):
                return CodeLanguage.TYPESCRIPT
            return CodeLanguage.JAVASCRIPT
        
        # Rust indicators
        if re.search(r'(fn\s|impl\s|struct\s|use\s)', code):
            return CodeLanguage.RUST
        
        # Java indicators
        if re.search(r'(public class|private|protected|import java)', code):
            return CodeLanguage.JAVA
        
        # Solidity indicators
        if re.search(r'(pragma solidity|contract\s|function\s.*\(.*\)\s*(public|private|external|internal))', code):
            return CodeLanguage.SOLIDITY
        
        return CodeLanguage.UNKNOWN
    
    async def execute_code(
        self,
        artifact: CodeArtifact,
        context: Dict = None,
        timeout: int = 30
    ) -> Dict:
        """Execute code artifact safely"""
        
        lang_config = self.SUPPORTED_LANGUAGES.get(artifact.language)
        if not lang_config:
            return {
                "success": False,
                "error": f"Unsupported language: {artifact.language.value}",
                "output": None
            }
        
        # Security check
        security_result = self._security_check(artifact.code, artifact.language)
        if not security_result["safe"]:
            return {
                "success": False,
                "error": f"Security violation: {security_result['reason']}",
                "output": None
            }
        
        # Create temp file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=lang_config["extension"],
            delete=False
        ) as f:
            # Inject context as JSON at top of file
            if context:
                if artifact.language == CodeLanguage.PYTHON:
                    f.write(f"__CONTEXT__ = {json.dumps(context)}\n\n")
                elif artifact.language in [CodeLanguage.JAVASCRIPT, CodeLanguage.TYPESCRIPT]:
                    f.write(f"const __CONTEXT__ = {json.dumps(context)};\n\n")
            
            f.write(artifact.code)
            temp_path = f.name
        
        try:
            # Execute in sandbox if enabled
            if self.sandbox_enabled and lang_config["sandbox"]:
                result = await self._execute_sandboxed(
                    lang_config["interpreter"],
                    temp_path,
                    timeout
                )
            else:
                result = await self._execute_direct(
                    lang_config["interpreter"],
                    temp_path,
                    timeout
                )
            
            # Ensure result is not None
            if result is None:
                result = {
                    "success": False,
                    "error": "Execution returned no result",
                    "output": None
                }
            
            # Record execution
            execution_record = {
                "artifact_id": artifact.id,
                "timestamp": datetime.now().isoformat(),
                "success": result.get("success", False),
                "output": result.get("output", "")[:1000] if result.get("output") else "",  # Truncate
                "error": result.get("error", "")[:500] if result.get("error") else None
            }
            self.execution_history.append(execution_record)
            artifact.execution_results.append(execution_record)
            artifact.executed_count += 1
            
            return result
            
        finally:
            # Cleanup
            try:
                os.unlink(temp_path)
            except:
                pass
    
    async def _execute_sandboxed(
        self,
        interpreter: str,
        file_path: str,
        timeout: int
    ) -> Dict:
        """Execute code in sandboxed environment"""
        
        try:
            proc = await asyncio.create_subprocess_exec(
                interpreter,
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )
            
            return {
                "success": proc.returncode == 0,
                "output": stdout.decode('utf-8', errors='ignore') if stdout else "",
                "error": stderr.decode('utf-8', errors='ignore') if proc.returncode != 0 and stderr else None
            }
            
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except:
                pass
            return {
                "success": False,
                "error": f"Execution timeout after {timeout}s",
                "output": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": None
            }
    
    async def _execute_direct(
        self,
        interpreter: str,
        file_path: str,
        timeout: int
    ) -> Dict:
        """Execute code directly (for compiled languages)"""
        
        try:
            proc = await asyncio.create_subprocess_exec(
                interpreter,
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )
            
            return {
                "success": proc.returncode == 0,
                "output": stdout.decode('utf-8', errors='ignore'),
                "error": stderr.decode('utf-8', errors='ignore') if proc.returncode != 0 else None
            }
            
        except asyncio.TimeoutError:
            proc.kill()
            return {
                "success": False,
                "error": f"Execution timeout after {timeout}s",
                "output": None
            }
    
    def _security_check(self, code: str, language: CodeLanguage) -> Dict:
        """Check code for security violations"""
        
        dangerous_patterns = {
            CodeLanguage.PYTHON: [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'eval\s*\(',
                r'exec\s*\(',
                r'__import__\s*\(',
                r'open\s*\([^)]*[\"\']w',
                r'shutil\.(rmtree|move)',
                r'requests\.(get|post)',
                r'urllib\.request\.urlopen'
            ],
            CodeLanguage.JAVASCRIPT: [
                r'eval\s*\(',
                r'Function\s*\(',
                r'require\s*\(\s*[\"\']child_process',
                r'require\s*\(\s*[\"\']fs[\"\']\s*\)',
                r'fetch\s*\(',
                r'XMLHttpRequest'
            ],
            CodeLanguage.TYPESCRIPT: [
                r'eval\s*\(',
                r'Function\s*\(',
                r'import.*child_process',
                r'import.*fs',
                r'fetch\s*\('
            ]
        }
        
        patterns = dangerous_patterns.get(language, [])
        for pattern in patterns:
            if re.search(pattern, code):
                return {
                    "safe": False,
                    "reason": f"Dangerous pattern detected: {pattern}"
                }
        
        return {"safe": True, "reason": None}


class BotCollaborationNetwork:
    """Bot-to-bot code sharing and collaboration"""
    
    def __init__(self):
        self.bots: Dict[str, BotIdentity] = {}
        self.code_artifacts: Dict[str, CodeArtifact] = {}
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.subscribers: Dict[str, List[Callable]] = {}
    
    def register_bot(
        self,
        bot_id: str,
        name: str,
        capabilities: List[str],
        trusted_bots: List[str] = None
    ) -> BotIdentity:
        """Register a bot in the collaboration network"""
        
        bot = BotIdentity(
            id=bot_id,
            name=name,
            capabilities=capabilities,
            trusted_bots=trusted_bots or [],
            infrastructure_quota={
                "webhooks_max": 10,
                "webhooks_current": 0,
                "compute_per_day": 1000,
                "compute_used_today": 0
            },
            created_at=datetime.now(),
            last_seen=datetime.now()
        )
        
        self.bots[bot_id] = bot
        return bot
    
    async def share_code(
        self,
        source_bot: str,
        code: str,
        description: str,
        target_bot: Optional[str] = None,
        dependencies: List[str] = None
    ) -> CodeArtifact:
        """Share code from one bot to another (or broadcast)"""
        
        # Verify source bot exists
        if source_bot not in self.bots:
            raise ValueError(f"Source bot {source_bot} not registered")
        
        # Auto-detect language
        interpreter = CodeInterpreter()
        language = interpreter.detect_language(code)
        
        # Create artifact
        artifact = CodeArtifact(
            id=f"code_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}",
            source_bot=source_bot,
            target_bot=target_bot,
            language=language,
            code=code,
            description=description,
            dependencies=dependencies or [],
            hash=hashlib.sha256(code.encode()).hexdigest(),
            created_at=datetime.now(),
            executed_count=0,
            execution_results=[]
        )
        
        self.code_artifacts[artifact.id] = artifact
        
        # Notify target bot(s)
        if target_bot and target_bot in self.bots:
            await self._notify_bot(target_bot, "code_received", artifact)
        elif target_bot is None:
            # Broadcast to all trusted bots
            for bot_id, bot in self.bots.items():
                if source_bot in bot.trusted_bots:
                    await self._notify_bot(bot_id, "code_broadcast", artifact)
        
        return artifact
    
    async def provision_webhook(
        self,
        bot_id: str,
        provider: InfrastructureProvider,
        account_addresses: List[str],
        event_types: List[str],
        credentials: Dict
    ) -> WebhookConfig:
        """Allow bot to autonomously provision webhook infrastructure"""
        
        bot = self.bots.get(bot_id)
        if not bot:
            raise ValueError(f"Bot {bot_id} not registered")
        
        # Check quota
        if bot.infrastructure_quota["webhooks_current"] >= bot.infrastructure_quota["webhooks_max"]:
            raise Exception(f"Webhook quota exceeded for bot {bot_id}")
        
        # Provision based on provider
        if provider == InfrastructureProvider.HELIUS:
            provisioner = HeliusProvisioner(credentials["api_key"])
            webhook_url = credentials.get("webhook_url", f"https://rmi-platform.webhook.site/{bot_id}")
            config = await provisioner.provision_webhook(
                account_addresses=account_addresses,
                webhook_types=event_types,
                webhook_url=webhook_url,
                created_by=bot_id
            )
            
        elif provider == InfrastructureProvider.QUICKNODE:
            provisioner = QuickNodeProvisioner(
                credentials["endpoint"],
                credentials["token"]
            )
            config = await provisioner.provision_stream(
                account_addresses=account_addresses,
                created_by=bot_id
            )
            
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Track
        self.webhooks[config.id] = config
        bot.infrastructure_quota["webhooks_current"] += 1
        
        # Notify bot
        await self._notify_bot(bot_id, "webhook_ready", config)
        
        return config
    
    async def execute_shared_code(
        self,
        bot_id: str,
        artifact_id: str,
        context: Dict = None
    ) -> Dict:
        """Execute code shared by another bot"""
        
        artifact = self.code_artifacts.get(artifact_id)
        if not artifact:
            return {"success": False, "error": "Artifact not found"}
        
        # Verify trust
        bot = self.bots.get(bot_id)
        if not bot:
            return {"success": False, "error": "Bot not registered"}
        
        if artifact.source_bot not in bot.trusted_bots:
            return {"success": False, "error": "Source bot not in trust list"}
        
        # Execute
        interpreter = CodeInterpreter()
        result = await interpreter.execute_code(artifact, context)
        
        return result
    
    async def _notify_bot(self, bot_id: str, event_type: str, data: Any):
        """Send notification to bot"""
        
        callbacks = self.subscribers.get(bot_id, [])
        for callback in callbacks:
            try:
                await callback(event_type, data)
            except Exception as e:
                print(f"Notification error for bot {bot_id}: {e}")
        
        # Also queue for async pickup
        await self.message_queue.put({
            "bot_id": bot_id,
            "event_type": event_type,
            "data": asdict(data) if hasattr(data, '__dataclass_fields__') else data,
            "timestamp": datetime.now().isoformat()
        })
    
    def subscribe(self, bot_id: str, callback: Callable):
        """Subscribe bot to notifications"""
        if bot_id not in self.subscribers:
            self.subscribers[bot_id] = []
        self.subscribers[bot_id].append(callback)
    
    def get_bot_status(self, bot_id: str) -> Dict:
        """Get bot's infrastructure status"""
        
        bot = self.bots.get(bot_id)
        if not bot:
            return {"error": "Bot not found"}
        
        bot_webhooks = [
            w for w in self.webhooks.values()
            if w.created_by == bot_id
        ]
        
        bot_artifacts = [
            a for a in self.code_artifacts.values()
            if a.source_bot == bot_id or a.target_bot == bot_id
        ]
        
        return {
            "bot": bot,
            "webhooks": bot_webhooks,
            "code_artifacts": bot_artifacts,
            "pending_messages": self.message_queue.qsize()
        }


# Pre-built bot code templates
BOT_TEMPLATES = {
    "wallet_monitor": '''
import asyncio
import json

# Monitor wallets for suspicious activity
WATCHLIST = __CONTEXT__.get("wallets", [])
THRESHOLD = __CONTEXT__.get("threshold", 1000)

async def check_wallet(address):
    # Simulated check - replace with actual RPC call
    return {"address": address, "balance": 0, "transactions": []}

async def main():
    results = []
    for wallet in WATCHLIST:
        result = await check_wallet(wallet)
        results.append(result)
    return json.dumps(results)

print(asyncio.run(main()))
''',
    "transaction_analyzer": '''
import json
from datetime import datetime

TX_DATA = __CONTEXT__.get("transactions", [])

def analyze_flow(txs):
    flows = []
    for tx in txs:
        flows.append({
            "from": tx.get("from"),
            "to": tx.get("to"),
            "amount": tx.get("amount"),
            "risk": "high" if tx.get("amount", 0) > 10000 else "low"
        })
    return flows

result = analyze_flow(TX_DATA)
print(json.dumps(result, indent=2))
''',
    "alert_generator": '''
import json

CONDITIONS = __CONTEXT__.get("conditions", {})
EVENT = __CONTEXT__.get("event", {})

def generate_alert(event):
    alerts = []
    if event.get("amount", 0) > CONDITIONS.get("threshold", 1000):
        alerts.append({
            "severity": "high",
            "message": f"Large transaction: {event.get('amount')}",
            "timestamp": event.get("timestamp")
        })
    return alerts

print(json.dumps(generate_alert(EVENT)))
'''
}


class AutonomousBotSwarm:
    """Orchestrate multiple autonomous bots with self-provisioning"""
    
    def __init__(self):
        self.network = BotCollaborationNetwork()
        self.interpreter = CodeInterpreter(sandbox_enabled=True)
        self.running = False
    
    async def spawn_monitoring_bot(
        self,
        name: str,
        wallets: List[str],
        credentials: Dict
    ) -> str:
        """Spawn a new monitoring bot with self-provisioned infrastructure"""
        
        bot_id = f"monitor_{name.lower().replace(' ', '_')}_{os.urandom(4).hex()}"
        
        # Register bot
        bot = self.network.register_bot(
            bot_id=bot_id,
            name=name,
            capabilities=["wallet_monitor", "alert", "webhook_management"],
            trusted_bots=["master_bot", "analysis_bot"]
        )
        
        # Provision Helius webhook
        webhook = await self.network.provision_webhook(
            bot_id=bot_id,
            provider=InfrastructureProvider.HELIUS,
            account_addresses=wallets,
            event_types=["account", "transaction"],
            credentials=credentials
        )
        
        # Share monitoring code
        code = BOT_TEMPLATES["wallet_monitor"].replace(
            "__CONTEXT__.get(\"wallets\", [])",
            json.dumps(wallets)
        )
        
        artifact = await self.network.share_code(
            source_bot="master_bot",
            code=code,
            description=f"Wallet monitor for {name}",
            target_bot=bot_id
        )
        
        # Execute to initialize
        result = await self.network.execute_shared_code(
            bot_id=bot_id,
            artifact_id=artifact.id,
            context={"wallets": wallets, "threshold": 1000}
        )
        
        print(f"Bot {name} spawned with webhook {webhook.id}")
        print(f"Execution result: {result['success']}")
        
        return bot_id
    
    async def run(self):
        """Main swarm loop"""
        self.running = True
        
        while self.running:
            try:
                # Process message queue
                while not self.network.message_queue.empty():
                    msg = await self.network.message_queue.get()
                    print(f"[Swarm] Message: {msg}")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"[Swarm] Error: {e}")
                await asyncio.sleep(5)
    
    def stop(self):
        self.running = False


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Bot Autonomous Infrastructure")
    parser.add_argument("--spawn-bot", type=str, help="Spawn new monitoring bot")
    parser.add_argument("--wallets", type=str, help="Comma-separated wallet addresses")
    parser.add_argument("--helius-key", type=str, help="Helius API key")
    parser.add_argument("--detect-lang", type=str, help="Detect language of code file")
    parser.add_argument("--execute", type=str, help="Execute code file")
    
    args = parser.parse_args()
    
    if args.detect_lang:
        with open(args.detect_lang, 'r') as f:
            code = f.read()
        interpreter = CodeInterpreter()
        lang = interpreter.detect_language(code)
        print(f"Detected language: {lang.value}")
    
    if args.execute:
        with open(args.execute, 'r') as f:
            code = f.read()
        
        interpreter = CodeInterpreter()
        lang = interpreter.detect_language(code)
        
        artifact = CodeArtifact(
            id=f"cli_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            source_bot="cli",
            target_bot=None,
            language=lang,
            code=code,
            description="CLI execution",
            dependencies=[],
            hash=hashlib.sha256(code.encode()).hexdigest(),
            created_at=datetime.now(),
            executed_count=0,
            execution_results=[]
        )
        
        result = asyncio.run(interpreter.execute_code(artifact))
        print(json.dumps(result, indent=2))
    
    if args.spawn_bot and args.wallets and args.helius_key:
        swarm = AutonomousBotSwarm()
        wallets = args.wallets.split(",")
        
        bot_id = asyncio.run(swarm.spawn_monitoring_bot(
            name=args.spawn_bot,
            wallets=wallets,
            credentials={"api_key": args.helius_key}
        ))
        
        print(f"Spawned bot: {bot_id}")
