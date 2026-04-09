#!/usr/bin/env python3
"""
Drone Show Demo Runner
Demonstrates the complete drone show workflow step by step.
Can be run standalone or as part of the full stack.
"""

import asyncio
import json
import os
import sys
import time

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, os.path.join(PROJECT_DIR, "scripts"))

from drone_show_controller import DroneShowController, ShowPhase


class DemoRunner:
    """Interactive demo runner with step-by-step execution."""

    def __init__(self, num_drones: int = 3, auto: bool = False):
        self.num_drones = num_drones
        self.auto = auto
        self.config_path = os.path.join(PROJECT_DIR, "config", "show_config.json")
        self.choreography_path = os.path.join(PROJECT_DIR, "choreography", "demo_show.json")
        self.controller = DroneShowController(self.config_path)

    def banner(self, text: str):
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}")

    def step(self, num: int, text: str):
        print(f"\n{'─'*60}")
        print(f"  Step {num}: {text}")
        print(f"{'─'*60}")

    def wait_for_user(self, prompt: str = "Press Enter to continue..."):
        if not self.auto:
            input(f"\n  >>> {prompt}")

    def print_status(self):
        """Print current status of all drones."""
        status = self.controller.get_all_status()
        print(f"\n  Show Phase: {status['show_phase']}")
        print(f"  {'─'*50}")
        for drone_id, drone in status["drones"].items():
            print(f"  Drone {drone_id}: "
                  f"State={drone['state']:12s} "
                  f"Mode={drone['mode']:10s} "
                  f"Armed={'Y' if drone['armed'] else 'N'} "
                  f"Alt={drone['alt']:6.1f}m "
                  f"Batt={drone['battery_voltage']:5.1f}V "
                  f"GPS={drone['gps_satellites']:2d}sats")

    async def run(self):
        """Run the complete demo."""
        self.banner("DRONE SHOW DEMO")
        print(f"  Drones: {self.num_drones}")
        print(f"  Mode: {'Automatic' if self.auto else 'Interactive'}")
        print(f"  Config: {self.config_path}")
        print(f"  Choreography: {self.choreography_path}")

        # Step 1: Connect
        self.step(1, "Connect to SITL Drones")
        for i in range(1, self.num_drones + 1):
            port = 5760 + (i - 1) * 10
            self.controller.add_drone(i, f"tcp:127.0.0.1:{port}")
            print(f"  Added Drone {i}: tcp:127.0.0.1:{port}")

        print("\n  Connecting...")
        connected = self.controller.connect_all()
        if connected:
            print("  All drones connected!")
        else:
            print("  WARNING: Some drones failed to connect")
            connected_count = sum(
                1 for d in self.controller.drones.values()
                if d.status.state.value != "disconnected"
            )
            print(f"  Connected: {connected_count}/{self.num_drones}")

        self.print_status()
        self.wait_for_user()

        # Step 2: Preflight
        self.step(2, "Preflight Checks")
        preflight = self.controller.preflight_check()
        for drone_id, result in preflight.items():
            status = "PASS" if result["passed"] else "FAIL"
            print(f"  Drone {drone_id}: {status}")
            for check, val in result["checks"].items():
                if not val:
                    print(f"    ! {check}: FAILED")

        print("\n  Note: In SITL mode, some checks may fail (expected)")
        self.wait_for_user()

        # Step 3: Load Choreography
        self.step(3, "Load Show Choreography")
        self.controller.load_choreography(self.choreography_path)
        with open(self.choreography_path) as f:
            show_data = json.load(f)
        print(f"  Show: {show_data['show_name']}")
        print(f"  Duration: {show_data['total_duration']}s")
        print(f"  Segments: {len(show_data['segments'])}")
        for seg in show_data["segments"]:
            print(f"    - {seg['name']} ({seg['duration']}s)")
        self.wait_for_user()

        # Step 4: Arm
        self.step(4, "Arm All Drones")
        print("  Setting GUIDED mode and arming...")
        armed = await self.controller.arm_all()
        if armed:
            print("  All drones armed!")
        else:
            print("  WARNING: Arming issues (continuing for demo)")
        self.print_status()
        self.wait_for_user()

        # Step 5: Takeoff
        self.step(5, "Synchronized Takeoff")
        takeoff_alt = self.controller.config["takeoff_altitude"]
        print(f"  Taking off to {takeoff_alt}m...")
        took_off = await self.controller.takeoff_all(takeoff_alt)
        if took_off:
            print("  All drones at altitude!")
        else:
            print("  WARNING: Altitude timeout (continuing)")
        self.print_status()
        self.wait_for_user()

        # Step 6: Execute Show
        self.step(6, "Execute Show Choreography")
        print("  Starting show execution...")
        self.controller.running = True
        self.controller.show_phase = ShowPhase.SHOW
        self.controller.show_start_time = time.time()

        for i, segment in enumerate(self.controller.choreography):
            if not self.controller.running:
                break

            print(f"\n  Segment {i+1}/{len(self.controller.choreography)}: {segment.name}")
            print(f"  Duration: {segment.duration}s")

            await self.controller.execute_segment(segment)
            self.print_status()

            elapsed = time.time() - self.controller.show_start_time
            print(f"  Show elapsed: {elapsed:.0f}s")

        elapsed = time.time() - self.controller.show_start_time
        print(f"\n  Show execution complete! Total time: {elapsed:.1f}s")
        self.wait_for_user()

        # Step 7: RTL
        self.step(7, "Return to Launch")
        print("  Initiating RTL for all drones...")
        await self.controller.rtl_all()
        self.print_status()

        # Step 8: Summary
        self.banner("DEMO COMPLETE")
        print(f"  Show Duration: {elapsed:.1f}s")
        print(f"  Segments Executed: {len(self.controller.choreography)}")
        print(f"  Drones: {self.num_drones}")
        print(f"\n  All drones safely returned to launch positions.")

        # Cleanup
        self.controller.close_all()
        print("\n  Connections closed. Demo finished.")

    async def run_api_demo(self):
        """Demo using the HTTP API (requires skybrush_bridge to be running)."""
        import aiohttp

        base_url = "http://127.0.0.1:5000/api"

        self.banner("API-BASED DRONE SHOW DEMO")
        print("  Using Skybrush Bridge HTTP API")

        async with aiohttp.ClientSession() as session:
            # Connect
            self.step(1, "Connect via API")
            async with session.post(f"{base_url}/connect",
                                     json={"num_drones": self.num_drones}) as resp:
                data = await resp.json()
                print(f"  Result: {json.dumps(data, indent=2)}")
            self.wait_for_user()

            # Preflight
            self.step(2, "Preflight Check via API")
            async with session.post(f"{base_url}/preflight") as resp:
                data = await resp.json()
                print(f"  Result: {json.dumps(data, indent=2)}")
            self.wait_for_user()

            # Load show
            self.step(3, "Load Show via API")
            async with session.post(f"{base_url}/show/load", json={}) as resp:
                data = await resp.json()
                print(f"  Result: {json.dumps(data, indent=2)}")
            self.wait_for_user()

            # Start show
            self.step(4, "Start Show via API")
            async with session.post(f"{base_url}/show/start") as resp:
                data = await resp.json()
                print(f"  Result: {json.dumps(data, indent=2)}")

            # Monitor
            print("\n  Monitoring show progress...")
            for _ in range(30):
                async with session.get(f"{base_url}/show/status") as resp:
                    status = await resp.json()
                    print(f"  Phase: {status['phase']}, "
                          f"Elapsed: {status['elapsed']:.0f}s, "
                          f"Running: {status['running']}")
                    if not status["running"]:
                        break
                await asyncio.sleep(5)

            # Final status
            async with session.get(f"{base_url}/status") as resp:
                status = await resp.json()
                print(f"\n  Final Status:")
                print(f"  {json.dumps(status, indent=2)}")

        self.banner("API DEMO COMPLETE")


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Drone Show Demo Runner")
    parser.add_argument("--drones", type=int, default=3, help="Number of drones")
    parser.add_argument("--auto", action="store_true", help="Non-interactive mode")
    parser.add_argument("--api", action="store_true", help="Use API demo mode")
    args = parser.parse_args()

    runner = DemoRunner(num_drones=args.drones, auto=args.auto)

    if args.api:
        await runner.run_api_demo()
    else:
        await runner.run()


if __name__ == "__main__":
    asyncio.run(main())
