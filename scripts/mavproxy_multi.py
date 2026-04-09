#!/usr/bin/env python3
"""
MAVProxy Multi-Drone Connection Manager
Connects to multiple SITL instances and provides unified control.
"""

import subprocess
import sys
import os
import time
import signal

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_DIR, "logs")

NUM_DRONES = int(sys.argv[1]) if len(sys.argv) > 1 else 3
BASE_PORT = 5760

processes = []


def cleanup(signum=None, frame=None):
    print("\n[INFO] Shutting down all MAVProxy instances...")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=5)
        except Exception:
            p.kill()
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


def launch_mavproxy(drone_id, master_port, out_port):
    """Launch a MAVProxy instance for a single drone."""
    cmd = [
        sys.executable, "-m", "MAVProxy.mavproxy",
        f"--master=tcp:127.0.0.1:{master_port}",
        f"--out=udp:127.0.0.1:{out_port}",
        f"--target-system={drone_id}",
        "--source-system=255",
        f"--source-component={drone_id}",
        "--daemon",
        "--state-basedir", os.path.join(LOG_DIR, f"mavproxy_drone{drone_id}"),
    ]
    os.makedirs(os.path.join(LOG_DIR, f"mavproxy_drone{drone_id}"), exist_ok=True)

    log_file = open(os.path.join(LOG_DIR, f"mavproxy_drone{drone_id}.log"), "w")
    proc = subprocess.Popen(cmd, stdout=log_file, stderr=log_file)
    return proc


print("=" * 50)
print(f"  MAVProxy Multi-Drone Manager")
print(f"  Connecting to {NUM_DRONES} drones")
print("=" * 50)

for i in range(1, NUM_DRONES + 1):
    master_port = BASE_PORT + (i - 1) * 10
    out_port = 14550 + (i - 1)

    print(f"  Drone {i}: tcp:127.0.0.1:{master_port} -> udp:127.0.0.1:{out_port}")
    proc = launch_mavproxy(i, master_port, out_port)
    processes.append(proc)
    time.sleep(1)

print(f"\nAll {NUM_DRONES} MAVProxy instances launched.")
print("Press Ctrl+C to stop.")

# Wait
while True:
    time.sleep(1)
    for i, p in enumerate(processes):
        if p.poll() is not None:
            print(f"WARNING: MAVProxy for Drone {i+1} exited with code {p.returncode}")
