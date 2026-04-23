#!/usr/bin/env python3
"""
RMI Background Agents Runner
Starts all background agents via the orchestrator.
Usage: python3 /root/rmi/scripts/run_agents.py
"""
import sys
import os

# Ensure backend is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.agents.orchestrator import main

if __name__ == "__main__":
    main()
