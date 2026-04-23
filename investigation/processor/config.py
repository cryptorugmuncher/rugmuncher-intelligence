"""
Investigation Processor Configuration
"""

# File type mappings
EVIDENCE_CATEGORIES = {
    'telegram_chats': {
        'extensions': ['.html'],
        'patterns': ['messages', 'chat', 'telegram'],
        'priority': 'critical',
        'processor': 'parse_telegram_html'
    },
    'wallet_data': {
        'extensions': ['.csv', '.txt'],
        'patterns': ['holders', 'transfer', 'export', 'wallet'],
        'priority': 'critical',
        'processor': 'parse_wallet_data'
    },
    'visual_evidence': {
        'extensions': ['.jpg', '.jpeg', '.png'],
        'patterns': ['screenshot', 'photo'],
        'priority': 'high',
        'processor': 'ocr_and_analyze'
    },
    'forensic_reports': {
        'extensions': ['.txt', '.md'],
        'patterns': ['report', 'analysis', 'forensic', 'sosana', 'crm'],
        'priority': 'critical',
        'processor': 'parse_forensic_report'
    },
    'architecture_docs': {
        'extensions': ['.txt', '.md', '.docx'],
        'patterns': ['build', 'app', 'architecture', 'system', 'api'],
        'priority': 'medium',
        'processor': 'parse_architecture'
    },
    'compressed_archives': {
        'extensions': ['.zip'],
        'patterns': [],
        'priority': 'high',
        'processor': 'extract_and_process'
    }
}

# SOSANA-specific keywords for auto-tagging
SOSANA_KEYWORDS = [
    'sosana', 'sosanna', 'shift ai', 'shift.ai', 'crm token',
    'david track', 'tracy silver', 'mark hamlin', 'peter ohanyan',
    'f1espc1', '7acsekys', 'dlhnb1yt', '8evza7b',
    'wallet', 'scam', 'rug', 'ponzi', 'ml'
]

# Wallet address patterns
WALLET_PATTERNS = {
    'solana': r'[A-HJ-NP-Za-km-z1-9]{32,44}',
    'ethereum': r'0x[a-fA-F0-9]{40}',
    'bitcoin': r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59}'
}
