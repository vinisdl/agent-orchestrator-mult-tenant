#!/usr/bin/env python3
"""Wait for PostgreSQL to be reachable (used in Docker entrypoint)."""
import os
import sys
import time

import socket

def main():
    host = os.environ.get("DB_HOST", "localhost")
    port = int(os.environ.get("DB_PORT", "5432"))
    timeout = int(os.environ.get("WAIT_FOR_DB_TIMEOUT", "60"))
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2):
                return
        except (socket.error, OSError):
            time.sleep(1)
    print(f"Timeout waiting for {host}:{port}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
