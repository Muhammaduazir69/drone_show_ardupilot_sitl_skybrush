#!/usr/bin/env python3
"""
Enhanced SITL Simulator for Drone Show
Wraps the basic ArduCopter SITL and adds a MAVLink proxy layer that:
- Simulates GPS with proper fix, satellites, and positions
- Simulates battery voltage/current/remaining
- Simulates EKF status
- Supports GUIDED mode, arming, takeoff, and waypoint navigation
- Provides full telemetry for the Skybrush bridge

This allows the complete drone show workflow to work end-to-end.
"""

import asyncio
import math
import os
import signal
import struct
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from pymavlink import mavutil
from pymavlink.dialects.v20 import common as mavlink2


@dataclass
class SimDroneState:
    """Full simulated drone state."""
    drone_id: int
    sysid: int

    # Home position
    home_lat: float = 47.397742
    home_lon: float = 8.545594
    home_alt: float = 488.0

    # Current position
    lat: float = 0.0
    lon: float = 0.0
    alt: float = 0.0  # absolute
    relative_alt: float = 0.0

    # Velocity
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0
    groundspeed: float = 0.0
    airspeed: float = 0.0

    # Attitude
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0
    heading: int = 0

    # Target (for guided mode navigation)
    target_lat: float = 0.0
    target_lon: float = 0.0
    target_alt: float = 0.0
    target_speed: float = 2.0
    has_target: bool = False

    # State
    armed: bool = False
    mode: str = "STABILIZE"
    mode_id: int = 0
    taking_off: bool = False
    takeoff_target_alt: float = 0.0

    # Battery simulation
    battery_voltage: float = 16.8  # Full 4S LiPo
    battery_remaining: int = 100
    battery_current: float = 0.5
    battery_mah_used: float = 0.0
    battery_capacity: float = 5200.0

    # GPS simulation
    gps_fix: int = 3  # 3D fix
    gps_satellites: int = 14
    gps_hdop: int = 80  # 0.80 * 100
    gps_vdop: int = 120

    # EKF
    ekf_flags: int = 0

    # Timing
    boot_time_ms: int = 0
    last_update: float = 0.0


# ArduCopter mode IDs
MODE_STABILIZE = 0
MODE_ACRO = 1
MODE_ALT_HOLD = 2
MODE_AUTO = 3
MODE_GUIDED = 4
MODE_LOITER = 5
MODE_RTL = 6
MODE_CIRCLE = 7
MODE_LAND = 9
MODE_DRIFT = 11
MODE_SPORT = 13
MODE_POSHOLD = 16
MODE_SMART_RTL = 21

MODE_NAMES = {
    0: "STABILIZE", 1: "ACRO", 2: "ALT_HOLD", 3: "AUTO",
    4: "GUIDED", 5: "LOITER", 6: "RTL", 7: "CIRCLE",
    9: "LAND", 11: "DRIFT", 13: "SPORT", 16: "POSHOLD",
    21: "SMART_RTL",
}

NAME_TO_MODE = {v: k for k, v in MODE_NAMES.items()}


class EnhancedSITL:
    """
    Enhanced SITL that simulates full drone behavior.
    Runs as a MAVLink-speaking TCP server on the assigned port.
    """

    # Earth constants
    LAT_PER_METER = 1.0 / 111320.0
    LON_PER_METER_BASE = 1.0 / 111320.0

    def __init__(self, drone_id: int, port: int, home_lat: float, home_lon: float, home_alt: float = 488.0):
        self.state = SimDroneState(
            drone_id=drone_id,
            sysid=drone_id,
            home_lat=home_lat,
            home_lon=home_lon,
            home_alt=home_alt,
            lat=home_lat,
            lon=home_lon,
            alt=home_alt,
            relative_alt=0.0,
            boot_time_ms=int(time.time() * 1000),
            last_update=time.time(),
        )
        self.port = port
        self.server = None
        self.clients: list = []
        self.running = False
        self.lon_per_meter = self.LON_PER_METER_BASE / math.cos(math.radians(home_lat))

    def _boot_ms(self) -> int:
        return int((time.time() * 1000) - self.state.boot_time_ms) & 0xFFFFFFFF

    def _update_physics(self, dt: float):
        """Update drone physics simulation."""
        s = self.state

        if not s.armed:
            s.groundspeed = 0
            s.vx = 0
            s.vy = 0
            s.vz = 0
            return

        # Battery drain
        if s.armed:
            current = 2.0 if s.relative_alt < 0.5 else (8.0 + s.groundspeed * 2.0)
            s.battery_current = current
            s.battery_mah_used += current * (dt / 3600.0) * 1000.0
            s.battery_remaining = max(0, int(100 * (1 - s.battery_mah_used / s.battery_capacity)))
            # Voltage sag model
            sag = (current / 30.0) * 0.5
            base_v = 16.8 * (0.3 + 0.7 * s.battery_remaining / 100.0)
            s.battery_voltage = max(12.0, base_v - sag)

        # Takeoff
        if s.taking_off and s.relative_alt < s.takeoff_target_alt:
            climb_rate = 2.5  # m/s
            s.vz = -climb_rate  # NED: negative = up
            s.relative_alt += climb_rate * dt
            s.alt = s.home_alt + s.relative_alt
            if s.relative_alt >= s.takeoff_target_alt * 0.90:
                s.taking_off = False
                s.vz = 0
            return

        # RTL
        if s.mode == "RTL":
            # First climb to RTL altitude (15m), then fly home, then descend
            rtl_alt = 15.0
            dist_home = self._distance_to(s.lat, s.lon, s.home_lat, s.home_lon)

            if s.relative_alt < rtl_alt - 0.5 and dist_home > 2.0:
                # Climb
                climb = min(1.5, rtl_alt - s.relative_alt) * dt
                s.relative_alt += climb
                s.alt = s.home_alt + s.relative_alt
            elif dist_home > 1.0:
                # Fly toward home
                self._fly_toward(s.home_lat, s.home_lon, rtl_alt, 3.0, dt)
            elif s.relative_alt > 0.3:
                # Descend
                desc = min(1.0, s.relative_alt) * dt
                s.relative_alt = max(0, s.relative_alt - desc)
                s.alt = s.home_alt + s.relative_alt
                s.groundspeed = 0
                s.vx = 0
                s.vy = 0
            else:
                # Landed
                s.relative_alt = 0
                s.alt = s.home_alt
                s.armed = False
                s.mode = "STABILIZE"
                s.mode_id = MODE_STABILIZE
                s.groundspeed = 0
                s.vx = 0
                s.vy = 0
                s.vz = 0
            return

        # LAND
        if s.mode == "LAND":
            if s.relative_alt > 0.3:
                desc = min(0.8, s.relative_alt) * dt
                s.relative_alt = max(0, s.relative_alt - desc)
                s.alt = s.home_alt + s.relative_alt
                s.vz = 0.8
            else:
                s.relative_alt = 0
                s.alt = s.home_alt
                s.armed = False
                s.mode = "STABILIZE"
                s.mode_id = MODE_STABILIZE
                s.vz = 0
            return

        # GUIDED mode - fly to target
        if s.mode == "GUIDED" and s.has_target:
            self._fly_toward(s.target_lat, s.target_lon, s.target_alt, s.target_speed, dt)
            return

        # LOITER - hold position
        if s.mode in ("LOITER", "POSHOLD"):
            s.groundspeed *= 0.9  # Slow down
            s.vx *= 0.9
            s.vy *= 0.9

    def _fly_toward(self, target_lat: float, target_lon: float, target_alt: float, speed: float, dt: float):
        """Fly toward a target position."""
        s = self.state
        dist = self._distance_to(s.lat, s.lon, target_lat, target_lon)
        alt_diff = target_alt - s.relative_alt

        if dist < 0.3 and abs(alt_diff) < 0.3:
            s.groundspeed = 0
            s.vx = 0
            s.vy = 0
            s.vz = 0
            return

        # Horizontal movement
        if dist > 0.3:
            move_dist = min(speed * dt, dist)
            bearing = self._bearing_to(s.lat, s.lon, target_lat, target_lon)

            dlat = move_dist * math.cos(math.radians(bearing)) * self.LAT_PER_METER
            dlon = move_dist * math.sin(math.radians(bearing)) * self.lon_per_meter

            s.lat += dlat
            s.lon += dlon
            s.groundspeed = min(speed, dist / max(dt, 0.01))
            s.heading = int(bearing) % 360

            s.vx = s.groundspeed * math.cos(math.radians(bearing))
            s.vy = s.groundspeed * math.sin(math.radians(bearing))

        # Vertical movement
        if abs(alt_diff) > 0.3:
            vert_speed = min(1.5, abs(alt_diff)) * (1 if alt_diff > 0 else -1)
            s.relative_alt += vert_speed * dt
            s.alt = s.home_alt + s.relative_alt
            s.vz = -vert_speed  # NED

    def _distance_to(self, lat1, lon1, lat2, lon2) -> float:
        """Approximate distance in meters."""
        dlat = (lat2 - lat1) / self.LAT_PER_METER
        dlon = (lon2 - lon1) / self.lon_per_meter
        return math.sqrt(dlat**2 + dlon**2)

    def _bearing_to(self, lat1, lon1, lat2, lon2) -> float:
        """Bearing from point 1 to point 2 in degrees."""
        dlat = (lat2 - lat1) / self.LAT_PER_METER
        dlon = (lon2 - lon1) / self.lon_per_meter
        return (math.degrees(math.atan2(dlon, dlat)) + 360) % 360

    def _build_heartbeat(self) -> bytes:
        """Build HEARTBEAT message."""
        s = self.state
        base_mode = mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED
        if s.armed:
            base_mode |= mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED

        mav = mavutil.mavlink.MAVLink(None, srcSystem=s.sysid, srcComponent=1)
        msg = mav.heartbeat_encode(
            type=mavutil.mavlink.MAV_TYPE_QUADROTOR,
            autopilot=mavutil.mavlink.MAV_AUTOPILOT_ARDUPILOTMEGA,
            base_mode=base_mode,
            custom_mode=s.mode_id,
            system_status=mavutil.mavlink.MAV_STATE_ACTIVE if s.armed else mavutil.mavlink.MAV_STATE_STANDBY,
        )
        return msg.pack(mav)

    def _build_global_position(self) -> bytes:
        s = self.state
        mav = mavutil.mavlink.MAVLink(None, srcSystem=s.sysid, srcComponent=1)
        msg = mav.global_position_int_encode(
            time_boot_ms=self._boot_ms(),
            lat=int(s.lat * 1e7),
            lon=int(s.lon * 1e7),
            alt=int(s.alt * 1000),
            relative_alt=int(s.relative_alt * 1000),
            vx=int(s.vx * 100),
            vy=int(s.vy * 100),
            vz=int(s.vz * 100),
            hdg=s.heading * 100,
        )
        return msg.pack(mav)

    def _build_gps_raw(self) -> bytes:
        s = self.state
        mav = mavutil.mavlink.MAVLink(None, srcSystem=s.sysid, srcComponent=1)
        msg = mav.gps_raw_int_encode(
            time_usec=int(time.time() * 1e6),
            fix_type=s.gps_fix,
            lat=int(s.lat * 1e7),
            lon=int(s.lon * 1e7),
            alt=int(s.alt * 1000),
            eph=s.gps_hdop,
            epv=s.gps_vdop,
            vel=int(s.groundspeed * 100),
            cog=s.heading * 100,
            satellites_visible=s.gps_satellites,
        )
        return msg.pack(mav)

    def _build_sys_status(self) -> bytes:
        s = self.state
        mav = mavutil.mavlink.MAVLink(None, srcSystem=s.sysid, srcComponent=1)
        msg = mav.sys_status_encode(
            onboard_control_sensors_present=0x0FFF,
            onboard_control_sensors_enabled=0x0FFF,
            onboard_control_sensors_health=0x0FFF,
            load=250,
            voltage_battery=int(s.battery_voltage * 1000),
            current_battery=int(s.battery_current * 100),
            battery_remaining=s.battery_remaining,
            drop_rate_comm=0,
            errors_comm=0,
            errors_count1=0,
            errors_count2=0,
            errors_count3=0,
            errors_count4=0,
        )
        return msg.pack(mav)

    def _build_vfr_hud(self) -> bytes:
        s = self.state
        mav = mavutil.mavlink.MAVLink(None, srcSystem=s.sysid, srcComponent=1)
        msg = mav.vfr_hud_encode(
            airspeed=s.groundspeed,
            groundspeed=s.groundspeed,
            heading=s.heading,
            throttle=50 if s.armed and s.relative_alt > 0.5 else 0,
            alt=s.alt,
            climb=-s.vz,
        )
        return msg.pack(mav)

    def _build_ekf_status(self) -> bytes:
        s = self.state
        # All flags set = EKF healthy
        flags = (
            mavutil.mavlink.EKF_ATTITUDE |
            mavutil.mavlink.EKF_VELOCITY_HORIZ |
            mavutil.mavlink.EKF_VELOCITY_VERT |
            mavutil.mavlink.EKF_POS_HORIZ_REL |
            mavutil.mavlink.EKF_POS_HORIZ_ABS |
            mavutil.mavlink.EKF_POS_VERT_ABS |
            mavutil.mavlink.EKF_POS_VERT_AGL |
            mavutil.mavlink.EKF_PRED_POS_HORIZ_REL |
            mavutil.mavlink.EKF_PRED_POS_HORIZ_ABS
        )
        mav = mavutil.mavlink.MAVLink(None, srcSystem=s.sysid, srcComponent=1)
        msg = mav.ekf_status_report_encode(
            flags=flags,
            velocity_variance=0.02,
            pos_horiz_variance=0.03,
            pos_vert_variance=0.02,
            compass_variance=0.01,
            terrain_alt_variance=0.0,
        )
        return msg.pack(mav)

    def _build_attitude(self) -> bytes:
        s = self.state
        mav = mavutil.mavlink.MAVLink(None, srcSystem=s.sysid, srcComponent=1)
        msg = mav.attitude_encode(
            time_boot_ms=self._boot_ms(),
            roll=s.roll,
            pitch=s.pitch,
            yaw=math.radians(s.heading),
            rollspeed=0,
            pitchspeed=0,
            yawspeed=0,
        )
        return msg.pack(mav)

    def _process_incoming(self, data: bytes):
        """Process incoming MAVLink messages from GCS."""
        if not hasattr(self, '_rx_mav'):
            self._rx_mav = mavutil.mavlink.MAVLink(None, srcSystem=255, srcComponent=0)
            self._rx_mav.robust_parsing = True
        try:
            for byte in data:
                msg = self._rx_mav.parse_char(bytes([byte]))
                if msg and msg.get_type() != 'BAD_DATA':
                    self._handle_message(msg)
        except Exception as e:
            pass

    def _handle_message(self, msg):
        """Handle an incoming MAVLink message."""
        s = self.state
        mtype = msg.get_type()
        pass  # Message routing below

        if mtype == "SET_MODE":
            mode_id = msg.custom_mode
            if mode_id in MODE_NAMES:
                s.mode = MODE_NAMES[mode_id]
                s.mode_id = mode_id
                s.has_target = False
                s.taking_off = False

        elif mtype == "COMMAND_LONG":
            cmd = msg.command

            if cmd == mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM:
                if msg.param1 == 1:
                    s.armed = True
                else:
                    s.armed = False

            elif cmd == mavutil.mavlink.MAV_CMD_NAV_TAKEOFF:
                alt = msg.param7
                if s.armed:
                    s.taking_off = True
                    s.takeoff_target_alt = alt
                    s.mode = "GUIDED"
                    s.mode_id = MODE_GUIDED

            elif cmd == mavutil.mavlink.MAV_CMD_DO_SET_MODE:
                mode_id = int(msg.param2)
                if mode_id in MODE_NAMES:
                    s.mode = MODE_NAMES[mode_id]
                    s.mode_id = mode_id
                    s.has_target = False  # Clear target on mode change

            elif cmd == mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED:
                s.target_speed = msg.param2

            elif cmd == mavutil.mavlink.MAV_CMD_CONDITION_YAW:
                target_yaw = msg.param1
                if msg.param4 == 0:  # Absolute
                    s.heading = int(target_yaw) % 360
                else:  # Relative
                    s.heading = (s.heading + int(target_yaw)) % 360

        elif mtype == "SET_POSITION_TARGET_GLOBAL_INT":
            s.target_lat = msg.lat_int / 1e7
            s.target_lon = msg.lon_int / 1e7
            s.target_alt = msg.alt
            s.has_target = True
            # print(f"  [Drone {s.drone_id}] Target: {s.target_lat:.6f}, {s.target_lon:.6f}, {s.target_alt}m")

        elif mtype == "PARAM_REQUEST_LIST":
            pass  # Could send params, skip for now

        elif mtype == "PARAM_SET":
            pass  # Accept all param sets silently

        elif mtype == "REQUEST_DATA_STREAM":
            pass  # We stream everything anyway

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle a connected GCS client."""
        self.clients.append((reader, writer))

        # Per-client MAVLink parser
        rx_mav = mavutil.mavlink.MAVLink(None, srcSystem=255, srcComponent=0)
        rx_mav.robust_parsing = True

        try:
            while self.running:
                try:
                    data = await reader.read(4096)
                    if not data:
                        break
                    for byte in data:
                        try:
                            msg = rx_mav.parse_char(bytes([byte]))
                            if msg and msg.get_type() != 'BAD_DATA':
                                self._handle_message(msg)
                        except Exception:
                            pass
                except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, OSError):
                    break
        finally:
            if (reader, writer) in self.clients:
                self.clients.remove((reader, writer))
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def _telemetry_loop(self):
        """Send telemetry at ~10Hz."""
        msg_cycle = 0
        while self.running:
            now = time.time()
            dt = now - self.state.last_update
            self.state.last_update = now

            # Update physics
            self._update_physics(dt)

            # Build messages to send
            messages = []
            messages.append(self._build_heartbeat())  # Always send heartbeat

            if msg_cycle % 2 == 0:
                messages.append(self._build_global_position())
                messages.append(self._build_vfr_hud())

            if msg_cycle % 3 == 0:
                messages.append(self._build_gps_raw())
                messages.append(self._build_sys_status())

            if msg_cycle % 5 == 0:
                messages.append(self._build_ekf_status())
                messages.append(self._build_attitude())

            # Send to all clients
            data = b"".join(messages)
            dead_clients = []
            for reader, writer in self.clients:
                try:
                    writer.write(data)
                    await writer.drain()
                except Exception:
                    dead_clients.append((reader, writer))

            for client in dead_clients:
                if client in self.clients:
                    self.clients.remove(client)

            msg_cycle += 1
            await asyncio.sleep(0.1)  # 10Hz

    async def start(self):
        """Start the enhanced SITL server."""
        self.running = True

        self.server = await asyncio.start_server(
            self._handle_client,
            "127.0.0.1",
            self.port,
        )

        print(f"  Drone {self.state.drone_id}: Enhanced SITL on tcp:127.0.0.1:{self.port} "
              f"(SYSID={self.state.sysid}, "
              f"Home={self.state.home_lat:.6f},{self.state.home_lon:.6f})")

        # Start telemetry loop
        asyncio.create_task(self._telemetry_loop())

    async def stop(self):
        """Stop the SITL server."""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()


class EnhancedSITLFleet:
    """Manage a fleet of enhanced SITL drones."""

    def __init__(self, num_drones: int = 3, base_port: int = 5760):
        self.drones: list[EnhancedSITL] = []
        self.num_drones = num_drones
        self.base_port = base_port

        base_lat = 47.397742
        base_lon = 8.545594
        base_alt = 488.0
        spacing = 0.00005  # ~5.5m

        for i in range(num_drones):
            row = i // 5
            col = i % 5
            lat = base_lat + row * spacing
            lon = base_lon + col * spacing
            port = base_port + i * 10

            drone = EnhancedSITL(
                drone_id=i + 1,
                port=port,
                home_lat=lat,
                home_lon=lon,
                home_alt=base_alt,
            )
            self.drones.append(drone)

    async def start_all(self):
        """Start all SITL drones."""
        print(f"\n{'='*60}")
        print(f"  Enhanced SITL Fleet - {self.num_drones} Drones")
        print(f"  Full sensor simulation: GPS, Battery, EKF, Navigation")
        print(f"{'='*60}\n")

        for drone in self.drones:
            await drone.start()
            await asyncio.sleep(0.2)

        print(f"\n  All {self.num_drones} drones ready!")
        print(f"  Connect at: tcp:127.0.0.1:{self.base_port} ... "
              f"tcp:127.0.0.1:{self.base_port + (self.num_drones - 1) * 10}")

    async def stop_all(self):
        for drone in self.drones:
            await drone.stop()


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Enhanced SITL Fleet Simulator")
    parser.add_argument("--drones", type=int, default=3, help="Number of drones")
    parser.add_argument("--port", type=int, default=5760, help="Base TCP port")
    args = parser.parse_args()

    fleet = EnhancedSITLFleet(num_drones=args.drones, base_port=args.port)
    await fleet.start_all()

    print(f"\n  Press Ctrl+C to stop\n")

    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        await fleet.stop_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
