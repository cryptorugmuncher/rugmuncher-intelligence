"""
Omega Forensic V5 - Core Module
================================
Core functionality for the investigation platform.

Modules:
- intelligent_switcher: Smart AI model selection
- data_processor: Universal document ingestion
"""

from .intelligent_switcher import (
    IntelligentSwitcher,
    TaskConfig,
    quick_reply,
    deep_analysis,
    generate_code
)
from .data_processor import (
    UniversalDocumentProcessor,
    ProcessedDocument,
    process_document,
    batch_process_directory
)

__all__ = [
    # Intelligent Switcher
    "IntelligentSwitcher",
    "TaskConfig",
    "quick_reply",
    "deep_analysis",
    "generate_code",
    # Data Processor
    "UniversalDocumentProcessor",
    "ProcessedDocument",
    "process_document",
    "batch_process_directory",
]
