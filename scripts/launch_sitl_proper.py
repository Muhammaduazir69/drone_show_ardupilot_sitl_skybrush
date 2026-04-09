#!/usr/bin/env python3
"""
Proper SITL Launcher using dronekit-sitl Python API
Launches multiple SITL instances with proper port management.
"""

import os
import sys
import time
import signal
import subprocess

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APM_PATH = os.path.expanduser("~/.dronekit/sitl/copter-3.3/apm")


def launch_sitl_fleet(num_drones=3):
    """Launch multiple SITL instances using direct binary execution."""
    processes = []
    base_lat = 47.397742
    base_lon = 8.545594
    base_alt = 488.0
    spacing = 0.00005

    print(f"Launching {num_drones} SITL instances...")

    for i in range(num_drones):
        lat = base_lat + (i // 5) * spacing
        lon = base_lon + (i % 5) * spacing
        home = f"{lat},{lon},{base_alt},0"
        instance = i

        cmd = [
            APM_PATH,
            f"--home={home}",
            "--model=quad",
            f"--instance={instance}",
            f"--speedup=1",
        ]

        log_path = os.path.join(PROJECT_DIR, "logs", f"sitl_drone{i+1}.log")
        log_file = open(log_path, "w")

        proc = subprocess.Popen(cmd, stdout=log_file, stderr=log_file)
        processes.append(proc)
        port = 5760 + instance * 10
        print(f"  Drone {i+1}: PID={proc.pid}, port={port}, home={home}")
        time.sleep(2)

    print(f"\nAll {num_drones} SITL instances launched!")
    print("Ports:")
    for i in range(num_drones):
        print(f"  Drone {i+1}: tcp:127.0.0.1:{5760 + i * 10}")

    return processes


def test_connections(num_drones=3):
    """Test MAVLink connections to all drones."""
    from pymavlink import mavutil

    print(f"\nTesting connections to {num_drones} drones...")
    results = []

    for i in range(num_drones):
        port = 5760 + i * 10
        try:
            conn = mavutil.mavlink_connection(f"tcp:127.0.0.1:{port}")
            conn.wait_heartbeat(timeout=15)
            mode = mavutil.mode_string_v10(conn.messages["HEARTBEAT"])

            # Request data
            conn.mav.request_data_stream_send(
                conn.target_system, conn.target_component,
                mavutil.mavlink.MAV_DATA_STREAM_ALL, 4, 1,
            )
            time.sleep(1)

            # Read a few messages
            gps_fix = 0
            sats = 0
            batt_v = 0
            for _ in range(10):
                msg = conn.recv_match(blocking=True, timeout=2)
                if msg:
                    if msg.get_type() == "GPS_RAW_INT":
                        gps_fix = msg.fix_type
                        sats = msg.satellites_visible
                    elif msg.get_type() == "SYS_STATUS":
                        batt_v = msg.voltage_battery / 1000.0

            results.append({
                "drone": i + 1,
                "port": port,
                "system": conn.target_system,
                "mode": mode,
                "gps_fix": gps_fix,
                "gps_sats": sats,
                "battery_v": batt_v,
                "status": "OK",
            })
            print(f"  Drone {i+1}: OK (sys={conn.target_system}, mode={mode}, "
                  f"GPS={gps_fix}/{sats}sats, batt={batt_v:.1f}V)")
            conn.close()
        except Exception as e:
            results.append({"drone": i + 1, "port": port, "status": f"FAIL: {e}"})
            print(f"  Drone {i+1}: FAIL ({e})")

    return results


def test_arm_and_takeoff(drone_id=1, port=5760):
    """Test arming and takeoff of a single drone."""
    from pymavlink import mavutil

    print(f"\nTesting arm + takeoff: Drone {drone_id} on port {port}")
    conn = mavutil.mavlink_connection(f"tcp:127.0.0.1:{port}")
    conn.wait_heartbeat(timeout=10)
    print(f"  Connected: sys={conn.target_system}")

    # Set GUIDED mode
    mode_mapping = conn.mode_mapping()
    if "GUIDED" in mode_mapping:
        conn.mav.set_mode_send(
            conn.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_mapping["GUIDED"],
        )
        print("  Mode: GUIDED set")
        time.sleep(2)

    # Arm
    conn.mav.command_long_send(
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, 0, 0, 0, 0, 0, 0,
    )
    print("  Arm command sent")
    time.sleep(3)

    # Check armed state
    msg = conn.recv_match(type="HEARTBEAT", blocking=True, timeout=5)
    if msg:
        armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
        print(f"  Armed: {armed}")

    # Takeoff to 10m
    conn.mav.command_long_send(
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, 0, 10,
    )
    print("  Takeoff command sent (target: 10m)")
    time.sleep(5)

    # Check altitude
    conn.mav.request_data_stream_send(
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 4, 1,
    )
    time.sleep(2)

    for _ in range(10):
        msg = conn.recv_match(type="VFR_HUD", blocking=True, timeout=2)
        if msg:
            print(f"  Altitude: {msg.alt:.1f}m, Speed: {msg.groundspeed:.1f}m/s")
            break

    # RTL
    if "RTL" in mode_mapping:
        conn.mav.set_mode_send(
            conn.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_mapping["RTL"],
        )
        print("  Mode: RTL set")

    conn.close()
    print(f"  Drone {drone_id} test complete")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["launch", "test", "arm-test", "full"],
                        default="full", nargs="?")
    parser.add_argument("--drones", type=int, default=3)
    args = parser.parse_args()

    if args.action == "launch":
        procs = launch_sitl_fleet(args.drones)
        print("\nPress Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            for p in procs:
                p.terminate()

    elif args.action == "test":
        test_connections(args.drones)

    elif args.action == "arm-test":
        test_arm_and_takeoff()

    elif args.action == "full":
        procs = launch_sitl_fleet(args.drones)
        print("\nWaiting 10s for SITL initialization...")
        time.sleep(10)
        test_connections(args.drones)
        test_arm_and_takeoff(1, 5760)

        # Cleanup
        print("\nCleaning up...")
        for p in procs:
            p.terminate()
        print("Done!")
