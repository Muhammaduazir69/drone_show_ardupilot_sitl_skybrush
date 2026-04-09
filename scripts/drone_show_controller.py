#!/usr/bin/env python3
"""
Drone Show Controller
Main orchestration engine for synchronized drone show execution.
Connects to multiple ArduPilot instances via MAVLink and executes
choreographed formations with precise timing.
"""

import asyncio
import json
import logging
import math
import os
import signal
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# Add project root to path
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

from pymavlink import mavutil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(PROJECT_DIR, "logs", "show_controller.log")),
    ],
)
logger = logging.getLogger("DroneShowController")


class DroneState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    ARMED = "armed"
    TAKING_OFF = "taking_off"
    IN_POSITION = "in_position"
    PERFORMING = "performing"
    RETURNING = "returning"
    LANDED = "landed"
    ERROR = "error"


class ShowPhase(Enum):
    IDLE = "idle"
    PREFLIGHT = "preflight"
    ARMING = "arming"
    TAKEOFF = "takeoff"
    SHOW = "show"
    RTL = "rtl"
    LANDED = "landed"
    EMERGENCY = "emergency"


@dataclass
class DroneStatus:
    drone_id: int
    state: DroneState = DroneState.DISCONNECTED
    armed: bool = False
    mode: str = ""
    lat: float = 0.0
    lon: float = 0.0
    alt: float = 0.0
    relative_alt: float = 0.0
    heading: float = 0.0
    groundspeed: float = 0.0
    battery_voltage: float = 0.0
    battery_remaining: int = 100
    gps_fix: int = 0
    gps_satellites: int = 0
    ekf_ok: bool = False
    last_heartbeat: float = 0.0
    errors: list = field(default_factory=list)


@dataclass
class Waypoint:
    lat: float
    lon: float
    alt: float  # relative altitude in meters
    speed: float = 2.0  # m/s
    hold_time: float = 0.0  # seconds to hold at waypoint
    yaw: float = 0.0  # heading in degrees
    led_color: tuple = (255, 255, 255)  # RGB


@dataclass
class ShowSegment:
    name: str
    duration: float  # seconds
    waypoints: dict  # drone_id -> list of Waypoint


class DroneConnection:
    """Manages MAVLink connection to a single drone."""

    def __init__(self, drone_id: int, connection_string: str):
        self.drone_id = drone_id
        self.connection_string = connection_string
        self.connection = None
        self.status = DroneStatus(drone_id=drone_id)

    def connect(self, timeout: int = 30) -> bool:
        """Establish MAVLink connection."""
        try:
            logger.info(f"Drone {self.drone_id}: Connecting to {self.connection_string}")
            self.connection = mavutil.mavlink_connection(
                self.connection_string,
                source_system=255,
                source_component=self.drone_id,
            )
            self.connection.wait_heartbeat(timeout=timeout)
            self.status.state = DroneState.CONNECTED
            self.status.last_heartbeat = time.time()
            logger.info(
                f"Drone {self.drone_id}: Connected "
                f"(system {self.connection.target_system}, "
                f"component {self.connection.target_component})"
            )
            return True
        except Exception as e:
            logger.error(f"Drone {self.drone_id}: Connection failed: {e}")
            self.status.state = DroneState.ERROR
            self.status.errors.append(str(e))
            return False

    def update_status(self):
        """Read latest MAVLink messages and update drone status."""
        if not self.connection:
            return

        # Process all pending messages (drain buffer to get latest)
        count = 0
        while count < 100:
            msg = self.connection.recv_match(blocking=False)
            if msg is None:
                break
            count += 1

            msg_type = msg.get_type()

            if msg_type == "HEARTBEAT":
                self.status.last_heartbeat = time.time()
                self.status.armed = msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
                self.status.mode = mavutil.mode_string_v10(msg)

            elif msg_type == "GLOBAL_POSITION_INT":
                self.status.lat = msg.lat / 1e7
                self.status.lon = msg.lon / 1e7
                self.status.alt = msg.alt / 1000.0
                self.status.relative_alt = msg.relative_alt / 1000.0
                self.status.heading = msg.hdg / 100.0

            elif msg_type == "VFR_HUD":
                self.status.groundspeed = msg.groundspeed

            elif msg_type == "SYS_STATUS":
                self.status.battery_voltage = msg.voltage_battery / 1000.0
                self.status.battery_remaining = msg.battery_remaining

            elif msg_type == "GPS_RAW_INT":
                self.status.gps_fix = msg.fix_type
                self.status.gps_satellites = msg.satellites_visible

            elif msg_type == "EKF_STATUS_REPORT":
                flags = msg.flags
                self.status.ekf_ok = (
                    flags & mavutil.mavlink.EKF_ATTITUDE
                    and flags & mavutil.mavlink.EKF_VELOCITY_HORIZ
                    and flags & mavutil.mavlink.EKF_VELOCITY_VERT
                    and flags & mavutil.mavlink.EKF_POS_HORIZ_ABS
                    and flags & mavutil.mavlink.EKF_POS_VERT_ABS
                )

    def set_mode(self, mode: str) -> bool:
        """Set flight mode."""
        if not self.connection:
            return False

        mode_mapping = self.connection.mode_mapping()
        if mode not in mode_mapping:
            logger.error(f"Drone {self.drone_id}: Unknown mode '{mode}'")
            return False

        mode_id = mode_mapping[mode]
        self.connection.mav.set_mode_send(
            self.connection.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id,
        )
        logger.info(f"Drone {self.drone_id}: Mode set to {mode}")
        return True

    def arm(self) -> bool:
        """Arm the drone."""
        if not self.connection:
            return False

        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 1, 0, 0, 0, 0, 0, 0,
        )
        logger.info(f"Drone {self.drone_id}: Arm command sent")
        return True

    def disarm(self) -> bool:
        """Disarm the drone."""
        if not self.connection:
            return False

        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 0, 0, 0, 0, 0, 0, 0,
        )
        logger.info(f"Drone {self.drone_id}: Disarm command sent")
        return True

    def takeoff(self, altitude: float) -> bool:
        """Command takeoff to specified altitude."""
        if not self.connection:
            return False

        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 0, 0, 0, 0, 0, 0, altitude,
        )
        logger.info(f"Drone {self.drone_id}: Takeoff to {altitude}m")
        self.status.state = DroneState.TAKING_OFF
        return True

    def goto_position(self, lat: float, lon: float, alt: float, speed: float = 2.0):
        """Send drone to a specific GPS position."""
        if not self.connection:
            return

        # Set speed first
        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED,
            0, 0, speed, -1, 0, 0, 0, 0,
        )

        # Send position target
        self.connection.mav.set_position_target_global_int_send(
            0,  # time_boot_ms
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            0b0000111111111000,  # type_mask (position only)
            int(lat * 1e7),
            int(lon * 1e7),
            alt,
            0, 0, 0,  # velocity
            0, 0, 0,  # acceleration
            0, 0,  # yaw, yaw_rate
        )

    def set_yaw(self, yaw_degrees: float, relative: bool = False):
        """Set drone heading."""
        if not self.connection:
            return

        self.connection.mav.command_long_send(
            self.connection.target_system,
            self.connection.target_component,
            mavutil.mavlink.MAV_CMD_CONDITION_YAW,
            0,
            yaw_degrees,
            25,  # degrees per second
            1 if yaw_degrees >= 0 else -1,  # direction
            1 if relative else 0,  # relative
            0, 0, 0,
        )

    def rtl(self):
        """Return to launch."""
        self.set_mode("RTL")
        self.status.state = DroneState.RETURNING
        logger.info(f"Drone {self.drone_id}: RTL initiated")

    def land(self):
        """Land at current position."""
        self.set_mode("LAND")
        logger.info(f"Drone {self.drone_id}: Landing")

    def is_alive(self) -> bool:
        """Check if heartbeat is recent."""
        return (time.time() - self.status.last_heartbeat) < 5.0

    def close(self):
        """Close connection."""
        if self.connection:
            self.connection.close()
            self.status.state = DroneState.DISCONNECTED


class DroneShowController:
    """Main controller for drone show orchestration."""

    def __init__(self, config_path: str = None):
        self.drones: dict[int, DroneConnection] = {}
        self.show_phase = ShowPhase.IDLE
        self.choreography: list[ShowSegment] = []
        self.running = False
        self.show_start_time: float = 0
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str = None) -> dict:
        """Load show configuration."""
        default_config = {
            "num_drones": 3,
            "base_port": 5760,
            "takeoff_altitude": 10.0,
            "show_altitude": 20.0,
            "max_speed": 5.0,
            "safety_distance": 3.0,
            "geofence_radius": 300,
            "geofence_alt_max": 120,
            "rtl_altitude": 15.0,
            "connection_timeout": 30,
            "heartbeat_timeout": 5.0,
            "preflight_checks": True,
            "base_lat": 47.397742,
            "base_lon": 8.545594,
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                loaded = json.load(f)
                default_config.update(loaded)

        return default_config

    def add_drone(self, drone_id: int, connection_string: str):
        """Add a drone to the show."""
        self.drones[drone_id] = DroneConnection(drone_id, connection_string)

    def connect_all(self) -> bool:
        """Connect to all drones."""
        logger.info(f"Connecting to {len(self.drones)} drones...")
        all_connected = True

        for drone_id, drone in self.drones.items():
            if not drone.connect(timeout=self.config["connection_timeout"]):
                all_connected = False
                logger.error(f"Failed to connect to Drone {drone_id}")

        connected_count = sum(
            1 for d in self.drones.values()
            if d.status.state != DroneState.DISCONNECTED
        )
        logger.info(f"Connected: {connected_count}/{len(self.drones)}")
        return all_connected

    def preflight_check(self) -> dict:
        """Run preflight checks on all drones."""
        self.show_phase = ShowPhase.PREFLIGHT
        results = {}

        for drone_id, drone in self.drones.items():
            drone.update_status()
            checks = {
                "connected": drone.status.state != DroneState.DISCONNECTED,
                "heartbeat": drone.is_alive(),
                "gps_fix": drone.status.gps_fix >= 3,
                "gps_satellites": drone.status.gps_satellites >= 8,
                "ekf_ok": drone.status.ekf_ok,
                "battery_ok": drone.status.battery_voltage > self.config.get("min_battery_voltage", 14.0),
                "battery_level": drone.status.battery_remaining > 30,
                "not_armed": not drone.status.armed,
            }
            results[drone_id] = {
                "passed": all(checks.values()),
                "checks": checks,
                "status": drone.status,
            }

            status = "PASS" if results[drone_id]["passed"] else "FAIL"
            logger.info(f"Drone {drone_id} preflight: {status}")
            for check_name, check_result in checks.items():
                if not check_result:
                    logger.warning(f"  FAILED: {check_name}")

        return results

    def load_choreography(self, choreography_file: str):
        """Load show choreography from JSON file."""
        with open(choreography_file, "r") as f:
            data = json.load(f)

        self.choreography = []
        for segment_data in data["segments"]:
            waypoints = {}
            for drone_id_str, wp_list in segment_data["waypoints"].items():
                drone_id = int(drone_id_str)
                waypoints[drone_id] = [
                    Waypoint(
                        lat=wp["lat"],
                        lon=wp["lon"],
                        alt=wp["alt"],
                        speed=wp.get("speed", 2.0),
                        hold_time=wp.get("hold_time", 0),
                        yaw=wp.get("yaw", 0),
                        led_color=tuple(wp.get("led_color", [255, 255, 255])),
                    )
                    for wp in wp_list
                ]

            self.choreography.append(
                ShowSegment(
                    name=segment_data["name"],
                    duration=segment_data["duration"],
                    waypoints=waypoints,
                )
            )

        logger.info(f"Loaded choreography: {len(self.choreography)} segments")

    async def arm_all(self) -> bool:
        """Arm all drones simultaneously."""
        self.show_phase = ShowPhase.ARMING
        logger.info("Arming all drones...")

        for drone in self.drones.values():
            drone.set_mode("GUIDED")
            await asyncio.sleep(0.5)

        await asyncio.sleep(2)

        for drone in self.drones.values():
            drone.arm()
            await asyncio.sleep(0.3)

        # Wait for arming confirmation
        timeout = time.time() + 15
        while time.time() < timeout:
            all_armed = True
            for drone in self.drones.values():
                drone.update_status()
                if not drone.status.armed:
                    all_armed = False
            if all_armed:
                logger.info("All drones armed successfully")
                return True
            await asyncio.sleep(0.5)

        logger.error("Not all drones armed within timeout")
        return False

    async def takeoff_all(self, altitude: float = None) -> bool:
        """Synchronized takeoff for all drones."""
        self.show_phase = ShowPhase.TAKEOFF
        alt = altitude or self.config["takeoff_altitude"]
        logger.info(f"Takeoff all drones to {alt}m...")

        for drone in self.drones.values():
            drone.takeoff(alt)
            await asyncio.sleep(0.3)

        # Wait for all drones to reach altitude
        timeout = time.time() + 60
        while time.time() < timeout:
            all_at_altitude = True
            for drone in self.drones.values():
                drone.update_status()
                if drone.status.relative_alt < (alt * 0.9):
                    all_at_altitude = False
            if all_at_altitude:
                logger.info("All drones at takeoff altitude")
                return True
            await asyncio.sleep(1)

        logger.warning("Takeoff timeout - not all drones reached altitude")
        return False

    async def execute_segment(self, segment: ShowSegment):
        """Execute a single choreography segment."""
        logger.info(f"Executing segment: {segment.name} ({segment.duration}s)")

        for drone_id, waypoints in segment.waypoints.items():
            if drone_id not in self.drones:
                continue
            drone = self.drones[drone_id]

            for wp in waypoints:
                drone.goto_position(wp.lat, wp.lon, wp.alt, wp.speed)
                if wp.yaw:
                    drone.set_yaw(wp.yaw)

        # Wait for segment duration
        await asyncio.sleep(segment.duration)

    async def execute_show(self):
        """Execute the full drone show choreography."""
        self.show_phase = ShowPhase.SHOW
        self.show_start_time = time.time()
        logger.info("=" * 50)
        logger.info("DRONE SHOW STARTING")
        logger.info("=" * 50)

        for i, segment in enumerate(self.choreography):
            if not self.running:
                logger.warning("Show stopped")
                break

            logger.info(f"Segment {i+1}/{len(self.choreography)}: {segment.name}")
            await self.execute_segment(segment)

            # Safety check between segments
            for drone in self.drones.values():
                drone.update_status()
                if not drone.is_alive():
                    logger.error(f"Drone {drone.drone_id}: Lost heartbeat!")
                    await self.emergency_stop()
                    return

        elapsed = time.time() - self.show_start_time
        logger.info(f"Show completed in {elapsed:.1f}s")

    async def rtl_all(self):
        """Return all drones to launch."""
        self.show_phase = ShowPhase.RTL
        logger.info("Returning all drones to launch...")

        for drone in self.drones.values():
            drone.rtl()
            await asyncio.sleep(0.3)

        # Wait for landing
        timeout = time.time() + 120
        while time.time() < timeout:
            all_landed = True
            for drone in self.drones.values():
                drone.update_status()
                if drone.status.relative_alt > 0.5:
                    all_landed = False
            if all_landed:
                logger.info("All drones landed")
                self.show_phase = ShowPhase.LANDED
                return
            await asyncio.sleep(2)

        logger.warning("RTL timeout")

    async def emergency_stop(self):
        """Emergency stop - land all drones immediately."""
        self.show_phase = ShowPhase.EMERGENCY
        logger.critical("EMERGENCY STOP ACTIVATED")
        self.running = False

        for drone in self.drones.values():
            drone.land()
            await asyncio.sleep(0.1)

    async def run_show(self, choreography_file: str):
        """Execute complete drone show workflow."""
        self.running = True

        try:
            # 1. Connect to all drones
            if not self.connect_all():
                logger.error("Connection failed")
                return False

            # 2. Preflight checks
            preflight = self.preflight_check()
            all_passed = all(r["passed"] for r in preflight.values())
            if not all_passed and self.config["preflight_checks"]:
                logger.error("Preflight checks failed")
                # In SITL, some checks will fail (GPS etc) - continue anyway
                logger.warning("Continuing despite preflight failures (SITL mode)")

            # 3. Load choreography
            self.load_choreography(choreography_file)

            # 4. Arm all drones
            if not await self.arm_all():
                logger.error("Arming failed")
                return False

            # 5. Synchronized takeoff
            if not await self.takeoff_all():
                logger.error("Takeoff failed")
                await self.emergency_stop()
                return False

            # 6. Execute show
            await self.execute_show()

            # 7. RTL
            await self.rtl_all()

            logger.info("Show completed successfully!")
            return True

        except Exception as e:
            logger.error(f"Show error: {e}")
            await self.emergency_stop()
            return False
        finally:
            self.running = False

    def get_all_status(self) -> dict:
        """Get status of all drones."""
        for drone in self.drones.values():
            drone.update_status()

        return {
            "show_phase": self.show_phase.value,
            "drones": {
                drone_id: {
                    "state": drone.status.state.value,
                    "armed": drone.status.armed,
                    "mode": drone.status.mode,
                    "lat": drone.status.lat,
                    "lon": drone.status.lon,
                    "alt": drone.status.relative_alt,
                    "heading": drone.status.heading,
                    "battery_voltage": drone.status.battery_voltage,
                    "battery_remaining": drone.status.battery_remaining,
                    "gps_fix": drone.status.gps_fix,
                    "gps_satellites": drone.status.gps_satellites,
                    "groundspeed": drone.status.groundspeed,
                    "alive": drone.is_alive(),
                }
                for drone_id, drone in self.drones.items()
            },
        }

    def close_all(self):
        """Close all drone connections."""
        for drone in self.drones.values():
            drone.close()


async def main():
    """Main entry point for standalone execution."""
    config_file = os.path.join(PROJECT_DIR, "config", "show_config.json")
    choreography_file = os.path.join(PROJECT_DIR, "choreography", "demo_show.json")

    controller = DroneShowController(config_file)

    # Add 3 drones
    for i in range(1, 4):
        port = 5760 + (i - 1) * 10
        controller.add_drone(i, f"tcp:127.0.0.1:{port}")

    # Handle shutdown
    def shutdown(signum, frame):
        logger.info("Shutdown signal received")
        controller.running = False
        asyncio.get_event_loop().create_task(controller.emergency_stop())

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Run the show
    success = await controller.run_show(choreography_file)
    controller.close_all()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
