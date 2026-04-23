"""
Omega Forensic V5 - Bots Module
================================
Bot implementations for the investigation platform.

Modules:
- investigator_bot: The Investigator - self-healing forensic bot
"""

from .investigator_bot import (
    InvestigatorBot,
    InvestigationSession,
    INVESTIGATOR_PERSONALITY,
    get_investigator,
    investigate,
    find_kyc,
    ask_investigator
)

__all__ = [
    "InvestigatorBot",
    "InvestigationSession",
    "INVESTIGATOR_PERSONALITY",
    "get_investigator",
    "investigate",
    "find_kyc",
    "ask_investigator",
]
