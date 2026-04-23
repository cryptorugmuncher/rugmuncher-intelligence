"""
================================================================================
EVIDENCE FORTRESS CONFIGURATION
================================================================================
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Database connection settings."""
    host: str = "localhost"
    port: int = 5432
    name: str = "evidence_fortress"
    user: str = "evidence_user"
    password: str = ""
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class LLMConfig:
    """LLM API configurations."""
    # Groq ($200 credit)
    groq_api_key: str = ""
    
    # OpenRouter (free tiers - USE WITH CAUTION!)
    openrouter_api_key: str = ""
    
    # AWS Bedrock ($200 credit)
    aws_access_key: str = ""
    aws_secret_key: str = ""
    aws_region: str = "us-east-1"
    
    # Ollama (local)
    ollama_url: str = "http://localhost:11434"
    ollama_models: list = None
    
    def __post_init__(self):
        if self.ollama_models is None:
            self.ollama_models = [
                "llama3.1:8b",
                "phi4:14b",
                "qwen2.5:32b"
            ]


@dataclass
class SecurityConfig:
    """Security settings."""
    # Encryption key (32 bytes, base64 encoded)
    encryption_key_b64: str = ""
    
    # LUKS container path (for evidence vault)
    luks_container_path: str = "/evidence/vault.luks"
    
    # Audit log retention (days)
    audit_retention_days: int = 2555  # 7 years for legal
    
    # Maximum failed login attempts
    max_login_attempts: int = 5
    
    # Session timeout (minutes)
    session_timeout: int = 30


@dataclass
class CaseConfig:
    """Case-specific settings."""
    case_id: str = "SOSANA_RICO_2026"
    case_name: str = "SOSANA/CRM RICO Investigation"
    lead_investigator: str = ""
    jurisdiction: str = "Federal"
    
    # Evidence handling
    evidence_prefix: str = "SOSANA"
    chain_of_custody_required: bool = True


class Settings:
    """Application settings singleton."""
    
    def __init__(self):
        self.db = DatabaseConfig(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            name=os.getenv('DB_NAME', 'evidence_fortress'),
            user=os.getenv('DB_USER', 'evidence_user'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        self.llm = LLMConfig(
            groq_api_key=os.getenv('GROQ_API_KEY', ''),
            openrouter_api_key=os.getenv('OPENROUTER_API_KEY', ''),
            aws_access_key=os.getenv('AWS_ACCESS_KEY', ''),
            aws_secret_key=os.getenv('AWS_SECRET_KEY', ''),
            aws_region=os.getenv('AWS_REGION', 'us-east-1'),
            ollama_url=os.getenv('OLLAMA_URL', 'http://localhost:11434')
        )
        
        self.security = SecurityConfig(
            encryption_key_b64=os.getenv('ENCRYPTION_KEY_B64', ''),
            luks_container_path=os.getenv('LUKS_PATH', '/evidence/vault.luks')
        )
        
        self.case = CaseConfig(
            case_id=os.getenv('CASE_ID', 'SOSANA_RICO_2026'),
            case_name=os.getenv('CASE_NAME', 'SOSANA/CRM RICO Investigation')
        )
    
    def get_encryption_key(self) -> bytes:
        """Get encryption key from environment."""
        import base64
        if not self.security.encryption_key_b64:
            raise ValueError("ENCRYPTION_KEY_B64 not set!")
        return base64.b64decode(self.security.encryption_key_b64)


# Global settings instance
settings = Settings()
