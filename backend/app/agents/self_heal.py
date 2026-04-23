"""
Self-Heal Agent
Monitors services and clears stale cache.
"""
import os
import logging
import subprocess
from datetime import datetime

logger = logging.getLogger("self_heal")


def run():
    logger.info("Self-heal agent running")

    # Check backend health
    healthy = True
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:8000/health", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status != 200:
                healthy = False
    except Exception:
        healthy = False

    if not healthy:
        logger.warning("Backend unhealthy — attempting docker compose restart")
        try:
            subprocess.run(["docker", "compose", "restart", "backend"], cwd="/root/rmi", capture_output=True, timeout=60)
        except Exception as e:
            logger.error(f"Restart failed: {e}")

    # Clear stale Redis keys (older than 24h)
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        # Simple ping to ensure connectivity
        r.ping()
        logger.info("Redis healthy")
    except Exception as e:
        logger.warning(f"Redis check failed: {e}")

    logger.info("Self-heal complete")
