"""
Agent Orchestrator
Manages background agent tasks using APScheduler.
"""
import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, Any, Callable

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
except ImportError:
    BackgroundScheduler = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("/var/log/rmi-agents.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("orchestrator")

AGENT_REGISTRY: Dict[str, Dict[str, Any]] = {}


def register_agent(name: str, func: Callable, minutes: int = 5, args: tuple = ()):
    """Register an agent to run on a schedule."""
    AGENT_REGISTRY[name] = {"func": func, "minutes": minutes, "args": args, "last_run": None, "errors": 0}
    logger.info(f"Registered agent: {name} (every {minutes}m)")


def run_agent(name: str):
    """Execute a single agent and track health."""
    cfg = AGENT_REGISTRY.get(name)
    if not cfg:
        return
    try:
        logger.info(f"Running agent: {name}")
        cfg["func"](*cfg.get("args", ()))
        cfg["last_run"] = datetime.utcnow().isoformat()
        cfg["errors"] = 0
    except Exception as e:
        cfg["errors"] += 1
        logger.error(f"Agent {name} failed: {e}")


def get_agent_status() -> Dict[str, Any]:
    """Return health status for all agents."""
    return {
        name: {
            "last_run": cfg["last_run"],
            "errors": cfg["errors"],
            "interval_minutes": cfg["minutes"],
            "healthy": cfg["errors"] < 3,
        }
        for name, cfg in AGENT_REGISTRY.items()
    }


def start_scheduler() -> BackgroundScheduler:
    """Start the APScheduler with all registered agents."""
    if BackgroundScheduler is None:
        logger.error("APScheduler not installed. Run: pip install apscheduler")
        raise RuntimeError("APScheduler not installed")

    sched = BackgroundScheduler()
    for name, cfg in AGENT_REGISTRY.items():
        sched.add_job(
            run_agent,
            trigger=IntervalTrigger(minutes=cfg["minutes"]),
            id=name,
            replace_existing=True,
            args=[name],
        )
    sched.start()
    logger.info(f"Orchestrator started with {len(AGENT_REGISTRY)} agents")
    return sched


def main():
    # Import and register agents
    try:
        from app.agents.threat_scraper import run as threat_run
        register_agent("threat_scraper", threat_run, minutes=15)
    except Exception as e:
        logger.warning(f"Could not load threat_scraper: {e}")

    try:
        from app.agents.chain_monitor import run as chain_run
        register_agent("chain_monitor", chain_run, minutes=5)
    except Exception as e:
        logger.warning(f"Could not load chain_monitor: {e}")

    try:
        from app.agents.self_heal import run as heal_run
        register_agent("self_heal", heal_run, minutes=2)
    except Exception as e:
        logger.warning(f"Could not load self_heal: {e}")

    try:
        from app.agents.sentiment_agent import run as sentiment_run
        register_agent("sentiment_agent", sentiment_run, minutes=30)
    except Exception as e:
        logger.warning(f"Could not load sentiment_agent: {e}")

    sched = start_scheduler()
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down orchestrator...")
        sched.shutdown()


if __name__ == "__main__":
    main()
