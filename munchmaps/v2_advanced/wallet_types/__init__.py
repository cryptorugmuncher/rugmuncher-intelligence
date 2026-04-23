"""
Suspicious Wallet Type Detection
Identify bot farms, pig butcherers, mixers, and other malicious actors
"""
from .wallet_classifier import WalletClassifier, SUSPICIOUS_WALLET_TYPES

__all__ = ['WalletClassifier', 'SUSPICIOUS_WALLET_TYPES']
