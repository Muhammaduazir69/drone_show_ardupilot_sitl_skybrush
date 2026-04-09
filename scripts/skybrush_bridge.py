#!/usr/bin/env python3
"""
Skybrush-ArduPilot Integration Bridge
Provides a Skybrush-compatible server that interfaces with ArduPilot
drones via MAVLink for drone show orchestration.

This bridge implements the Skybrush Live protocol endpoints for:
- Drone discovery and status
- Show upload and execution
- Real-time telemetry streaming
- Emergency controls
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime

from aiohttp import web
import websockets

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, os.path.join(PROJECT_DIR, "scripts"))

from drone_show_controller import DroneShowController, DroneState, ShowPhase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(PROJECT_DIR, "logs", "skybrush_bridge.log")),
    ],
)
logger = logging.getLogger("SkybrushBridge")


class SkybrushBridge:
    """
    Bridge between Skybrush Live and ArduPilot SITL drones.
    Exposes HTTP REST API + WebSocket for real-time telemetry.
    """

    def __init__(self, config_path: str = None):
        self.controller = DroneShowController(config_path)
        self.app = web.Application()
        self.ws_clients: set = set()
        self.telemetry_task = None
        self.show_loaded = False
        self.show_file = None

        self._setup_routes()

    def _setup_routes(self):
        """Register HTTP API routes."""
        self.app.router.add_get("/api/status", self.handle_status)
        self.app.router.add_get("/api/drones", self.handle_drones)
        self.app.router.add_get("/api/drones/{drone_id}", self.handle_drone_detail)
        self.app.router.add_post("/api/connect", self.handle_connect)
        self.app.router.add_post("/api/show/load", self.handle_load_show)
        self.app.router.add_post("/api/show/start", self.handle_start_show)
        self.app.router.add_post("/api/show/stop", self.handle_stop_show)
        self.app.router.add_post("/api/emergency", self.handle_emergency)
        self.app.router.add_post("/api/arm", self.handle_arm_all)
        self.app.router.add_post("/api/takeoff", self.handle_takeoff)
        self.app.router.add_post("/api/rtl", self.handle_rtl)
        self.app.router.add_post("/api/land", self.handle_land)
        self.app.router.add_post("/api/preflight", self.handle_preflight)
        self.app.router.add_get("/api/show/status", self.handle_show_status)
        self.app.router.add_get("/api/config", self.handle_get_config)
        self.app.router.add_post("/api/params/upload", self.handle_upload_params)
        self.app.router.add_get("/ws", self.handle_websocket)

        # Serve static files for web dashboard
        static_dir = os.path.join(PROJECT_DIR, "monitoring", "static")
        if os.path.exists(static_dir):
            self.app.router.add_static("/static/", static_dir)
        self.app.router.add_get("/", self.handle_dashboard)
        self.app.router.add_get("/viz", self.handle_visualization)

    async def handle_dashboard(self, request):
        """Serve the monitoring dashboard."""
        dashboard_path = os.path.join(PROJECT_DIR, "monitoring", "dashboard.html")
        if os.path.exists(dashboard_path):
            return web.FileResponse(dashboard_path)
        return web.Response(text="Dashboard not found", status=404)

    async def handle_visualization(self, request):
        """Serve the 3D visualization page."""
        viz_path = os.path.join(PROJECT_DIR, "monitoring", "visualization.html")
        if os.path.exists(viz_path):
            return web.FileResponse(viz_path)
        return web.Response(text="Visualization not found", status=404)

    async def handle_status(self, request):
        """Get overall system status."""
        status = self.controller.get_all_status()
        status["server_time"] = datetime.now().isoformat()
        status["show_loaded"] = self.show_loaded
        status["show_file"] = self.show_file
        return web.json_response(status)

    async def handle_drones(self, request):
        """Get status of all drones."""
        status = self.controller.get_all_status()
        return web.json_response(status["drones"])

    async def handle_drone_detail(self, request):
        """Get detailed status of a specific drone."""
        drone_id = int(request.match_info["drone_id"])
        status = self.controller.get_all_status()
        if str(drone_id) in status["drones"] or drone_id in status["drones"]:
            drone_status = status["drones"].get(drone_id, status["drones"].get(str(drone_id)))
            return web.json_response(drone_status)
        return web.json_response({"error": "Drone not found"}, status=404)

    async def handle_connect(self, request):
        """Connect to all configured drones."""
        data = await request.json() if request.can_read_body else {}
        num_drones = data.get("num_drones", self.controller.config["num_drones"])

        # Add drones if not already added
        if not self.controller.drones:
            for i in range(1, num_drones + 1):
                port = self.controller.config["base_port"] + (i - 1) * 10
                self.controller.add_drone(i, f"tcp:127.0.0.1:{port}")

        success = self.controller.connect_all()
        return web.json_response({
            "success": success,
            "connected": sum(
                1 for d in self.controller.drones.values()
                if d.status.state.value != "disconnected"
            ),
            "total": len(self.controller.drones),
        })

    async def handle_load_show(self, request):
        """Load a choreography file."""
        data = await request.json()
        show_file = data.get("file", os.path.join(
            PROJECT_DIR, "choreography", "demo_show.json"
        ))

        try:
            self.controller.load_choreography(show_file)
            self.show_loaded = True
            self.show_file = show_file
            return web.json_response({
                "success": True,
                "segments": len(self.controller.choreography),
                "file": show_file,
            })
        except Exception as e:
            return web.json_response({"success": False, "error": str(e)}, status=400)

    async def handle_start_show(self, request):
        """Start the drone show.

        Assumes drones are already connected, armed, and airborne
        (via the /api/connect, /api/arm, and /api/takeoff endpoints).
        This only executes the choreography segments followed by RTL.
        """
        if not self.show_loaded:
            return web.json_response(
                {"success": False, "error": "No show loaded"}, status=400
            )

        # Verify drones are connected
        if not self.controller.drones:
            return web.json_response(
                {"success": False, "error": "No drones connected"}, status=400
            )

        connected = sum(
            1 for d in self.controller.drones.values()
            if d.status.state != DroneState.DISCONNECTED
        )
        if connected == 0:
            return web.json_response(
                {"success": False, "error": "No drones connected"}, status=400
            )

        # Set up show state
        self.controller.running = True
        self.controller.show_phase = ShowPhase.SHOW
        self.controller.show_start_time = time.time()

        # Execute choreography in background, then RTL
        async def _run_show_task():
            try:
                await self.controller.execute_show()
                await self.controller.rtl_all()
            except Exception as e:
                logger.error(f"Show execution error: {e}")
                await self.controller.emergency_stop()
            finally:
                self.controller.running = False

        asyncio.create_task(_run_show_task())
        return web.json_response({"success": True, "message": "Show starting"})

    async def handle_stop_show(self, request):
        """Stop the show and RTL."""
        self.controller.running = False
        await self.controller.rtl_all()
        return web.json_response({"success": True, "message": "Show stopped, RTL initiated"})

    async def handle_emergency(self, request):
        """Emergency stop - land all drones immediately."""
        await self.controller.emergency_stop()
        return web.json_response({"success": True, "message": "EMERGENCY STOP"})

    async def handle_arm_all(self, request):
        """Arm all drones."""
        success = await self.controller.arm_all()
        # Allow state to propagate so subsequent status queries reflect armed state
        await asyncio.sleep(1)
        return web.json_response({"success": success})

    async def handle_takeoff(self, request):
        """Takeoff all drones."""
        data = await request.json() if request.can_read_body else {}
        altitude = data.get("altitude", self.controller.config["takeoff_altitude"])
        success = await self.controller.takeoff_all(altitude)
        # Allow state to propagate so subsequent status queries reflect airborne state
        await asyncio.sleep(1)
        return web.json_response({"success": success})

    async def handle_rtl(self, request):
        """Return all drones to launch."""
        await self.controller.rtl_all()
        return web.json_response({"success": True})

    async def handle_land(self, request):
        """Land all drones at current position."""
        for drone in self.controller.drones.values():
            drone.land()
        return web.json_response({"success": True})

    async def handle_preflight(self, request):
        """Run preflight checks."""
        results = self.controller.preflight_check()
        serializable = {}
        for drone_id, result in results.items():
            serializable[drone_id] = {
                "passed": result["passed"],
                "checks": result["checks"],
            }
        return web.json_response(serializable)

    async def handle_show_status(self, request):
        """Get current show execution status."""
        return web.json_response({
            "phase": self.controller.show_phase.value,
            "running": self.controller.running,
            "show_loaded": self.show_loaded,
            "elapsed": (
                time.time() - self.controller.show_start_time
                if self.controller.show_start_time
                else 0
            ),
        })

    async def handle_get_config(self, request):
        """Get current configuration."""
        return web.json_response(self.controller.config)

    async def handle_upload_params(self, request):
        """Upload parameters to a drone."""
        data = await request.json()
        drone_id = data.get("drone_id")
        params = data.get("params", {})

        if drone_id not in self.controller.drones:
            return web.json_response({"error": "Drone not found"}, status=404)

        drone = self.controller.drones[drone_id]
        for param_name, param_value in params.items():
            drone.connection.mav.param_set_send(
                drone.connection.target_system,
                drone.connection.target_component,
                param_name.encode("utf-8"),
                float(param_value),
                mavutil.mavlink.MAV_PARAM_TYPE_REAL32,
            )

        return web.json_response({"success": True, "params_set": len(params)})

    async def handle_websocket(self, request):
        """WebSocket handler for real-time telemetry streaming."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.ws_clients.add(ws)
        logger.info(f"WebSocket client connected ({len(self.ws_clients)} total)")

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data.get("type") == "command":
                        await self._handle_ws_command(data, ws)
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")
        finally:
            self.ws_clients.discard(ws)
            logger.info(f"WebSocket client disconnected ({len(self.ws_clients)} total)")

        return ws

    async def _handle_ws_command(self, data: dict, ws):
        """Handle commands received via WebSocket."""
        cmd = data.get("command")
        if cmd == "emergency_stop":
            await self.controller.emergency_stop()
        elif cmd == "rtl":
            await self.controller.rtl_all()

    async def _broadcast_telemetry(self):
        """Broadcast telemetry to all WebSocket clients."""
        while True:
            if self.ws_clients:
                status = self.controller.get_all_status()
                status["timestamp"] = time.time()
                message = json.dumps(status)

                dead_clients = set()
                for ws in self.ws_clients:
                    try:
                        await ws.send_str(message)
                    except Exception:
                        dead_clients.add(ws)
                self.ws_clients -= dead_clients

            await asyncio.sleep(0.2)  # 5Hz telemetry update

    async def start(self, host: str = "0.0.0.0", port: int = 5000):
        """Start the Skybrush bridge server."""
        logger.info(f"Starting Skybrush Bridge on {host}:{port}")

        # Start telemetry broadcast
        self.telemetry_task = asyncio.create_task(self._broadcast_telemetry())

        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()

        logger.info(f"Skybrush Bridge running at http://{host}:{port}")
        logger.info(f"Dashboard: http://{host}:{port}/")
        logger.info(f"API: http://{host}:{port}/api/status")
        logger.info(f"WebSocket: ws://{host}:{port}/ws")

        # Keep running
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            pass
        finally:
            if self.telemetry_task:
                self.telemetry_task.cancel()
            self.controller.close_all()
            await runner.cleanup()


async def main():
    config_path = os.path.join(PROJECT_DIR, "config", "show_config.json")
    bridge = SkybrushBridge(config_path)
    await bridge.start()


if __name__ == "__main__":
    asyncio.run(main())
