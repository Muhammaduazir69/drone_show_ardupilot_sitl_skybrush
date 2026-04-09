# Drone Show System — ArduPilot SITL + Skybrush Integration

A complete drone show orchestration system built on ArduPilot with Skybrush-compatible integration, featuring 3D real-time visualization, synchronized multi-drone choreography, and fleet scaling to 150+ drones.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![ArduPilot](https://img.shields.io/badge/ArduPilot-Copter%204.5%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Demo Video

[![Drone Show 3D Visualization Demo](https://img.shields.io/badge/Watch%20Demo-Google%20Drive-blue?style=for-the-badge&logo=googledrive)](https://drive.google.com/file/d/1zMQdsiwkGdwgGaSi0yXbzXsSpRS7KGAZ/view?usp=sharing)

**[Watch the full demo video here](https://drive.google.com/file/d/1zMQdsiwkGdwgGaSi0yXbzXsSpRS7KGAZ/view?usp=sharing)** — Real-time 3D visualization showing 3 drones performing synchronized formations (Triangle, Line, Vertical Stack), live telemetry (GPS, battery, altitude, speed), Skybrush bridge integration, and the complete show workflow from preflight checks through choreography execution to RTL landing.

---

## Features

- **Full ArduPilot SITL Simulation** — Enhanced simulator with complete sensor emulation (GPS 3D fix, 14 satellites, battery model, EKF status, MAVLink telemetry)
- **Skybrush-Compatible Bridge** — HTTP REST API + WebSocket server implementing Skybrush Live protocol endpoints for drone discovery, show upload, execution, and monitoring
- **3D Real-Time Visualization** — Three.js WebGL dashboard with orbit camera, drone models with spinning rotors, LED glow effects, flight trails, and formation tracking
- **Synchronized Choreography** — 6-segment demo show: Triangle, Rise, Line, Vertical Stack, Expanding Triangle, Finale — with per-drone waypoint sequencing
- **128-Parameter ArduPilot Configuration** — Production-ready parameter sets covering EKF3, GPS/RTK, geofence, failsafes, motor tuning, position controller, and flight modes
- **Fleet Scaling System** — Automated parameter replication generating unique configs for 150 drones with GPS grid positioning and fleet manifests
- **Comprehensive Safety Stack** — Layered failsafes (GCS loss, EKF degradation, battery cascade, geofence breach), emergency stop, preflight checklist
- **ESC & Sensor Calibration** — Automated scripts for accelerometer, gyroscope, compass, barometer, and ESC parameter deployment

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              3D Visualization (Three.js WebGL)              │
│         Real-time drone positions, trails, formations       │
│                    http://host:5000/viz                      │
├─────────────────────────────────────────────────────────────┤
│                   Skybrush Bridge Server                     │
│          HTTP REST API (15+ endpoints) + WebSocket           │
│                      Port 5000                               │
├─────────────────────────────────────────────────────────────┤
│                 Drone Show Controller                        │
│    Orchestration · Choreography · Safety · Monitoring        │
├───────────┬───────────┬───────────┬─────────────────────────┤
│  Drone 1  │  Drone 2  │  Drone 3  │  ... Drone N            │
│   :5760   │   :5770   │   :5780   │  :5760+(N-1)*10         │
│  SYSID=1  │  SYSID=2  │  SYSID=3  │  SYSID=N               │
└───────────┴───────────┴───────────┴─────────────────────────┘
      Enhanced SITL Instances (MAVLink over TCP)
```

---

## Quick Start

### Prerequisites

```bash
# Python 3.10+ required
python3 --version

# Clone the repository
git clone https://github.com/Muhammaduazir69/drone_show_ardupilot_sitl_skybrush.git
cd drone_show_ardupilot_sitl_skybrush
```

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install pymavlink MAVProxy dronekit dronekit-sitl
pip install flask flask-socketio aiohttp websockets geopy numpy scipy requests pyyaml jsonschema
```

### Launch

```bash
# Option 1: Master launch script (starts everything)
./scripts/launch_all.sh 3

# Option 2: Manual launch
source venv/bin/activate

# Terminal 1 — SITL (3 drones with full sensor simulation)
python3 scripts/enhanced_sitl.py --drones 3

# Terminal 2 — Skybrush Bridge + Dashboard
python3 scripts/skybrush_bridge.py
```

### Open in Browser

| Page | URL | Description |
|------|-----|-------------|
| **3D Visualization** | `http://127.0.0.1:5000/viz` | Real-time 3D drone view with formations |
| **Control Dashboard** | `http://127.0.0.1:5000/` | Telemetry panels + controls |

### Run the Demo Show

1. Open `http://127.0.0.1:5000/viz`
2. **Connect** — links to all SITL drones
3. **Preflight Check** — validates GPS, EKF, battery, parameters
4. **Load Show** — loads 6-segment choreography
5. **Arm All** — rotors spin up
6. **Takeoff** — synchronized climb to 10m
7. **START SHOW** — executes formations (Triangle → Line → Stack → Finale)
8. **RTL** — all drones return home and land

---

## Project Structure

```
├── config/
│   ├── show_config.json                  # Master show configuration
│   ├── drone_params/
│   │   ├── drone_show_base.param         # 128 ArduPilot parameters (base template)
│   │   ├── drone1.param                  # Drone 1 overrides (SYSID=1)
│   │   ├── drone2.param                  # Drone 2 overrides (SYSID=2)
│   │   └── drone3.param                  # Drone 3 overrides (SYSID=3)
│   └── show_params/
│       ├── geofence_show.param           # Geofence: 300m radius, 120m alt
│       ├── safety_show.param             # Failsafe chain configuration
│       └── rtk_gps.param                # RTK GPS + EKF precision tuning
│
├── choreography/
│   └── demo_show.json                    # 6-segment formation choreography
│
├── scripts/
│   ├── enhanced_sitl.py                  # Full-sensor SITL simulator
│   ├── drone_show_controller.py          # Core orchestration engine
│   ├── skybrush_bridge.py                # HTTP/WebSocket bridge server
│   ├── launch_all.sh                     # Master launch script
│   ├── launch_sitl.sh                    # SITL-only launcher
│   ├── launch_sitl_proper.py             # Python SITL launcher + tester
│   ├── launch_fleet_sitl.sh              # 150-drone fleet launcher
│   ├── mavproxy_multi.py                 # MAVProxy multi-drone manager
│   ├── param_replicator.py              # Fleet parameter generator
│   ├── esc_calibration.py                # ESC calibration deployment
│   ├── sensor_calibration.py             # IMU/compass/baro calibration
│   ├── preflight_checklist.py            # Pre-show GO/NO-GO validation
│   └── run_demo.py                       # Interactive demo runner
│
├── monitoring/
│   ├── dashboard.html                    # Telemetry control dashboard
│   └── visualization.html                # Three.js 3D visualization
│
├── logs/                                 # Runtime logs (git-ignored)
└── templates/                            # Show templates
```

---

## ArduPilot Parameters

### Base Configuration (128 parameters)

The `drone_show_base.param` template covers every parameter group required for drone show operations:

| Category | Key Parameters | Purpose |
|----------|---------------|---------|
| **EKF3** | `EK3_ENABLE`, `EK3_GPS_TYPE`, `EK3_POSNE_M_NSE`, `EK3_SRC1_POSXY` | Navigation filter with GPS source, tuned noise for show precision |
| **GPS/RTK** | `GPS_TYPE`, `GPS_NAVFILTER`, `GPS_INJECT_TO`, `GPS_AUTO_SWITCH` | RTK injection, DGPS, blending for cm-level accuracy |
| **Geofence** | `FENCE_ENABLE`, `FENCE_TYPE=7`, `FENCE_ALT_MAX=120`, `FENCE_RADIUS=300` | Altitude + circle + polygon boundary enforcement |
| **Failsafes** | `FS_THR_ENABLE`, `FS_GCS_ENABLE=2`, `FS_EKF_ACTION`, `BATT_FS_*` | Throttle, GCS loss (SmartRTL), EKF degradation, battery cascade |
| **Battery** | `BATT_LOW_VOLT=14.0`, `BATT_CRT_VOLT=13.2`, `BATT_FS_LOW_ACT=2` | 4S LiPo monitoring with RTL/Land cascade |
| **Position** | `WPNAV_SPEED=500`, `WPNAV_ACCEL=100`, `PSC_POSXY_P`, `PSC_VELXY_P/I/D` | Waypoint navigation and position hold tuning |
| **Motors** | `MOT_SPIN_ARM=0.1`, `MOT_THST_EXPO=0.65`, `MOT_THST_HOVER=0.35` | Throttle curve, spin ranges, hover estimate |
| **Flight Modes** | `FLTMODE1-6`: Stabilize, Guided, RTL, Loiter, Land, Auto | Show requires GUIDED (Skybrush), RTL (failsafe) |
| **Safety** | `ARMING_CHECK=1`, `RC8_OPTION=31`, `BRD_SAFETY*` | Pre-arm validation, emergency motor kill channel |
| **Logging** | `LOG_BITMASK=176126`, `LOG_FILE_DSRMROT=1` | Full telemetry logging for post-show analysis |

### Parameter Relationships

These parameters form interdependent systems:

- **EKF ↔ GPS**: `EK3_POSNE_M_NSE` must match GPS accuracy — 0.3m for RTK, 1.0m+ for standard GPS
- **Motor ↔ Battery ↔ Failsafe**: `MOT_BAT_VOLT_MAX/MIN` → `BATT_LOW_VOLT` → `BATT_FS_LOW_ACT` cascade
- **WPNAV ↔ PSC**: `WPNAV_ACCEL` limits how aggressively `PSC_VELXY_P` can respond — tuned together for formation precision without oscillation
- **Geofence ↔ RTL**: `FENCE_ACTION=1` triggers RTL; `RTL_ALT` must be staggered across fleet to prevent collision

---

## Show Choreography Format

Shows are JSON files with segments containing per-drone waypoints:

```json
{
    "show_name": "Demo Formation Show",
    "total_duration": 180,
    "segments": [
        {
            "name": "Formation: Triangle",
            "duration": 30,
            "waypoints": {
                "1": [{ "lat": 47.397792, "lon": 8.545594, "alt": 15.0, "speed": 2.0,
                         "yaw": 180, "led_color": [255, 0, 0] }],
                "2": [{ "lat": 47.397717, "lon": 8.545494, "alt": 15.0, "speed": 2.0,
                         "yaw": 60, "led_color": [0, 255, 0] }],
                "3": [{ "lat": 47.397717, "lon": 8.545694, "alt": 15.0, "speed": 2.0,
                         "yaw": 300, "led_color": [0, 0, 255] }]
            }
        }
    ]
}
```

### Demo Show Segments

| # | Formation | Duration | Description |
|---|-----------|----------|-------------|
| 1 | Triangle | 30s | Equilateral triangle at 15m |
| 2 | Rise | 15s | All drones climb to 25m |
| 3 | Line | 30s | Horizontal line at 25m |
| 4 | Vertical Stack | 30s | Stacked at 15/25/35m |
| 5 | Expanding Triangle | 30s | Wide triangle at 20m |
| 6 | Finale | 25s | Converge to center at 10m |

---

## API Reference

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | System status + all drone telemetry |
| `/api/drones` | GET | All drone positions and states |
| `/api/drones/{id}` | GET | Single drone detail |
| `/api/connect` | POST | Connect to SITL drones |
| `/api/preflight` | POST | Run GO/NO-GO checks |
| `/api/show/load` | POST | Load choreography file |
| `/api/show/start` | POST | Execute show (choreography only) |
| `/api/show/stop` | POST | Stop show + RTL |
| `/api/show/status` | GET | Current show phase + elapsed time |
| `/api/arm` | POST | Arm all drones |
| `/api/takeoff` | POST | Synchronized takeoff |
| `/api/rtl` | POST | Return to launch |
| `/api/land` | POST | Land at current position |
| `/api/emergency` | POST | Emergency stop (immediate land) |
| `/api/config` | GET | Get current configuration |
| `/api/params/upload` | POST | Upload parameters to a drone |

### WebSocket

```
ws://127.0.0.1:5000/ws
```

5Hz telemetry stream with all drone positions, states, battery, GPS, and show phase.

---

## Scaling to 150 Drones

### Generate Fleet Parameters

```bash
source venv/bin/activate
python3 scripts/param_replicator.py --num-drones 150 --columns 15 --spacing 5.0
```

This generates:
- **150 parameter files** — each with unique `SYSID_THISMAV` (1–150)
- **Fleet manifest** (`fleet_manifest.json`) — GPS grid positions for all drones
- **Fleet launch script** (`launch_fleet_sitl.sh`) — starts all SITL instances

### Grid Layout

```
 15 columns × 10 rows = 150 drones
 5.0m spacing between drones
 Each drone: unique SYSID + calculated GPS home position
```

### Upload to Real Hardware

```bash
python3 scripts/param_replicator.py --upload 1 --connection /dev/ttyUSB0
```

---

## Calibration Scripts

```bash
source venv/bin/activate

# ESC calibration (motor parameters)
python3 scripts/esc_calibration.py 3

# Sensor calibration (accel, gyro, compass, baro)
python3 scripts/sensor_calibration.py 3

# Pre-show checklist (GO/NO-GO)
python3 scripts/preflight_checklist.py 3
```

---

## Enhanced SITL Simulator

The `enhanced_sitl.py` provides a full-featured ArduPilot SITL replacement with:

- **GPS simulation** — 3D fix, 14 satellites, configurable HDOP/VDOP
- **Battery model** — Voltage sag under load, current draw based on throttle, mAh tracking
- **EKF status** — All flags set (attitude, velocity, position horizontal/vertical)
- **Physics engine** — Takeoff, guided navigation, RTL with altitude hold, landing detection
- **MAVLink v1** — Full heartbeat, GLOBAL_POSITION_INT, GPS_RAW_INT, SYS_STATUS, VFR_HUD, EKF_STATUS_REPORT, ATTITUDE
- **Multi-client TCP** — Multiple simultaneous GCS connections per drone

---

## Transitioning to Real Hardware

| Step | Action | Tool |
|------|--------|------|
| 1 | Flash ArduCopter 4.5+ firmware | Mission Planner |
| 2 | Upload `drone_show_base.param` | Mission Planner / MAVProxy |
| 3 | Upload drone-specific params (SYSID) | `param_replicator.py --upload` |
| 4 | Accelerometer calibration (6-position) | Mission Planner |
| 5 | Compass calibration | Mission Planner |
| 6 | ESC calibration | `esc_calibration.py` or Mission Planner |
| 7 | Configure RTK base station | Mission Planner GPS inject |
| 8 | Set polygon geofence around show area | Mission Planner |
| 9 | Verify all failsafes trigger correctly | Manual testing |
| 10 | Update `show_config.json` with real GPS coords | Text editor |
| 11 | Switch connection strings from TCP to serial/UDP | `show_config.json` |
| 12 | Run preflight checklist | `preflight_checklist.py` |

---

## Tech Stack

- **Simulation**: Custom Enhanced SITL with MAVLink TCP server
- **Communication**: pymavlink, MAVProxy, dronekit-python
- **Server**: aiohttp (async HTTP + WebSocket)
- **Visualization**: Three.js r128, OrbitControls, WebGL
- **Orchestration**: Python asyncio
- **Parameters**: ArduCopter 4.5+ compatible `.param` files

---

## License

MIT
