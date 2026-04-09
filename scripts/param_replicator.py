#!/usr/bin/env python3
"""
Parameter Replication System for Scaling to 150+ Drones
Generates unique parameter files for each drone from a base template,
handles SYSID assignment, GPS offset calculation, and batch parameter upload.
"""

import argparse
import json
import math
import os
import sys
import time
from dataclasses import dataclass

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from pymavlink import mavutil


@dataclass
class DroneConfig:
    drone_id: int
    sysid: int
    home_lat: float
    home_lon: float
    home_alt: float
    row: int
    col: int
    param_file: str


class ParameterReplicator:
    """Generate and deploy parameters across a fleet of drones."""

    # GPS offset per meter at reference latitude (approx 47.4N)
    LAT_PER_METER = 1.0 / 111320.0
    LON_PER_METER = 1.0 / (111320.0 * math.cos(math.radians(47.4)))

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.base_params = {}
        self.drone_configs: list[DroneConfig] = []

    def _load_config(self, config_path: str = None) -> dict:
        """Load fleet configuration."""
        default = {
            "num_drones": 150,
            "base_lat": 47.397742,
            "base_lon": 8.545594,
            "base_alt": 488.0,
            "grid_spacing_meters": 5.0,
            "grid_columns": 15,
            "base_port": 5760,
            "port_increment": 10,
            "base_param_file": os.path.join(
                PROJECT_DIR, "config", "drone_params", "drone_show_base.param"
            ),
            "output_dir": os.path.join(PROJECT_DIR, "config", "fleet_params"),
        }
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                default.update(json.load(f))
        return default

    def load_base_params(self, param_file: str = None):
        """Load base parameter template."""
        filepath = param_file or self.config["base_param_file"]
        self.base_params = {}

        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(",", 1)
                if len(parts) == 2:
                    name = parts[0].strip()
                    value = parts[1].strip()
                    try:
                        self.base_params[name] = float(value)
                    except ValueError:
                        self.base_params[name] = value

        print(f"Loaded {len(self.base_params)} base parameters")

    def calculate_grid_positions(self):
        """Calculate GPS home positions for all drones in a grid layout."""
        num_drones = self.config["num_drones"]
        columns = self.config["grid_columns"]
        spacing = self.config["grid_spacing_meters"]
        base_lat = self.config["base_lat"]
        base_lon = self.config["base_lon"]
        base_alt = self.config["base_alt"]

        self.drone_configs = []

        for i in range(num_drones):
            row = i // columns
            col = i % columns

            # Center the grid
            total_rows = math.ceil(num_drones / columns)
            lat_offset = (row - total_rows / 2) * spacing * self.LAT_PER_METER
            lon_offset = (col - columns / 2) * spacing * self.LON_PER_METER

            drone_lat = base_lat + lat_offset
            drone_lon = base_lon + lon_offset

            self.drone_configs.append(DroneConfig(
                drone_id=i + 1,
                sysid=i + 1,
                home_lat=drone_lat,
                home_lon=drone_lon,
                home_alt=base_alt,
                row=row,
                col=col,
                param_file="",
            ))

        print(f"Calculated positions for {num_drones} drones "
              f"({math.ceil(num_drones / columns)} rows x {columns} cols)")

    def generate_param_files(self):
        """Generate individual parameter files for each drone."""
        output_dir = self.config["output_dir"]
        os.makedirs(output_dir, exist_ok=True)

        for drone in self.drone_configs:
            params = dict(self.base_params)

            # Set unique SYSID
            params["SYSID_THISMAV"] = drone.sysid

            # Write param file
            filename = f"drone_{drone.drone_id:03d}.param"
            filepath = os.path.join(output_dir, filename)
            drone.param_file = filepath

            with open(filepath, "w") as f:
                f.write(f"# Drone {drone.drone_id} Parameters\n")
                f.write(f"# SYSID: {drone.sysid}\n")
                f.write(f"# Grid Position: Row {drone.row}, Col {drone.col}\n")
                f.write(f"# Home: {drone.home_lat:.7f}, {drone.home_lon:.7f}, "
                        f"{drone.home_alt:.1f}\n")
                f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("#\n")

                for name, value in sorted(params.items()):
                    if isinstance(value, float):
                        if value == int(value):
                            f.write(f"{name},{int(value)}\n")
                        else:
                            f.write(f"{name},{value}\n")
                    else:
                        f.write(f"{name},{value}\n")

        print(f"Generated {len(self.drone_configs)} parameter files in {output_dir}")

    def generate_fleet_manifest(self):
        """Generate a fleet manifest JSON file."""
        manifest = {
            "fleet_name": "Drone Show Fleet",
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "num_drones": len(self.drone_configs),
            "grid_config": {
                "spacing_meters": self.config["grid_spacing_meters"],
                "columns": self.config["grid_columns"],
                "rows": math.ceil(len(self.drone_configs) / self.config["grid_columns"]),
            },
            "base_position": {
                "lat": self.config["base_lat"],
                "lon": self.config["base_lon"],
                "alt": self.config["base_alt"],
            },
            "drones": [
                {
                    "id": d.drone_id,
                    "sysid": d.sysid,
                    "home_lat": round(d.home_lat, 7),
                    "home_lon": round(d.home_lon, 7),
                    "home_alt": d.home_alt,
                    "row": d.row,
                    "col": d.col,
                    "port": self.config["base_port"] + (d.drone_id - 1) * self.config["port_increment"],
                    "param_file": d.param_file,
                }
                for d in self.drone_configs
            ],
        }

        manifest_path = os.path.join(self.config["output_dir"], "fleet_manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"Fleet manifest saved to {manifest_path}")
        return manifest

    def generate_sitl_launch_script(self):
        """Generate a bash script to launch all SITL instances."""
        script_path = os.path.join(PROJECT_DIR, "scripts", "launch_fleet_sitl.sh")

        with open(script_path, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Auto-generated fleet SITL launch script\n")
            f.write(f"# {len(self.drone_configs)} drones\n\n")
            f.write("set -e\n\n")
            f.write('SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\n')
            f.write('PROJECT_DIR="$(dirname "$SCRIPT_DIR")"\n')
            f.write('source "$PROJECT_DIR/venv/bin/activate"\n\n')
            f.write("PIDS=()\n\n")

            for drone in self.drone_configs:
                port = self.config["base_port"] + (drone.drone_id - 1) * self.config["port_increment"]
                home = f"{drone.home_lat},{drone.home_lon},{drone.home_alt},0"
                f.write(f"# Drone {drone.drone_id} (SYSID={drone.sysid})\n")
                f.write(f'dronekit-sitl copter --home="{home}" '
                        f'--instance {drone.drone_id - 1} '
                        f'-I {drone.drone_id - 1} '
                        f'--sysid {drone.sysid} '
                        f'> "$PROJECT_DIR/logs/sitl_drone{drone.drone_id}.log" 2>&1 &\n')
                f.write("PIDS+=($!)\n")
                # Add small delay every 10 drones to avoid overwhelming the system
                if drone.drone_id % 10 == 0:
                    f.write("sleep 2\n")
                f.write("\n")

            f.write(f'\necho "Launched {len(self.drone_configs)} SITL instances"\n')
            f.write('echo "${PIDS[*]}" > "$PROJECT_DIR/logs/fleet_pids.txt"\n')
            f.write('echo "PIDs saved to logs/fleet_pids.txt"\n\n')
            f.write('trap "kill ${PIDS[*]} 2>/dev/null; exit 0" SIGINT SIGTERM\n')
            f.write("wait\n")

        os.chmod(script_path, 0o755)
        print(f"Fleet SITL launch script saved to {script_path}")

    def upload_params_to_drone(self, drone_id: int, connection_string: str):
        """Upload parameters to a single drone via MAVLink."""
        drone = next((d for d in self.drone_configs if d.drone_id == drone_id), None)
        if not drone:
            print(f"Drone {drone_id} not found")
            return False

        # Load drone-specific params
        params = {}
        with open(drone.param_file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(",", 1)
                if len(parts) == 2:
                    try:
                        params[parts[0].strip()] = float(parts[1].strip())
                    except ValueError:
                        pass

        # Connect and upload
        print(f"Connecting to Drone {drone_id} at {connection_string}...")
        conn = mavutil.mavlink_connection(connection_string)
        conn.wait_heartbeat(timeout=10)
        print(f"Connected. Uploading {len(params)} parameters...")

        count = 0
        for name, value in params.items():
            conn.mav.param_set_send(
                conn.target_system,
                conn.target_component,
                name.encode("utf-8"),
                value,
                mavutil.mavlink.MAV_PARAM_TYPE_REAL32,
            )
            # Wait for ACK
            ack = conn.recv_match(type="PARAM_VALUE", blocking=True, timeout=2)
            if ack:
                count += 1
            else:
                print(f"  WARNING: No ACK for {name}")

            if count % 50 == 0:
                print(f"  Uploaded {count}/{len(params)}...")

        print(f"Uploaded {count}/{len(params)} parameters to Drone {drone_id}")
        conn.close()
        return count == len(params)

    def generate_all(self):
        """Generate everything needed for fleet deployment."""
        print("=" * 60)
        print(f"  Fleet Parameter Replication System")
        print(f"  Target: {self.config['num_drones']} drones")
        print("=" * 60)

        self.load_base_params()
        self.calculate_grid_positions()
        self.generate_param_files()
        self.generate_fleet_manifest()
        self.generate_sitl_launch_script()

        print("\n" + "=" * 60)
        print("  Fleet configuration complete!")
        print(f"  Parameter files: {self.config['output_dir']}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Drone Fleet Parameter Replicator")
    parser.add_argument("--num-drones", type=int, default=150, help="Number of drones")
    parser.add_argument("--config", type=str, help="Config file path")
    parser.add_argument("--columns", type=int, default=15, help="Grid columns")
    parser.add_argument("--spacing", type=float, default=5.0, help="Grid spacing (meters)")
    parser.add_argument("--upload", type=int, help="Upload params to drone ID")
    parser.add_argument("--connection", type=str, help="MAVLink connection string")
    args = parser.parse_args()

    replicator = ParameterReplicator(args.config)
    replicator.config["num_drones"] = args.num_drones
    replicator.config["grid_columns"] = args.columns
    replicator.config["grid_spacing_meters"] = args.spacing

    if args.upload:
        replicator.load_base_params()
        replicator.calculate_grid_positions()
        replicator.generate_param_files()
        conn_str = args.connection or f"tcp:127.0.0.1:{5760 + (args.upload - 1) * 10}"
        replicator.upload_params_to_drone(args.upload, conn_str)
    else:
        replicator.generate_all()


if __name__ == "__main__":
    main()
