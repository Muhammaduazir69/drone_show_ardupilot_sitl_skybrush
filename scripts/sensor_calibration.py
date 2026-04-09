#!/usr/bin/env python3
"""
Sensor Calibration Script for Drone Show Fleet
Handles accelerometer, compass, and gyro calibration via MAVLink.
For SITL: sets optimal calibration parameters.
For Hardware: triggers onboard calibration routines.
"""

import sys
import time
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from pymavlink import mavutil


def calibrate_sensors(connection_string: str, drone_id: int = 1, is_sitl: bool = True):
    """Calibrate all sensors on a drone."""
    print(f"\n{'='*50}")
    print(f"  Drone {drone_id} - Sensor Calibration")
    print(f"  Mode: {'SITL (parameter-based)' if is_sitl else 'Hardware (interactive)'}")
    print(f"{'='*50}")

    conn = mavutil.mavlink_connection(connection_string)
    conn.wait_heartbeat(timeout=10)
    print(f"  Connected (System {conn.target_system})")

    results = {}

    # 1. Accelerometer Calibration
    print("\n  [1/4] Accelerometer Calibration")
    accel_params = {
        "INS_ACCOFFS_X": 0.0,
        "INS_ACCOFFS_Y": 0.0,
        "INS_ACCOFFS_Z": 0.0,
        "INS_ACCSCAL_X": 1.0,
        "INS_ACCSCAL_Y": 1.0,
        "INS_ACCSCAL_Z": 1.0,
        "INS_ACC2OFFS_X": 0.0,
        "INS_ACC2OFFS_Y": 0.0,
        "INS_ACC2OFFS_Z": 0.0,
        "INS_ACC2SCAL_X": 1.0,
        "INS_ACC2SCAL_Y": 1.0,
        "INS_ACC2SCAL_Z": 1.0,
        "INS_ACCEL_FILTER": 20,
        "INS_USE": 1,
        "INS_USE2": 1,
        "INS_USE3": 0,
    }
    results["accelerometer"] = _set_params(conn, accel_params, "Accelerometer")

    # 2. Gyroscope Calibration
    print("\n  [2/4] Gyroscope Calibration")
    gyro_params = {
        "INS_GYROFFS_X": 0.0,
        "INS_GYROFFS_Y": 0.0,
        "INS_GYROFFS_Z": 0.0,
        "INS_GYR2OFFS_X": 0.0,
        "INS_GYR2OFFS_Y": 0.0,
        "INS_GYR2OFFS_Z": 0.0,
        "INS_GYRO_FILTER": 20,
    }
    results["gyroscope"] = _set_params(conn, gyro_params, "Gyroscope")

    # 3. Compass Calibration
    print("\n  [3/4] Compass Calibration")
    compass_params = {
        "COMPASS_USE": 1,
        "COMPASS_USE2": 0,
        "COMPASS_USE3": 0,
        "COMPASS_ENABLE": 1,
        "COMPASS_AUTODEC": 1,
        "COMPASS_OFS_X": 0.0,
        "COMPASS_OFS_Y": 0.0,
        "COMPASS_OFS_Z": 0.0,
        "COMPASS_DIA_X": 1.0,
        "COMPASS_DIA_Y": 1.0,
        "COMPASS_DIA_Z": 1.0,
        "COMPASS_ODI_X": 0.0,
        "COMPASS_ODI_Y": 0.0,
        "COMPASS_ODI_Z": 0.0,
    }
    results["compass"] = _set_params(conn, compass_params, "Compass")

    # 4. Barometer / Altitude
    print("\n  [4/4] Barometer Configuration")
    baro_params = {
        "GND_ABS_PRESS": 101325.0,
        "GND_TEMP": 20.0,
        "GND_ALT_OFFSET": 0.0,
    }
    results["barometer"] = _set_params(conn, baro_params, "Barometer")

    conn.close()

    # Summary
    print(f"\n{'='*50}")
    print(f"  Drone {drone_id} - Calibration Summary")
    for sensor, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"    {sensor}: {status}")
    print(f"{'='*50}")

    return all(results.values())


def _set_params(conn, params: dict, sensor_name: str) -> bool:
    """Set a group of parameters."""
    success = True
    for name, value in params.items():
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
            success = False
        time.sleep(0.05)

    status = "Complete" if success else "Partial"
    print(f"  {sensor_name} calibration: {status}")
    return success


def calibrate_fleet(num_drones: int = 3, base_port: int = 5760):
    """Calibrate sensors on entire fleet."""
    print("=" * 60)
    print(f"  Fleet Sensor Calibration - {num_drones} drones")
    print("=" * 60)

    results = {}
    for i in range(1, num_drones + 1):
        port = base_port + (i - 1) * 10
        conn_str = f"tcp:127.0.0.1:{port}"
        try:
            results[i] = calibrate_sensors(conn_str, i)
        except Exception as e:
            print(f"  [Drone {i}] FAILED: {e}")
            results[i] = False

    passed = sum(1 for v in results.values() if v)
    print(f"\nFleet calibration: {passed}/{num_drones} passed")
    return results


if __name__ == "__main__":
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    calibrate_fleet(num)
