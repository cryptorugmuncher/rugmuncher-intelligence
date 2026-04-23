#!/usr/bin/env python3
"""
RMI Self-Healing System
=======================
5-state machine: Healthy -> Degraded -> Failing -> Healing -> Emergency
Monitors all services and auto-repairs. Runs as cron job every 60s.
"""

import os
import sys
import json
import time
import subprocess
import asyncio
import urllib.request
import urllib.error
import redis
from datetime import datetime

sys.path.insert(0, "/root/rmi/backend")

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "") or None
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "") or os.getenv("SUPABASE_ANON_KEY", "")

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "")

AI_PROVIDERS = [
    "OPENROUTER_API_KEY",
    "NVIDIA_API_KEY",
    "NVIDIA_DEV_API_KEY",
    "GROQ_API_KEY",
    "GEMINI_API_KEY",
    "MISTRAL_API_KEY",
    "KIMI_API_KEY",
]

CRYPTO_APIS = [
    "HELIUS_API_KEY",
    "HELIUS_API_KEY_2",
    "BIRDEYE_API_KEY",
    "ARKHAM_API_KEY",
    "MORALIS_API_KEY",
    "COINGECKO_API_KEY",
    "SOLSCAN_API_KEY",
    "ETHERSCAN_KEY",
    "BSCSCAN_KEY",
    "ALCHEMY_KEY",
]

STATES = ["healthy", "degraded", "failing", "healing", "emergency"]


def _http_get(url: str, timeout: int = 5, headers=None):
    req = urllib.request.Request(url, method="GET", headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return None, None


def check_redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB):
    try:
        r = redis.Redis(host=host, port=port, password=password, db=db, decode_responses=True)
        return r.ping()
    except Exception:
        return False


def check_supabase():
    if not SUPABASE_URL:
        return {"reachable": False, "reason": "SUPABASE_URL not set"}
    try:
        # Lightweight connectivity check to Supabase REST edge
        headers = {"apikey": SUPABASE_KEY} if SUPABASE_KEY else {}
        status, _ = _http_get(f"{SUPABASE_URL}/rest/v1/", timeout=5, headers=headers)
        # Any response means the edge is reachable (even 401/404)
        return {"reachable": status is not None, "status": status}
    except Exception as e:
        return {"reachable": False, "reason": str(e)}


def check_helius():
    if not HELIUS_API_KEY:
        return {"reachable": False, "reason": "HELIUS_API_KEY not set"}
    try:
        url = (
            f"https://api.helius.xyz/v0/addresses/?api-key={HELIUS_API_KEY}"
            f"&address=11111111111111111111111111111111"
        )
        status, _ = _http_get(url, timeout=10)
        return {"reachable": status == 200, "status": status}
    except Exception as e:
        return {"reachable": False, "reason": str(e)}


def check_ai_providers():
    results = {}
    for key_name in AI_PROVIDERS:
        value = os.getenv(key_name, "")
        results[key_name] = {"set": bool(value), "prefix": value[:4] + "..." if value else None}
    return results


def check_crypto_apis():
    results = {}
    for key_name in CRYPTO_APIS:
        value = os.getenv(key_name, "")
        results[key_name] = {"set": bool(value), "prefix": value[:4] + "..." if value else None}
    return results


def check_backend():
    try:
        status, _ = _http_get("http://127.0.0.1:8000/health", timeout=5)
        return status == 200
    except Exception:
        return False


def check_n8n():
    try:
        status, _ = _http_get("http://127.0.0.1:5678/healthz", timeout=5)
        return status == 200
    except Exception:
        return False


def check_docker_services():
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}:{{.Status}}"],
            capture_output=True, text=True, timeout=10
        )
        services = {}
        for line in result.stdout.strip().split("\n"):
            if ":" in line:
                name, status = line.split(":", 1)
                services[name] = "up" in status.lower()
        return services
    except Exception as e:
        return {"error": str(e)}


def run_checks():
    """Run all health checks and return a report dict.
    Can be imported and called by the worker."""
    checks = {
        "redis": check_redis(),
        "supabase": check_supabase(),
        "helius": check_helius(),
        "ai_providers": check_ai_providers(),
        "crypto_apis": check_crypto_apis(),
        "backend": check_backend(),
        "n8n": check_n8n(),
        "docker": check_docker_services(),
        "timestamp": datetime.utcnow().isoformat(),
    }

    failures = 0
    if not checks["redis"]:
        failures += 1
    if not checks["backend"]:
        failures += 1
    if not checks["n8n"]:
        failures += 1
    if isinstance(checks["supabase"], dict) and not checks["supabase"].get("reachable"):
        failures += 1
    if isinstance(checks["helius"], dict) and not checks["helius"].get("reachable"):
        failures += 1

    return checks, failures


class SelfHealer:
    def __init__(self):
        self.r = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT,
            password=REDIS_PASSWORD, db=REDIS_DB,
            decode_responses=True
        )
        self.state = "healthy"
        self.consecutive_failures = 0

    def run_health_checks(self):
        checks, failures = run_checks()

        # Store in Redis
        self.r.hset(
            "rmi:health",
            mapping={
                k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                for k, v in checks.items()
            }
        )

        return checks, failures

    def determine_state(self, failures):
        if failures == 0:
            return "healthy"
        elif failures == 1:
            return "degraded"
        elif failures == 2:
            return "failing"
        else:
            return "emergency"

    def attempt_repair(self, state, checks):
        repairs = []

        if state in ["failing", "emergency"]:
            if not checks.get("backend", True):
                try:
                    subprocess.run(["docker", "restart", "rmi_backend"], capture_output=True, timeout=30)
                    repairs.append("restarted_backend")
                except Exception as e:
                    repairs.append(f"backend_restart_failed: {e}")

            if not checks.get("n8n", True):
                try:
                    subprocess.run(["docker", "restart", "rmi_n8n"], capture_output=True, timeout=30)
                    repairs.append("restarted_n8n")
                except Exception as e:
                    repairs.append(f"n8n_restart_failed: {e}")

        if state == "emergency":
            try:
                self.r.flushdb()
                repairs.append("cleared_redis_cache")
            except Exception:
                pass

            try:
                subprocess.run(
                    ["docker", "compose", "-f", "/root/rmi/docker-compose.yml", "restart"],
                    capture_output=True, timeout=60, cwd="/root/rmi"
                )
                repairs.append("docker_compose_restart")
            except Exception as e:
                repairs.append(f"compose_restart_failed: {e}")

        return repairs

    def run_cycle(self):
        checks, failures = self.run_health_checks()
        new_state = self.determine_state(failures)

        if new_state != self.state:
            print(f"[{datetime.utcnow().isoformat()}] State change: {self.state} -> {new_state}")
            self.r.set("rmi:state", new_state)
            self.state = new_state

        if new_state in ["failing", "emergency"]:
            repairs = self.attempt_repair(new_state, checks)
            self.r.hset("rmi:repairs", datetime.utcnow().isoformat(), json.dumps(repairs))
            print(f"[{datetime.utcnow().isoformat()}] Repairs: {repairs}")

        return checks


def main():
    healer = SelfHealer()
    once = "--once" in sys.argv
    while True:
        try:
            healer.run_cycle()
        except Exception as e:
            print(f"[{datetime.utcnow().isoformat()}] Error: {e}")
        if once:
            break
        time.sleep(60)


if __name__ == "__main__":
    main()
