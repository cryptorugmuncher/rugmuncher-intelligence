#!/usr/bin/env python3
"""
RMI Server Startup
=============
Usage: python3 /root/rmi/scripts/start_server.py [port]

Starts the RMI API on an available port (default: 5555)
"""

import socket
import sys
import os
import subprocess
import signal
import time

VERIFY_KEY = "RMI-SERVER-2026-VERIFIED"


def find_available_port(start=5555, end=5600):
    """Find an available port in range."""
    for port in range(start, end):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", port))
                return port
        except OSError:
            continue
    return None


def verify_pc():
    """Verify this is the correct PC."""
    return os.path.exists("/root/.env.secure")


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5555

    # Check port availability
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", port))
    except OSError:
        port = find_available_port()
        if port is None:
            print("ERROR: No available ports in 5555-5600")
            sys.exit(1)

    # Verify PC
    if not verify_pc():
        print("ERROR: This is not the authorized PC")
        sys.exit(1)

    print(f"RMI Server starting on port {port}...")
    print(f"URL: http://localhost:{port}")
    print(f"Upload: POST http://localhost:{port}/api/admin/upload")

    os.environ["FLASK_PORT"] = str(port)

    # Start the server
    cmd = [
        "python3",
        "-c",
        f"""
import sys
sys.path.insert(0, "/root/rmi")
from api.investigation_server import create_app
app = create_app()
app.run(host="0.0.0.0", port={port}, debug=False)
""",
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"PID: {proc.pid}")

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
