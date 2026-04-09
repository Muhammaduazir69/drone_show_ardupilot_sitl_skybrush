#!/usr/bin/env python3
"""
Pre-Show Comprehensive Checklist
Validates every aspect of drone readiness before a show.
"""

import json
import os
import sys
import time

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from pymavlink import mavutil


class PreflightChecker:
    """Comprehensive preflight check system."""

    REQUIRED_GPS_FIX = 3      # 3D fix minimum
    REQUIRED_GPS_SATS = 8     # Minimum satellites
    MIN_BATTERY_VOLTAGE = 14.0 # 4S LiPo minimum
    MIN_BATTERY_PCT = 80       # Minimum battery percentage for show
    MAX_VIBRATION = 30.0       # Maximum acceptable vibration (m/s/s)
    HEARTBEAT_TIMEOUT = 5.0

    def __init__(self, num_drones: int = 3, base_port: int = 5760):
        self.num_drones = num_drones
        self.base_port = base_port
        self.connections = {}
        self.results = {}

    def connect_all(self) -> bool:
        """Connect to all drones."""
        print("\n[Phase 1] Establishing Connections")
        print("-" * 40)

        all_ok = True
        for i in range(1, self.num_drones + 1):
            port = self.base_port + (i - 1) * 10
            conn_str = f"tcp:127.0.0.1:{port}"
            try:
                conn = mavutil.mavlink_connection(conn_str)
                conn.wait_heartbeat(timeout=10)
                self.connections[i] = conn
                print(f"  Drone {i}: CONNECTED (System {conn.target_system})")
            except Exception as e:
                print(f"  Drone {i}: FAILED ({e})")
                all_ok = False

        return all_ok

    def check_heartbeat(self, drone_id: int) -> bool:
        """Verify heartbeat is active."""
        conn = self.connections.get(drone_id)
        if not conn:
            return False
        msg = conn.recv_match(type="HEARTBEAT", blocking=True, timeout=self.HEARTBEAT_TIMEOUT)
        return msg is not None

    def check_gps(self, drone_id: int) -> dict:
        """Check GPS status."""
        conn = self.connections.get(drone_id)
        if not conn:
            return {"pass": False, "reason": "Not connected"}

        msg = conn.recv_match(type="GPS_RAW_INT", blocking=True, timeout=5)
        if not msg:
            return {"pass": False, "reason": "No GPS data", "fix": 0, "sats": 0}

        fix_ok = msg.fix_type >= self.REQUIRED_GPS_FIX
        sats_ok = msg.satellites_visible >= self.REQUIRED_GPS_SATS

        return {
            "pass": fix_ok and sats_ok,
            "fix_type": msg.fix_type,
            "satellites": msg.satellites_visible,
            "hdop": msg.eph / 100.0 if msg.eph else None,
            "vdop": msg.epv / 100.0 if msg.epv else None,
        }

    def check_battery(self, drone_id: int) -> dict:
        """Check battery status."""
        conn = self.connections.get(drone_id)
        if not conn:
            return {"pass": False, "reason": "Not connected"}

        msg = conn.recv_match(type="SYS_STATUS", blocking=True, timeout=5)
        if not msg:
            return {"pass": False, "reason": "No battery data"}

        voltage = msg.voltage_battery / 1000.0
        remaining = msg.battery_remaining

        return {
            "pass": voltage >= self.MIN_BATTERY_VOLTAGE and remaining >= self.MIN_BATTERY_PCT,
            "voltage": voltage,
            "remaining": remaining,
            "current": msg.current_battery / 100.0 if msg.current_battery >= 0 else None,
        }

    def check_ekf(self, drone_id: int) -> dict:
        """Check EKF status."""
        conn = self.connections.get(drone_id)
        if not conn:
            return {"pass": False, "reason": "Not connected"}

        msg = conn.recv_match(type="EKF_STATUS_REPORT", blocking=True, timeout=5)
        if not msg:
            return {"pass": False, "reason": "No EKF data"}

        flags = msg.flags
        attitude = bool(flags & mavutil.mavlink.EKF_ATTITUDE)
        vel_horiz = bool(flags & mavutil.mavlink.EKF_VELOCITY_HORIZ)
        vel_vert = bool(flags & mavutil.mavlink.EKF_VELOCITY_VERT)
        pos_horiz = bool(flags & mavutil.mavlink.EKF_POS_HORIZ_ABS)
        pos_vert = bool(flags & mavutil.mavlink.EKF_POS_VERT_ABS)

        return {
            "pass": attitude and vel_horiz and vel_vert and pos_horiz and pos_vert,
            "attitude": attitude,
            "vel_horiz": vel_horiz,
            "vel_vert": vel_vert,
            "pos_horiz": pos_horiz,
            "pos_vert": pos_vert,
            "variance_pos": msg.pos_horiz_variance,
            "variance_vel": msg.velocity_variance,
        }

    def check_mode(self, drone_id: int) -> dict:
        """Check current flight mode."""
        conn = self.connections.get(drone_id)
        if not conn:
            return {"pass": False, "reason": "Not connected"}

        msg = conn.recv_match(type="HEARTBEAT", blocking=True, timeout=5)
        if not msg:
            return {"pass": False, "reason": "No heartbeat"}

        armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
        mode = mavutil.mode_string_v10(msg)

        return {
            "pass": not armed,  # Should NOT be armed during preflight
            "mode": mode,
            "armed": armed,
        }

    def check_params(self, drone_id: int) -> dict:
        """Verify critical parameters are set correctly."""
        conn = self.connections.get(drone_id)
        if not conn:
            return {"pass": False, "reason": "Not connected"}

        critical_params = {
            "SYSID_THISMAV": drone_id,
            "FENCE_ENABLE": 1,
            "FS_THR_ENABLE": 1,
            "ARMING_CHECK": 1,
            "EK3_ENABLE": 1,
        }

        results = {}
        all_ok = True
        for name, expected in critical_params.items():
            conn.mav.param_request_read_send(
                conn.target_system,
                conn.target_component,
                name.encode("utf-8"),
                -1,
            )
            msg = conn.recv_match(type="PARAM_VALUE", blocking=True, timeout=3)
            if msg:
                actual = msg.param_value
                ok = abs(actual - expected) < 0.01
                results[name] = {"expected": expected, "actual": actual, "ok": ok}
                if not ok:
                    all_ok = False
            else:
                results[name] = {"expected": expected, "actual": None, "ok": False}
                all_ok = False

        return {"pass": all_ok, "params": results}

    def run_full_check(self) -> dict:
        """Run complete preflight checklist on all drones."""
        print("=" * 60)
        print("  DRONE SHOW PRE-FLIGHT CHECKLIST")
        print(f"  Drones: {self.num_drones}")
        print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Connect
        if not self.connect_all():
            print("\n  WARNING: Not all drones connected")

        results = {}
        for drone_id in range(1, self.num_drones + 1):
            print(f"\n[Drone {drone_id}] Running checks...")
            print("-" * 40)

            drone_results = {}

            # Heartbeat
            heartbeat = self.check_heartbeat(drone_id)
            drone_results["heartbeat"] = {"pass": heartbeat}
            print(f"  Heartbeat:   {'PASS' if heartbeat else 'FAIL'}")

            # GPS
            gps = self.check_gps(drone_id)
            drone_results["gps"] = gps
            print(f"  GPS:         {'PASS' if gps['pass'] else 'FAIL'} "
                  f"(Fix={gps.get('fix_type', 'N/A')}, Sats={gps.get('satellites', 'N/A')})")

            # Battery
            battery = self.check_battery(drone_id)
            drone_results["battery"] = battery
            print(f"  Battery:     {'PASS' if battery['pass'] else 'FAIL'} "
                  f"({battery.get('voltage', 'N/A')}V, {battery.get('remaining', 'N/A')}%)")

            # EKF
            ekf = self.check_ekf(drone_id)
            drone_results["ekf"] = ekf
            print(f"  EKF:         {'PASS' if ekf['pass'] else 'FAIL'}")

            # Mode / Armed state
            mode = self.check_mode(drone_id)
            drone_results["mode"] = mode
            print(f"  Mode:        {'PASS' if mode['pass'] else 'FAIL'} "
                  f"(Mode={mode.get('mode', 'N/A')}, Armed={mode.get('armed', 'N/A')})")

            # Parameters
            params = self.check_params(drone_id)
            drone_results["params"] = params
            print(f"  Parameters:  {'PASS' if params['pass'] else 'FAIL'}")

            # Overall
            all_passed = all(
                v["pass"] if isinstance(v, dict) else v
                for v in drone_results.values()
            )
            drone_results["overall"] = all_passed
            results[drone_id] = drone_results

            status = "READY" if all_passed else "NOT READY"
            print(f"  >>> Drone {drone_id}: {status}")

        # Fleet summary
        ready_count = sum(1 for r in results.values() if r["overall"])
        print(f"\n{'='*60}")
        print(f"  FLEET STATUS: {ready_count}/{self.num_drones} READY")
        all_ready = ready_count == self.num_drones
        print(f"  SHOW GO/NO-GO: {'GO' if all_ready else 'NO-GO'}")
        print(f"{'='*60}")

        # Save results
        report_path = os.path.join(PROJECT_DIR, "logs", "preflight_report.json")
        with open(report_path, "w") as f:
            # Convert non-serializable values
            serializable = {}
            for drone_id, drone_results in results.items():
                serializable[str(drone_id)] = {}
                for check_name, check_result in drone_results.items():
                    if isinstance(check_result, dict):
                        serializable[str(drone_id)][check_name] = {
                            k: v for k, v in check_result.items()
                            if not callable(v)
                        }
                    else:
                        serializable[str(drone_id)][check_name] = check_result
            json.dump(serializable, f, indent=2, default=str)

        print(f"  Report saved: {report_path}")

        # Close connections
        for conn in self.connections.values():
            conn.close()

        return results


if __name__ == "__main__":
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    checker = PreflightChecker(num)
    checker.run_full_check()
