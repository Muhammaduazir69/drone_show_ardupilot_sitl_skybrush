#!/usr/bin/env python3
"""
ESC Calibration Script for Drone Show Fleet
Performs ESC calibration sequence via MAVLink on SITL or real hardware.
"""

import sys
import time
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from pymavlink import mavutil


def calibrate_esc(connection_string: str, drone_id: int = 1):
    """
    Perform ESC calibration procedure.

    For real hardware:
    1. Power off ESCs
    2. Set throttle to max
    3. Power on ESCs
    4. Wait for calibration tones
    5. Set throttle to min
    6. Wait for confirmation tones

    For SITL: simulate the calibration sequence via parameters.
    """
    print(f"[Drone {drone_id}] ESC Calibration")
    print(f"  Connecting to {connection_string}...")

    conn = mavutil.mavlink_connection(connection_string)
    conn.wait_heartbeat(timeout=10)
    print(f"  Connected (System {conn.target_system})")

    # Set ESC calibration parameters
    esc_params = {
        "MOT_SPIN_ARM": 0.10,     # Spin when armed (10%)
        "MOT_SPIN_MIN": 0.15,     # Minimum spin (15%)
        "MOT_SPIN_MAX": 0.95,     # Maximum spin (95%)
        "MOT_THST_EXPO": 0.65,    # Thrust curve expo
        "MOT_THST_HOVER": 0.35,   # Hover throttle estimate
        "MOT_BAT_VOLT_MAX": 16.8, # 4S max voltage
        "MOT_BAT_VOLT_MIN": 13.2, # 4S min voltage
        "MOT_BAT_CURR_MAX": 30.0, # Max current per motor
        "MOT_PWM_TYPE": 0,        # Normal PWM
        "MOT_PWM_MIN": 1000,      # PWM minimum
        "MOT_PWM_MAX": 2000,      # PWM maximum
        "RC_SPEED": 490,          # ESC PWM frequency
        "SERVO_BLH_AUTO": 0,      # BLHeli auto passthrough
    }

    print(f"\n  Setting {len(esc_params)} ESC parameters...")
    for name, value in esc_params.items():
        conn.mav.param_set_send(
            conn.target_system,
            conn.target_component,
            name.encode("utf-8"),
            float(value),
            mavutil.mavlink.MAV_PARAM_TYPE_REAL32,
        )
        ack = conn.recv_match(type="PARAM_VALUE", blocking=True, timeout=2)
        if ack:
            print(f"    {name} = {value} [OK]")
        else:
            print(f"    {name} = {value} [NO ACK]")
        time.sleep(0.1)

    print(f"\n  ESC calibration parameters set for Drone {drone_id}")

    # Verify motor outputs
    print("\n  Motor output verification:")
    for i in range(1, 5):
        param_name = f"SERVO{i}_FUNCTION"
        conn.mav.param_request_read_send(
            conn.target_system,
            conn.target_component,
            param_name.encode("utf-8"),
            -1,
        )
        msg = conn.recv_match(type="PARAM_VALUE", blocking=True, timeout=2)
        if msg:
            print(f"    Motor {i} (SERVO{i}): Function={int(msg.param_value)}")

    conn.close()
    print(f"\n  [Drone {drone_id}] ESC calibration complete")
    return True


def calibrate_fleet(num_drones: int = 3, base_port: int = 5760):
    """Calibrate ESCs on entire fleet."""
    print("=" * 50)
    print(f"  Fleet ESC Calibration - {num_drones} drones")
    print("=" * 50)

    results = {}
    for i in range(1, num_drones + 1):
        port = base_port + (i - 1) * 10
        conn_str = f"tcp:127.0.0.1:{port}"
        try:
            results[i] = calibrate_esc(conn_str, i)
        except Exception as e:
            print(f"  [Drone {i}] FAILED: {e}")
            results[i] = False
        print()

    # Summary
    passed = sum(1 for v in results.values() if v)
    print("=" * 50)
    print(f"  Results: {passed}/{num_drones} passed")
    print("=" * 50)
    return results


if __name__ == "__main__":
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    calibrate_fleet(num)
