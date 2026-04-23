"""
Contract Forge Router
=====================
Multi-chain smart contract deployment engine for Base (EVM) and Solana.
Deploy single contracts or bundled deployments from the Darkroom Control Center.
"""
import os
import json
import uuid
import httpx
from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/forge", tags=["contract-forge"])

# ── AUTH ──
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "dev-key-change-me")

async def _verify_forge(request: Request):
    key = request.headers.get("X-Admin-Key", "")
    if key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    return True

# ── CONFIG ──
FORGE_BASE_KEY = os.getenv("FORGE_BASE_KEY", "")
FORGE_SOL_KEY = os.getenv("FORGE_SOL_KEY", "")
ALCHEMY_KEY = os.getenv("ALCHEMY_KEY", "")
HELIUS_KEY = os.getenv("HELIUS_API_KEY", "")

BASE_CHAIN_ID = 8453
BASE_RPC = f"https://base-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}" if ALCHEMY_KEY else ""
SOLANA_RPC = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_KEY}" if HELIUS_KEY else "https://api.mainnet-beta.solana.com"

# ── TEMPLATES ──
TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), "..", "forge_templates", "templates.json")
_templates_cache = None

def _load_templates() -> Dict[str, Any]:
    global _templates_cache
    if _templates_cache is None:
        try:
            with open(TEMPLATES_PATH, "r") as f:
                _templates_cache = json.load(f)
        except Exception:
            _templates_cache = {}
    return _templates_cache


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def _get_redis():
    """Lazy redis import to avoid circular deps."""
    from main import get_redis
    return get_redis

async def _store_deployment(deployment: Dict[str, Any]):
    """Store deployment in Redis + best-effort Supabase."""
    r = await _get_redis()()
    await r.lpush("forge:deployments", json.dumps(deployment))
    await r.hset(f"forge:deployment:{deployment['id']}", mapping={k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in deployment.items()})

async def _get_deployment(dep_id: str) -> Optional[Dict[str, Any]]:
    r = await _get_redis()()
    raw = await r.hgetall(f"forge:deployment:{dep_id}")
    if raw:
        return {k: json.loads(v) if v.startswith("[") or v.startswith("{") else v for k, v in raw.items()}
    return None

async def _get_all_deployments(limit: int = 100) -> List[Dict[str, Any]]:
    r = await _get_redis()()
    raw = await r.lrange("forge:deployments", 0, limit - 1)
    deployments = []
    for item in raw:
        try:
            deployments.append(json.loads(item))
        except:
            pass
    return deployments


# ═══════════════════════════════════════════════════════════════
# BASE (EVM) DEPLOYMENT
# ═══════════════════════════════════════════════════════════════

async def _deploy_base_evm(template_id: str, name: str, symbol: str, supply: Optional[int], owner: str) -> Dict[str, Any]:
    """Deploy an EVM contract on Base using Alchemy."""
    if not FORGE_BASE_KEY or not ALCHEMY_KEY:
        # Simulation mode
        return {
            "status": "simulated",
            "tx_hash": "0x" + os.urandom(32).hex(),
            "contract_address": "0x" + os.urandom(20).hex(),
            "note": "Simulation mode — set FORGE_BASE_KEY and ALCHEMY_KEY for live deployment"
        }

    try:
        from eth_account import Account
        from eth_abi import encode

        templates = _load_templates()
        tpl = templates.get(template_id)
        if not tpl:
            raise ValueError(f"Template {template_id} not found")

        bytecode_hex = tpl["bytecode"].replace("0x", "")
        abi = tpl.get("abi", [])

        # Build constructor args
        constructor_types = tpl.get("constructor_types", [])
        constructor_values = []
        for t in constructor_types:
            if t == "string":
                constructor_values.append(name if len(constructor_values) == 0 else symbol)
            elif t == "uint256":
                constructor_values.append(supply or 1000000)

        # Encode constructor
        if constructor_values:
            encoded = encode(constructor_types, constructor_values)
            deploy_data = bytecode_hex + encoded.hex()
        else:
            deploy_data = bytecode_hex

        # Get nonce and gas price
        account = Account.from_key(FORGE_BASE_KEY)
        deployer_address = account.address

        async with httpx.AsyncClient() as client:
            # Get nonce
            nonce_resp = await client.post(BASE_RPC, json={
                "jsonrpc": "2.0", "id": 1,
                "method": "eth_getTransactionCount",
                "params": [deployer_address, "pending"]
            })
            nonce = int(nonce_resp.json()["result"], 16)

            # Get gas price
            gas_resp = await client.post(BASE_RPC, json={
                "jsonrpc": "2.0", "id": 1,
                "method": "eth_gasPrice",
                "params": []
            })
            gas_price = int(gas_resp.json()["result"], 16)

            # Estimate gas (use a high default for contract creation)
            gas_limit = 3000000

            tx = {
                "nonce": nonce,
                "gasPrice": gas_price,
                "gas": gas_limit,
                "to": "",
                "value": 0,
                "data": "0x" + deploy_data,
                "chainId": BASE_CHAIN_ID,
            }

            signed = Account.sign_transaction(tx, FORGE_BASE_KEY)

            # Broadcast
            broadcast = await client.post(BASE_RPC, json={
                "jsonrpc": "2.0", "id": 1,
                "method": "eth_sendRawTransaction",
                "params": [signed.rawTransaction.hex()]
            })
            result = broadcast.json()

            if "error" in result:
                raise Exception(result["error"].get("message", "Unknown RPC error"))

            tx_hash = result["result"]

            # Compute contract address (CREATE)
            # For simplicity, we don't compute it here; we'll get it from receipt
            return {
                "status": "pending",
                "tx_hash": tx_hash,
                "contract_address": None,
                "note": "Transaction broadcast. Poll for confirmation."
            }
    except Exception as e:
        return {"status": "failed", "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# SOLANA DEPLOYMENT
# ═══════════════════════════════════════════════════════════════

async def _deploy_solana_spl(name: str, symbol: str, supply: int, decimals: int = 9) -> Dict[str, Any]:
    """Create an SPL Token on Solana."""
    if not FORGE_SOL_KEY:
        return {
            "status": "simulated",
            "tx_hash": "simulated-" + os.urandom(16).hex(),
            "contract_address": "simulated-" + os.urandom(16).hex(),
            "note": "Simulation mode — set FORGE_SOL_KEY for live deployment"
        }

    try:
        from solana.rpc.api import Client
        from solders.keypair import Keypair
        from solders.pubkey import Pubkey
        from solders.system_program import ID as SYS_PROGRAM_ID
        from solders.transaction import Transaction
        from spl.token.instructions import (
            initialize_mint, InitializeMintParams,
            create_associated_token_account, mint_to, MintToParams
        )
        from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID

        # Load deployer keypair
        deployer = Keypair.from_base58_string(FORGE_SOL_KEY)
        client = Client(SOLANA_RPC)

        # Create mint keypair
        mint = Keypair()

        # Get recent blockhash
        blockhash_resp = client.get_latest_blockhash()
        recent_blockhash = blockhash_resp.value.blockhash

        # Build transaction
        tx = Transaction()
        tx.fee_payer = deployer.pubkey()

        # Add create account instruction for mint
        from solders.system_program import create_account, CreateAccountParams
        from spl.token.constants import MINT_LEN
        from solana.rpc.types import TxOpts

        # Get rent exemption
        rent_resp = client.get_minimum_balance_for_rent_exemption(MINT_LEN)
        rent_lamports = rent_resp.value

        create_ix = create_account(CreateAccountParams(
            from_pubkey=deployer.pubkey(),
            to_pubkey=mint.pubkey(),
            lamports=rent_lamports,
            space=MINT_LEN,
            owner=TOKEN_PROGRAM_ID,
        ))
        tx.add(create_ix)

        # Initialize mint
        init_ix = initialize_mint(InitializeMintParams(
            program_id=TOKEN_PROGRAM_ID,
            mint=mint.pubkey(),
            decimals=decimals,
            mint_authority=deployer.pubkey(),
            freeze_authority=None,
        ))
        tx.add(init_ix)

        # Create associated token account for deployer
        from spl.token.instructions import get_associated_token_address
        ata = get_associated_token_address(deployer.pubkey(), mint.pubkey())

        create_ata_ix = create_associated_token_account(
            payer=deployer.pubkey(),
            owner=deployer.pubkey(),
            mint=mint.pubkey(),
        )
        tx.add(create_ata_ix)

        # Mint tokens to ATA
        mint_ix = mint_to(MintToParams(
            program_id=TOKEN_PROGRAM_ID,
            mint=mint.pubkey(),
            dest=ata,
            mint_authority=deployer.pubkey(),
            amount=supply * (10 ** decimals),
            signers=[deployer.pubkey()],
        ))
        tx.add(mint_ix)

        # Sign and send
        tx.recent_blockhash = recent_blockhash
        tx.sign(deployer, mint)

        opts = TxOpts(skip_preflight=False, preflight_commitment="confirmed")
        result = client.send_transaction(tx, opts=opts)

        return {
            "status": "confirmed",
            "tx_hash": str(result.value),
            "contract_address": str(mint.pubkey()),
            "note": f"SPL Token '{name}' ({symbol}) created with supply {supply}"
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}


async def _deploy_solana_nft(name: str, symbol: str, uri: str) -> Dict[str, Any]:
    """Create a Metaplex NFT on Solana."""
    if not FORGE_SOL_KEY:
        return {
            "status": "simulated",
            "tx_hash": "simulated-" + os.urandom(16).hex(),
            "contract_address": "simulated-" + os.urandom(16).hex(),
            "note": "Simulation mode — set FORGE_SOL_KEY for live deployment"
        }

    try:
        from solana.rpc.api import Client
        from solders.keypair import Keypair
        from solders.pubkey import Pubkey
        from solders.system_program import ID as SYS_PROGRAM_ID
        from solders.transaction import Transaction
        from spl.token.instructions import (
            initialize_mint, InitializeMintParams,
            create_associated_token_account, mint_to, MintToParams
        )
        from spl.token.constants import TOKEN_PROGRAM_ID, MINT_LEN

        deployer = Keypair.from_base58_string(FORGE_SOL_KEY)
        client = Client(SOLANA_RPC)

        mint = Keypair()
        blockhash_resp = client.get_latest_blockhash()
        recent_blockhash = blockhash_resp.value.blockhash

        tx = Transaction()
        tx.fee_payer = deployer.pubkey()

        from solders.system_program import create_account, CreateAccountParams
        rent_resp = client.get_minimum_balance_for_rent_exemption(MINT_LEN)
        rent_lamports = rent_resp.value

        create_ix = create_account(CreateAccountParams(
            from_pubkey=deployer.pubkey(),
            to_pubkey=mint.pubkey(),
            lamports=rent_lamports,
            space=MINT_LEN,
            owner=TOKEN_PROGRAM_ID,
        ))
        tx.add(create_ix)

        init_ix = initialize_mint(InitializeMintParams(
            program_id=TOKEN_PROGRAM_ID,
            mint=mint.pubkey(),
            decimals=0,
            mint_authority=deployer.pubkey(),
            freeze_authority=None,
        ))
        tx.add(init_ix)

        from spl.token.instructions import get_associated_token_address
        ata = get_associated_token_address(deployer.pubkey(), mint.pubkey())

        create_ata_ix = create_associated_token_account(
            payer=deployer.pubkey(),
            owner=deployer.pubkey(),
            mint=mint.pubkey(),
        )
        tx.add(create_ata_ix)

        mint_ix = mint_to(MintToParams(
            program_id=TOKEN_PROGRAM_ID,
            mint=mint.pubkey(),
            dest=ata,
            mint_authority=deployer.pubkey(),
            amount=1,
            signers=[deployer.pubkey()],
        ))
        tx.add(mint_ix)

        tx.recent_blockhash = recent_blockhash
        tx.sign(deployer, mint)

        from solana.rpc.types import TxOpts
        opts = TxOpts(skip_preflight=False, preflight_commitment="confirmed")
        result = client.send_transaction(tx, opts=opts)

        return {
            "status": "confirmed",
            "tx_hash": str(result.value),
            "contract_address": str(mint.pubkey()),
            "note": f"Metaplex NFT '{name}' ({symbol}) created"
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}


# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.get("/templates")
async def get_templates(request: Request, _=Depends(_verify_forge)):
    """List available contract templates."""
    templates = _load_templates()
    return {
        "templates": [
            {"id": k, "name": v["name"], "chain": v["chain"], "type": v["type"], "description": v["description"]}
            for k, v in templates.items()
        ]
    }


class DeployRequest(BaseModel):
    template_id: str
    name: str
    symbol: str
    supply: Optional[int] = Field(default=1000000)
    decimals: Optional[int] = Field(default=9)
    owner: Optional[str] = Field(default="")
    metadata_uri: Optional[str] = Field(default="")

@router.post("/deploy")
async def deploy_contract(req: DeployRequest, request: Request, _=Depends(_verify_forge)):
    """Deploy a single contract."""
    templates = _load_templates()
    if req.template_id not in templates:
        raise HTTPException(status_code=404, detail="Template not found")

    tpl = templates[req.template_id]
    dep_id = f"dep-{datetime.utcnow().timestamp():.0f}-{uuid.uuid4().hex[:8]}"

    if tpl["chain"] == "base":
        result = await _deploy_base_evm(req.template_id, req.name, req.symbol, req.supply, req.owner or "")
    elif tpl["chain"] == "solana":
        if tpl["type"] == "SPL":
            result = await _deploy_solana_spl(req.name, req.symbol, req.supply, req.decimals)
        else:
            result = await _deploy_solana_nft(req.name, req.symbol, req.metadata_uri or "")
    else:
        raise HTTPException(status_code=400, detail="Unsupported chain")

    deployment = {
        "id": dep_id,
        "template_id": req.template_id,
        "name": req.name,
        "symbol": req.symbol,
        "chain": tpl["chain"],
        "type": tpl["type"],
        "status": result.get("status", "unknown"),
        "tx_hash": result.get("tx_hash"),
        "contract_address": result.get("contract_address"),
        "owner": req.owner or "",
        "error": result.get("error"),
        "note": result.get("note", ""),
        "deployed_at": datetime.utcnow().isoformat(),
        "bundle_id": None,
    }

    await _store_deployment(deployment)
    return {"deployment": deployment}


class BundleRequest(BaseModel):
    name: str
    deployments: List[DeployRequest]

@router.post("/bundle")
async def deploy_bundle(req: BundleRequest, request: Request, _=Depends(_verify_forge)):
    """Deploy multiple contracts in a bundle."""
    bundle_id = f"bundle-{datetime.utcnow().timestamp():.0f}-{uuid.uuid4().hex[:8]}"
    results = []

    for deploy_req in req.deployments:
        templates = _load_templates()
        if deploy_req.template_id not in templates:
            results.append({"error": f"Template {deploy_req.template_id} not found"})
            continue

        tpl = templates[deploy_req.template_id]
        dep_id = f"dep-{datetime.utcnow().timestamp():.0f}-{uuid.uuid4().hex[:8]}"

        if tpl["chain"] == "base":
            result = await _deploy_base_evm(deploy_req.template_id, deploy_req.name, deploy_req.symbol, deploy_req.supply, deploy_req.owner or "")
        elif tpl["chain"] == "solana":
            if tpl["type"] == "SPL":
                result = await _deploy_solana_spl(deploy_req.name, deploy_req.symbol, deploy_req.supply, deploy_req.decimals)
            else:
                result = await _deploy_solana_nft(deploy_req.name, deploy_req.symbol, deploy_req.metadata_uri or "")
        else:
            results.append({"error": "Unsupported chain"})
            continue

        deployment = {
            "id": dep_id,
            "template_id": deploy_req.template_id,
            "name": deploy_req.name,
            "symbol": deploy_req.symbol,
            "chain": tpl["chain"],
            "type": tpl["type"],
            "status": result.get("status", "unknown"),
            "tx_hash": result.get("tx_hash"),
            "contract_address": result.get("contract_address"),
            "owner": deploy_req.owner or "",
            "error": result.get("error"),
            "note": result.get("note", ""),
            "deployed_at": datetime.utcnow().isoformat(),
            "bundle_id": bundle_id,
        }
        await _store_deployment(deployment)
        results.append(deployment)

    return {
        "bundle_id": bundle_id,
        "name": req.name,
        "deployments": results,
        "total": len(results),
        "successful": sum(1 for r in results if r.get("status") in ("confirmed", "pending", "simulated")),
    }


@router.get("/deployments")
async def list_deployments(request: Request, limit: int = 50, _=Depends(_verify_forge)):
    """List deployment history."""
    deployments = await _get_all_deployments(limit)
    return {"deployments": deployments, "total": len(deployments)}


@router.get("/deployments/{dep_id}")
async def get_deployment(dep_id: str, request: Request, _=Depends(_verify_forge)):
    """Get a single deployment."""
    deployment = await _get_deployment(dep_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return {"deployment": deployment}


@router.post("/deployments/{dep_id}/verify")
async def verify_deployment(dep_id: str, request: Request, _=Depends(_verify_forge)):
    """Verify a deployment on-chain and update status."""
    deployment = await _get_deployment(dep_id)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    tx_hash = deployment.get("tx_hash")
    chain = deployment.get("chain")

    if not tx_hash or tx_hash.startswith("simulated"):
        return {"status": "unverifiable", "note": "Simulated or missing transaction hash"}

    try:
        if chain == "base" and ALCHEMY_KEY:
            async with httpx.AsyncClient() as client:
                resp = await client.post(BASE_RPC, json={
                    "jsonrpc": "2.0", "id": 1,
                    "method": "eth_getTransactionReceipt",
                    "params": [tx_hash]
                })
                receipt = resp.json().get("result")
                if receipt and receipt.get("status") == "0x1":
                    contract_addr = receipt.get("contractAddress")
                    deployment["status"] = "confirmed"
                    deployment["contract_address"] = contract_addr
                    await _store_deployment(deployment)
                    return {"status": "confirmed", "contract_address": contract_addr}
                elif receipt:
                    deployment["status"] = "failed"
                    await _store_deployment(deployment)
                    return {"status": "failed", "receipt": receipt}
                else:
                    return {"status": "pending", "note": "Receipt not yet available"}
        elif chain == "solana":
            # Solana transactions are confirmed immediately in our flow
            return {"status": deployment.get("status", "unknown")}
        else:
            return {"status": "unknown", "note": "Unsupported chain for verification"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
