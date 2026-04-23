"""
Multi-Chain Support for MunchMaps V2
Supports: Ethereum, Solana, Tron, BSC, Polygon
"""
from .ethereum_adapter import EthereumAdapter
from .solana_adapter import SolanaAdapter
from .tron_adapter import TronAdapter
from .bsc_adapter import BSCAdapter
from .polygon_adapter import PolygonAdapter

CHAIN_ADAPTERS = {
    'ethereum': EthereumAdapter,
    'solana': SolanaAdapter,
    'tron': TronAdapter,
    'bsc': BSCAdapter,
    'polygon': PolygonAdapter
}

SUPPORTED_CHAINS = list(CHAIN_ADAPTERS.keys())

__all__ = [
    'EthereumAdapter', 'SolanaAdapter', 'TronAdapter', 
    'BSCAdapter', 'PolygonAdapter',
    'CHAIN_ADAPTERS', 'SUPPORTED_CHAINS'
]
