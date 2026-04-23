"""
Omega Forensic V5 - Utils Module
=================================
Utility functions for the investigation platform.

Modules:
- document_ingestion: Universal file ingestion
"""

from .document_ingestion import (
    DocumentIngestionManager,
    ingest_file,
    ingest_directory
)

__all__ = [
    "DocumentIngestionManager",
    "ingest_file",
    "ingest_directory",
]
