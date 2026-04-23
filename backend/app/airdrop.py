"""
RMI V2 Airdrop Checker
Secure wallet verification using message signatures (SIWE-style for EVM, Ed25519 for Solana)
Snappports unified Solana + Base snapshots with exclusion list management.
"""

import os
import time
import secrets
import json
from typing import Optional, Dict, List, Set
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from eth_account import Account
from eth_account.messages import encode_defunct
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import redis

router = APIRouter(prefix="/api/v1/airdrop", tags=["airdrop"])

# ═══════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════

_SNAPSHOT_DIR_OVERRIDE = os.getenv("SNAPSHOT_DIR", "")
if _SNAPSHOT_DIR_OVERRIDE:
    SNAPSHOT_DIR = Path(_SNAPSHOT_DIR_OVERRIDE)
elif Path("/app/snapshots").exists():
    SNAPSHOT_DIR = Path("/app/snapshots")
else:
    SNAPSHOT_DIR = Path(__file__).resolve().parent.parent / "snapshots"

BASE_SNAPSHOT = SNAPSHOT_DIR / "base_snapshot.txt"
SOLANA_SNAPSHOT = SNAPSHOT_DIR / "solana_snapshot.txt"
EXCLUSIONS_FILE = SNAPSHOT_DIR / "exclusions.json"

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

NONCE_TTL = 300  # 5 minutes

# Airdrop pool configuration
# Total RMI to distribute across both chains
AIRDROP_RMI_TOTAL = float(os.getenv("AIRDROP_RMI_TOTAL", "1000000000"))  # 1B default
# Split mode: 'equal' (50/50 per chain) or 'supply_weighted' (by circulating supply)
AIRDROP_CHAIN_SPLIT = os.getenv("AIRDROP_CHAIN_SPLIT", "equal").lower()

# ═══════════════════════════════════════════════════════════════════════════
# REDIS
# ═══════════════════════════════════════════════════════════════════════════

_redis_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
        )
    return _redis_client


# ═══════════════════════════════════════════════════════════════════════════
# EXCLUSIONS
# ═══════════════════════════════════════════════════════════════════════════

_exclusions_cache: Dict[str, Set[str]] = {"solana": set(), "base": set()}
_exclusions_mtime: float = 0.0


def load_exclusions() -> Dict[str, Set[str]]:
    """Load exclusion list from JSON. Returns sets per chain."""
    global _exclusions_cache, _exclusions_mtime

    if not EXCLUSIONS_FILE.exists():
        return {"solana": set(), "base": set()}

    mtime = EXCLUSIONS_FILE.stat().st_mtime
    if _exclusions_mtime >= mtime and _exclusions_cache.get("solana") is not None:
        return _exclusions_cache

    try:
        with open(EXCLUSIONS_FILE, "r") as f:
            data = json.load(f)
        _exclusions_cache = {
            "solana": set(addr.strip() for addr in data.get("solana", []) if addr.strip()),
            "base": set(addr.strip().lower() for addr in data.get("base", []) if addr.strip()),
        }
        _exclusions_mtime = mtime
        print(f"[Airdrop] Loaded exclusions: solana={len(_exclusions_cache['solana'])}, base={len(_exclusions_cache['base'])}")
    except Exception as e:
        print(f"[Airdrop] Error loading exclusions: {e}")

    return _exclusions_cache


def is_excluded(chain: str, address: str) -> bool:
    exclusions = load_exclusions()
    if chain == "base":
        return address.lower() in exclusions.get("base", set())
    return address in exclusions.get("solana", set())


# ═══════════════════════════════════════════════════════════════════════════
# SNAPSHOT LOADER
# ═══════════════════════════════════════════════════════════════════════════

_airdrop_cache: dict = {}
_cache_loaded_at: float = 0
_last_snapshot_mtime: float = 0.0


def _get_snapshot_mtime() -> float:
    mtime = 0.0
    for f in [BASE_SNAPSHOT, SOLANA_SNAPSHOT, EXCLUSIONS_FILE]:
        if f.exists():
            mtime = max(mtime, f.stat().st_mtime)
    return mtime


def load_snapshots() -> dict:
    """Load airdrop snapshots from text files. Format: address,allocation per line."""
    global _airdrop_cache, _cache_loaded_at, _last_snapshot_mtime

    mtime = _get_snapshot_mtime()
    if _cache_loaded_at >= mtime and _airdrop_cache:
        return _airdrop_cache

    exclusions = load_exclusions()
    data = {"base": {}, "solana": {}}

    if BASE_SNAPSHOT.exists():
        with open(BASE_SNAPSHOT, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(",")
                if len(parts) >= 2:
                    addr = parts[0].strip().lower()
                    if addr in exclusions["base"]:
                        continue
                    try:
                        alloc = float(parts[1].strip())
                        data["base"][addr] = alloc
                    except ValueError:
                        continue

    if SOLANA_SNAPSHOT.exists():
        with open(SOLANA_SNAPSHOT, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(",")
                if len(parts) >= 2:
                    addr = parts[0].strip()
                    if addr in exclusions["solana"]:
                        continue
                    try:
                        alloc = float(parts[1].strip())
                        data["solana"][addr] = alloc
                    except ValueError:
                        continue

    _airdrop_cache = data
    _cache_loaded_at = time.time()
    _last_snapshot_mtime = mtime
    print(f"[Airdrop] Loaded snapshots: base={len(data['base'])}, solana={len(data['solana'])}")
    return data


def _get_chain_pools() -> dict:
    """Calculate RMI pool per chain based on split mode."""
    snapshots = load_snapshots()
    sol_total = sum(snapshots.get("solana", {}).values())
    base_total = sum(snapshots.get("base", {}).values())
    combined = sol_total + base_total
    
    if AIRDROP_CHAIN_SPLIT == "supply_weighted" and combined > 0:
        sol_pool = AIRDROP_RMI_TOTAL * (sol_total / combined)
        base_pool = AIRDROP_RMI_TOTAL * (base_total / combined)
    else:
        # Equal split: each chain gets half the total pool
        sol_pool = AIRDROP_RMI_TOTAL / 2
        base_pool = AIRDROP_RMI_TOTAL / 2
    
    return {"solana": sol_pool, "base": base_pool, "solana_supply": sol_total, "base_supply": base_total}


def get_allocation(chain: str, address: str) -> Optional[float]:
    """Return normalized RMI allocation based on holder's % of chain supply."""
    snapshots = load_snapshots()
    chain_data = snapshots.get(chain, {})
    
    if chain == "base":
        raw = chain_data.get(address.lower())
    else:
        raw = chain_data.get(address)
    
    if raw is None or raw <= 0:
        return None
    
    pools = _get_chain_pools()
    supply = pools.get(f"{chain}_supply", 0)
    pool = pools.get(chain, 0)
    
    if supply > 0:
        share = raw / supply
        return share * pool
    return None


# ═══════════════════════════════════════════════════════════════════════════
# SIGNATURE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

def verify_evm_signature(address: str, message: str, signature: str) -> bool:
    """Verify EIP-191 signature for EVM wallets."""
    try:
        msg = encode_defunct(text=message)
        recovered = Account.recover_message(msg, signature=signature)
        return recovered.lower() == address.lower()
    except Exception as e:
        print(f"[Airdrop] EVM verify error: {e}")
        return False


def verify_solana_signature(address: str, message: str, signature: str) -> bool:
    """Verify Ed25519 signature for Solana wallets.
    
    Accepts signature in hex or base58.
    Address is the base58 Solana pubkey.
    """    
    import base58
    
    try:
        # Decode pubkey
        pubkey_bytes = base58.b58decode(address)
        
        # Decode signature (try hex first, then base58)
        sig_bytes = None
        try:
            sig_bytes = bytes.fromhex(signature)
        except ValueError:
            try:
                sig_bytes = base58.b58decode(signature)
            except Exception:
                return False
        
        if sig_bytes is None:
            return False
            
        vk = VerifyKey(pubkey_bytes)
        vk.verify(message.encode("utf-8"), sig_bytes)
        return True
    except BadSignatureError:
        return False
    except Exception as e:
        print(f"[Airdrop] Solana verify error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# API MODELS
# ═══════════════════════════════════════════════════════════════════════════

class NonceResponse(BaseModel):
    nonce: str
    message: str
    expires_in: int


class AirdropCheckRequest(BaseModel):
    wallet: str = Field(..., description="Wallet address (EVM or Solana)")
    signature: str = Field(..., description="Signed message signature")
    nonce: str = Field(..., description="Nonce from /nonce endpoint")
    chain: str = Field(..., description="'base' or 'solana'")


class AirdropCheckResponse(BaseModel):
    eligible: bool
    wallet: str
    chain: str
    allocation: Optional[float] = None
    allocation_formatted: Optional[str] = None
    message: str


class ExclusionUpdateRequest(BaseModel):
    chain: str = Field(..., description="'base' or 'solana'")
    addresses: List[str] = Field(..., description="List of addresses to exclude")


class ExclusionRemoveRequest(BaseModel):
    chain: str = Field(..., description="'base' or 'solana'")
    addresses: List[str] = Field(..., description="List of addresses to remove from exclusions")


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/nonce", response_model=NonceResponse)
async def get_nonce():
    """Generate a SIWE-style nonce for wallet signature verification."""
    nonce = secrets.token_hex(16)
    r = get_redis()
    r.setex(f"airdrop:nonce:{nonce}", NONCE_TTL, "1")
    
    message_template = (
        "CryptoRugMunch V2 Airdrop Verification\n"
        "Sign this message to verify your wallet ownership.\n"
        "This signature does not authorize any transaction.\n"
        f"Nonce: {nonce}"
    )
    
    return NonceResponse(
        nonce=nonce,
        message=message_template,
        expires_in=NONCE_TTL
    )


@router.post("/check", response_model=AirdropCheckResponse)
async def check_airdrop(req: AirdropCheckRequest):
    """Verify wallet signature and return airdrop eligibility from snapshot."""
    
    # Validate chain
    if req.chain not in ("base", "solana"):
        raise HTTPException(status_code=400, detail="Chain must be 'base' or 'solana'")
    
    # Verify nonce exists
    r = get_redis()
    nonce_key = f"airdrop:nonce:{req.nonce}"
    if not r.exists(nonce_key):
        raise HTTPException(status_code=400, detail="Invalid or expired nonce. Please request a new one.")
    
    # Consume nonce (one-time use)
    r.delete(nonce_key)
    
    # Build the exact message that was signed
    message = (
        "CryptoRugMunch V2 Airdrop Verification\n"
        "Sign this message to verify your wallet ownership.\n"
        "This signature does not authorize any transaction.\n"
        f"Nonce: {req.nonce}"
    )
    
    # Verify signature
    if req.chain == "base":
        valid = verify_evm_signature(req.wallet, message, req.signature)
    else:
        valid = verify_solana_signature(req.wallet, message, req.signature)
    
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid signature. Wallet ownership could not be verified.")
    
    # Check exclusion list
    if is_excluded(req.chain, req.wallet):
        return AirdropCheckResponse(
            eligible=False,
            wallet=req.wallet,
            chain=req.chain,
            allocation=0,
            allocation_formatted="0 RMI",
            message="This wallet has been flagged and is not eligible for the airdrop. Contact support if you believe this is an error."
        )
    
    # Check snapshot
    allocation = get_allocation(req.chain, req.wallet)
    
    if allocation is not None and allocation > 0:
        pools = _get_chain_pools()
        supply = pools.get(f"{req.chain}_supply", 0)
        share_pct = (allocation / pools.get(req.chain, 1)) * 100 if pools.get(req.chain) else 0
        return AirdropCheckResponse(
            eligible=True,
            wallet=req.wallet,
            chain=req.chain,
            allocation=allocation,
            allocation_formatted=f"{allocation:,.2f} RMI",
            message=f"You are eligible for the V2 airdrop. You hold {share_pct:.4f}% of the {req.chain} supply. Allocation confirmed from snapshot."
        )
    
    return AirdropCheckResponse(
        eligible=False,
        wallet=req.wallet,
        chain=req.chain,
        allocation=0,
        allocation_formatted="0 RMI",
        message="Wallet not found in snapshot. If you believe this is an error, contact support via Telegram."
    )


@router.get("/stats")
async def airdrop_stats():
    """Public stats about the airdrop snapshot — unified across chains."""
    snapshots = load_snapshots()
    base_raw = sum(snapshots.get("base", {}).values())
    sol_raw = sum(snapshots.get("solana", {}).values())
    
    pools = _get_chain_pools()
    exclusions = load_exclusions()
    
    return {
        "base_holders": len(snapshots.get("base", {})),
        "base_raw_supply": base_raw,
        "base_rmi_pool": pools["base"],
        "solana_holders": len(snapshots.get("solana", {})),
        "solana_raw_supply": sol_raw,
        "solana_rmi_pool": pools["solana"],
        "total_unique_holders": len(snapshots.get("base", {})) + len(snapshots.get("solana", {})),
        "total_rmi_pool": AIRDROP_RMI_TOTAL,
        "chain_split_mode": AIRDROP_CHAIN_SPLIT,
        "excluded_base": len(exclusions.get("base", set())),
        "excluded_solana": len(exclusions.get("solana", set())),
        "snapshot_loaded_at": _cache_loaded_at,
    }


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/admin/exclusions")
async def list_exclusions():
    """List all excluded addresses."""
    exclusions = load_exclusions()
    return {
        "solana": sorted(exclusions.get("solana", set())),
        "base": sorted(exclusions.get("base", set())),
        "count": len(exclusions.get("solana", set())) + len(exclusions.get("base", set())),
    }


@router.post("/admin/exclusions")
async def add_exclusions(req: ExclusionUpdateRequest):
    """Add addresses to exclusion list."""
    if req.chain not in ("base", "solana"):
        raise HTTPException(status_code=400, detail="Chain must be 'base' or 'solana'")
    
    # Load current
    if EXCLUSIONS_FILE.exists():
        with open(EXCLUSIONS_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"description": "Excluded wallets", "updated_at": "", "solana": [], "base": []}
    
    # Normalize
    if req.chain == "base":
        new_addrs = [a.strip().lower() for a in req.addresses if a.strip()]
    else:
        new_addrs = [a.strip() for a in req.addresses if a.strip()]
    
    existing = set(data.get(req.chain, []))
    added = []
    for addr in new_addrs:
        if addr not in existing:
            existing.add(addr)
            added.append(addr)
    
    data[req.chain] = sorted(existing)
    data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    with open(EXCLUSIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    
    # Invalidate cache
    global _exclusions_mtime
    _exclusions_mtime = 0.0
    load_exclusions()
    
    return {"added": added, "chain": req.chain, "total_excluded": len(existing)}


@router.delete("/admin/exclusions")
async def remove_exclusions(req: ExclusionRemoveRequest):
    """Remove addresses from exclusion list."""
    if req.chain not in ("base", "solana"):
        raise HTTPException(status_code=400, detail="Chain must be 'base' or 'solana'")
    
    if not EXCLUSIONS_FILE.exists():
        raise HTTPException(status_code=404, detail="No exclusions file found")
    
    with open(EXCLUSIONS_FILE, "r") as f:
        data = json.load(f)
    
    if req.chain == "base":
        remove_addrs = [a.strip().lower() for a in req.addresses if a.strip()]
    else:
        remove_addrs = [a.strip() for a in req.addresses if a.strip()]
    
    existing = set(data.get(req.chain, []))
    removed = []
    for addr in remove_addrs:
        if addr in existing:
            existing.discard(addr)
            removed.append(addr)
    
    data[req.chain] = sorted(existing)
    data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    with open(EXCLUSIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    
    global _exclusions_mtime
    _exclusions_mtime = 0.0
    load_exclusions()
    
    return {"removed": removed, "chain": req.chain, "total_excluded": len(existing)}
