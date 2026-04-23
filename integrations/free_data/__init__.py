"""
Free Data Access Manager
Rotates through free APIs to maximize zero-cost data access
"""

from .search_manager import FreeSearchManager, get_search_manager
from .config import FREE_APIS

__all__ = ['FreeSearchManager', 'get_search_manager', 'FREE_APIS']
