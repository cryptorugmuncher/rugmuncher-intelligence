"""
Web3 Wallet Authentication Service
==================================
Custom JWT-based wallet sign-in for RMI.
Uses eth-account for signature verification and python-jose for JWT signing.
"""

import os
import secrets
import hashlib
import hmac
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

from eth_account import Account
from eth_account.messages import encode_defunct
from fastapi import HTTPException
from jose import jwt, JWTError

# Secrets
JWT_SECRET = os.getenv("JWT_SECRET", "rmi-jwt-secret-change-me")
WALLET_AUTH_SECRET = os.getenv("WALLET_AUTH_SECRET", JWT_SECRET)

# Supabase client via db_client (optional — for profile lookups)
_supabase_admin = None

try:
    from app.db_client import get_db
    _db = get_db()
    _supabase_admin = _db.db.client
except Exception:
    _db = None


def generate_nonce() -> str:
    """Generate a cryptographically secure nonce."""
    return secrets.token_urlsafe(16)


def build_sign_message(wallet_address: str, nonce: str, timestamp: str) -> str:
    """Build the EIP-191 message to be signed."""
    return (
        f"RugMunch Intelligence wants you to sign in with your Ethereum account.\n"
        f"{wallet_address}\n\n"
        f"Sign in to RugMunch Intelligence.\n\n"
        f"Wallet: {wallet_address}\n"
        f"Nonce: {nonce}\n"
        f"Timestamp: {timestamp}"
    )


def verify_wallet_signature(message: str, signature: str, wallet_address: str) -> bool:
    """Verify an EIP-191 personal_sign signature."""
    try:
        wallet_address = wallet_address.lower()
        encoded = encode_defunct(text=message)
        recovered = Account.recover_message(encoded, signature=signature)
        return recovered.lower() == wallet_address
    except Exception as e:
        print(f"[AUTH] Signature verification failed: {e}")
        return False


def _derive_wallet_id(wallet_address: str) -> str:
    """Derive a deterministic UUID-like user ID from wallet address."""
    addr = wallet_address.lower()
    return hashlib.sha256(addr.encode()).hexdigest()[:32]


def create_wallet_jwt(user_id: str, wallet_address: str, tier: str = "FREE", role: str = "USER") -> str:
    """Create a custom JWT for a wallet-authenticated user."""
    now = datetime.utcnow()
    payload = {
        "sub": user_id,
        "wallet": wallet_address.lower(),
        "tier": tier,
        "role": role,
        "iat": now,
        "exp": now + timedelta(days=7),
        "type": "wallet_auth",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_wallet_jwt(token: str) -> Optional[Dict[str, Any]]:
    """Verify a custom wallet JWT."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "wallet_auth":
            return None
        return {
            "id": payload["sub"],
            "wallet_address": payload["wallet"],
            "tier": payload.get("tier", "FREE"),
            "role": payload.get("role", "USER"),
            "email": f"{payload['wallet'][:6]}...{payload['wallet'][-4:]}@wallet.rmi",
        }
    except JWTError as e:
        print(f"[AUTH] JWT decode failed: {e}")
        return None
    except Exception as e:
        print(f"[AUTH] JWT verification error: {e}")
        return None


async def get_or_create_wallet_user(wallet_address: str) -> Dict[str, Any]:
    """Get or create a wallet user profile. Returns user data + JWT."""
    addr = wallet_address.lower()
    user_id = _derive_wallet_id(addr)
    
    tier = "FREE"
    # Use db_client for proper persistence
    if _db is not None:
        try:
            from app.db_client import User
            user = User(
                id=user_id,
                email=f"{addr[:6]}...{addr[-4:]}@wallet.rmi",
                wallet_address=addr,
                role="USER",
                tier="FREE",
                created_at=datetime.utcnow().isoformat(),
                xp=0,
                level=1,
            )
            upserted = await _db.users.upsert(user)
            tier = upserted.get("tier", "FREE")
        except Exception as e:
            print(f"[AUTH] Profile upsert failed (non-critical): {e}")
    elif _supabase_admin:
        # Fallback to raw supabase client
        try:
            result = _supabase_admin.table("profiles").upsert({
                "id": user_id,
                "wallet_address": addr,
                "display_name": f"Agent {addr[2:8].upper()}",
                "subscription_tier": "FREE",
                "scans_remaining": 5,
                "total_scans_used": 0,
                "reputation_score": 0,
            }, on_conflict="id").execute()
            if result.data:
                tier = result.data[0].get("subscription_tier", "FREE")
        except Exception as e:
            print(f"[AUTH] Profile upsert failed (non-critical): {e}")
    
    access_token = create_wallet_jwt(user_id, addr, tier)
    
    return {
        "id": user_id,
        "email": f"{addr[:6]}...{addr[-4:]}@wallet.rmi",
        "wallet_address": addr,
        "role": "USER",
        "tier": tier,
        "created_at": datetime.utcnow().isoformat(),
        "access_token": access_token,
        "refresh_token": access_token,  # Same for simplicity; JWT has 7-day expiry
    }


# Unified JWT verification for protected routes
async def verify_auth_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify either a custom wallet JWT or a Supabase JWT."""
    # 1. Try custom wallet JWT first (fast, no network)
    wallet_user = verify_wallet_jwt(token)
    if wallet_user:
        return wallet_user
    
    # 2. Try Supabase JWT (requires network or JWKS verification)
    if _supabase_admin:
        try:
            result = _supabase_admin.auth.get_user(token)
            if result and result.user:
                return {
                    "id": result.user.id,
                    "email": result.user.email,
                    "role": "USER",
                }
        except Exception as e:
            print(f"[AUTH] Supabase JWT verification failed: {e}")
    
    return None
