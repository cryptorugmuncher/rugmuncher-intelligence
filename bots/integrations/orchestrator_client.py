"""
🔗 Orchestrator API Client
============================
Telegram bot integration with the unified bot orchestrator.
Allows the Telegram bot to dispatch tasks to the 8-bot task force.
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8081")


class OrchestratorClient:
    """Client for the RMI Bot Orchestrator API."""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or ORCHESTRATOR_URL

    async def health(self) -> Dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as resp:
                return await resp.json()

    async def dispatch_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        target_role: str = None,
        target_bot: str = None,
        priority: str = "normal",
        source: str = "telegram",
    ) -> Dict:
        """Dispatch a task to the orchestrator."""
        body = {
            "task_type": task_type,
            "payload": payload,
            "priority": priority,
            "source": source,
        }
        if target_role:
            body["target_role"] = target_role
        if target_bot:
            body["target_bot"] = target_bot

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/orchestrator/task",
                json=body,
            ) as resp:
                return await resp.json()

    async def get_bots(self) -> Dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/orchestrator/bots") as resp:
                return await resp.json()

    async def broadcast_alert(
        self,
        severity: str,
        title: str,
        description: str,
        contract_address: str = None,
        chain: str = None,
        channels: list = None,
    ) -> Dict:
        body = {
            "severity": severity,
            "title": title,
            "description": description,
            "channels": channels or ["telegram"],
        }
        if contract_address:
            body["contract_address"] = contract_address
        if chain:
            body["chain"] = chain

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/orchestrator/alert",
                json=body,
            ) as resp:
                return await resp.json()


# Singleton
_orchestrator_client: Optional[OrchestratorClient] = None


def get_orchestrator_client() -> OrchestratorClient:
    global _orchestrator_client
    if _orchestrator_client is None:
        _orchestrator_client = OrchestratorClient()
    return _orchestrator_client
