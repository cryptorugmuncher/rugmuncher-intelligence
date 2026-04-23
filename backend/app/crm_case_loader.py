#!/usr/bin/env python3
"""
CRM Investigation Case Loader
==============================
Loads and serves CRM-SCAM-2025-001 case data from the filesystem.
Pre-loads the case into Redis on startup.
"""

import os
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

CASE_ID = "CRM-SCAM-2025-001"
CASE_DIR = Path(os.getenv("CRM_CASE_DIR", "/app/investigation/cases/crm_scam_2025_001"))
CASE_DATA_FILE = CASE_DIR / "case_data.json"
DB_PATH = CASE_DIR / "evidence" / "blockchain_analysis.db"


def _load_json(path: Path) -> Optional[Dict]:
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[CRM] Failed to load {path}: {e}")
        return None


# Publication control — default FALSE until admin explicitly publishes
PUBLISHED_FLAG_PATH = CASE_DIR / ".published"


def is_published() -> bool:
    """Check if the CRM case is published for public viewing."""
    return PUBLISHED_FLAG_PATH.exists()


def set_published(published: bool) -> bool:
    """Toggle publication status. Returns new state."""
    if published:
        PUBLISHED_FLAG_PATH.write_text("1")
        return True
    else:
        if PUBLISHED_FLAG_PATH.exists():
            PUBLISHED_FLAG_PATH.unlink()
        return False


def get_case_summary() -> Dict[str, Any]:
    """Return a slim case summary for the cases list."""
    data = _load_json(CASE_DATA_FILE)
    if not data:
        return {
            "id": CASE_ID,
            "target": "Cross-Token Criminal Enterprise",
            "type": "syndicate",
            "status": "active",
            "published": False,
            "evidence": [],
            "agents_assigned": ["nexus", "tracer", "cipher", "chronicler"],
            "created_at": "2026-04-09T00:00:00",
            "updated_at": "2026-04-13T00:00:00",
            "risk_score": 0.98,
            "findings": {"summary": "CRM case data not loaded"},
        }

    meta = data.get("case_metadata", {})
    summary = data.get("executive_summary", {})
    return {
        "id": CASE_ID,
        "target": meta.get("case_name", "Cross-Token Criminal Enterprise"),
        "type": "syndicate",
        "status": meta.get("investigation_status", "active").lower().replace(" ", "_"),
        "published": is_published(),
        "evidence": list_evidence_files(),
        "agents_assigned": meta.get("assigned_investigators", ["nexus", "tracer", "cipher"]),
        "created_at": meta.get("created_date", "2026-04-09") + "T00:00:00",
        "updated_at": meta.get("last_updated", "2026-04-13") + "T00:00:00",
        "risk_score": 0.98,
        "findings": {
            "financial_impact": meta.get("estimated_financial_impact", "$1.07M - $1.74M"),
            "victim_count": meta.get("victim_count", "2000+"),
            "classification": meta.get("classification", "RICO-eligible"),
            "key_findings": summary.get("key_findings", [])[:5],
            "jurisdictions": meta.get("jurisdictions", []),
        },
    }


def get_full_case_data() -> Dict[str, Any]:
    """Return the full rich CRM case data."""
    data = _load_json(CASE_DATA_FILE)
    if not data:
        return {"error": "Case data not found"}
    return data


def get_timeline() -> List[Dict[str, Any]]:
    """Extract timeline from case data."""
    data = _load_json(CASE_DATA_FILE)
    if not data:
        return []
    return data.get("timeline", [])


def get_criminal_structure() -> Dict[str, Any]:
    """Return the criminal enterprise structure."""
    data = _load_json(CASE_DATA_FILE)
    if not data:
        return {}
    summary = data.get("executive_summary", {})
    return summary.get("criminal_enterprise_structure", {})


def get_wallets_from_db(limit: int = 500) -> List[Dict[str, Any]]:
    """Read wallets from the SQLite blockchain analysis DB."""
    if not DB_PATH.exists():
        return []
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            "SELECT * FROM wallets ORDER BY risk_score DESC LIMIT ?",
            (limit,),
        )
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[CRM] DB read error: {e}")
        return []


def get_wallet_details(address: str) -> Optional[Dict[str, Any]]:
    """Get single wallet + its transactions."""
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM wallets WHERE address = ?", (address,))
        wallet = c.fetchone()
        c.execute(
            "SELECT * FROM transactions WHERE from_wallet = ? OR to_wallet = ? ORDER BY block_time DESC LIMIT 100",
            (address, address),
        )
        txs = c.fetchall()
        conn.close()
        if not wallet:
            return None
        return {
            "wallet": dict(wallet),
            "transactions": [dict(tx) for tx in txs],
        }
    except Exception as e:
        print(f"[CRM] DB read error: {e}")
        return None


def get_transactions(min_suspicion: float = 0.0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get suspicious transactions."""
    if not DB_PATH.exists():
        return []
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            """
            SELECT * FROM transactions
            WHERE suspicious_score >= ?
            ORDER BY suspicious_score DESC, block_time DESC
            LIMIT ?
            """,
            (min_suspicion, limit),
        )
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"[CRM] DB read error: {e}")
        return []


def get_relationship_graph() -> Dict[str, Any]:
    """Load wallet relationship graph JSON."""
    graph_file = CASE_DIR / "evidence" / "wallet_relationship_graph.json"
    return _load_json(graph_file) or {"nodes": [], "edges": [], "metadata": {}}


def list_evidence_files() -> List[str]:
    """List all evidence file paths relative to case dir."""
    evidence = []
    evidence_dir = CASE_DIR / "evidence"
    if evidence_dir.exists():
        for f in sorted(evidence_dir.rglob("*")):
            if f.is_file() and f.name.endswith((".json", ".db", ".md", ".txt", ".html", ".png", ".jpg", ".pdf")):
                evidence.append(str(f.relative_to(CASE_DIR)))
    return evidence


def get_evidence_categories() -> Dict[str, List[Dict[str, Any]]]:
    """Group evidence files by category."""
    categories = {
        "blockchain_data": [],
        "communications": [],
        "forensic_reports": [],
        "photos_screenshots": [],
        "other": [],
    }
    evidence_dir = CASE_DIR / "evidence"
    if not evidence_dir.exists():
        return categories

    for f in sorted(evidence_dir.rglob("*")):
        if not f.is_file():
            continue
        item = {
            "name": f.name,
            "path": str(f.relative_to(CASE_DIR)),
            "size": f.stat().st_size,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
        }
        placed = False
        for cat in categories:
            if cat in str(f.relative_to(evidence_dir)).lower().replace(" ", "_").replace("-", "_"):
                categories[cat].append(item)
                placed = True
                break
        if not placed:
            categories["other"].append(item)
    return categories


def get_stats() -> Dict[str, Any]:
    """Aggregate case stats."""
    data = _load_json(CASE_DATA_FILE)
    meta = data.get("case_metadata", {}) if data else {}
    stats = {
        "wallets": {"total": 0, "suspect": 0, "victim": 0},
        "transactions": {"total": 0, "suspicious": 0},
        "financial": {
            "total_usd": 886597,
            "victim_count": int(meta.get("victim_count", "2000+").replace(",", "").replace("+", "").split()[0]) if meta else 2000,
        },
    }
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(str(DB_PATH))
            c = conn.cursor()
            c.execute("SELECT COUNT(*), classification FROM wallets GROUP BY classification")
            for count, classification in c.fetchall():
                stats["wallets"][classification] = count
                stats["wallets"]["total"] += count
            c.execute(
                "SELECT COUNT(*), SUM(CASE WHEN suspicious_score > 0.5 THEN 1 ELSE 0 END) FROM transactions"
            )
            result = c.fetchone()
            if result:
                stats["transactions"]["total"] = result[0] or 0
                stats["transactions"]["suspicious"] = result[1] or 0
            conn.close()
        except Exception as e:
            print(f"[CRM] Stats error: {e}")
    return stats
