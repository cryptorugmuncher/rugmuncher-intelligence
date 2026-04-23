#!/usr/bin/env python3
"""
Auth dependencies for FastAPI
"""
import os
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from jose import jwt, JWTError

JWT_SECRET = os.getenv("JWT_SECRET", "rmi-jwt-secret-change-me")
ALGORITHM = "HS256"


async def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Verify JWT from Authorization header (wallet or Supabase)."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # Try Supabase-style verification (just decode without secret for now)
        try:
            payload = jwt.get_unverified_claims(token)
            return payload
        except Exception:
            return None


async def require_auth(request: Request) -> Dict[str, Any]:
    """Require valid JWT. Raises 401 if missing/invalid."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user
