#!/bin/bash
# ============================================================
# Master Launch Script - Drone Show Complete Stack
# Launches Enhanced SITL + Skybrush Bridge + Dashboard
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
PYTHON="$VENV_DIR/bin/python3"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

NUM_DRONES=${1:-3}
SKYBRUSH_PORT=5000

echo -e "${CYAN}"
echo "  ======================================"
echo "   DRONE SHOW - COMPLETE STACK LAUNCHER"
echo "   Drones: $NUM_DRONES (Enhanced SITL)"
echo "  ======================================"
echo -e "${NC}"

mkdir -p "$LOG_DIR"

# Step 1: Cleanup
echo -e "${YELLOW}[1/3] Cleaning up...${NC}"
pkill -f "enhanced_sitl" 2>/dev/null || true
pkill -f "skybrush_bridge" 2>/dev/null || true
sleep 2

# Step 2: Launch Enhanced SITL
echo -e "${BLUE}[2/3] Launching Enhanced SITL ($NUM_DRONES drones)...${NC}"
"$PYTHON" "$SCRIPT_DIR/enhanced_sitl.py" --drones "$NUM_DRONES" \
    > "$LOG_DIR/enhanced_sitl.log" 2>&1 &
SITL_PID=$!
echo -e "  SITL PID: $SITL_PID"
sleep 3

# Step 3: Launch Skybrush Bridge
echo -e "${BLUE}[3/3] Launching Skybrush Bridge on port $SKYBRUSH_PORT...${NC}"
"$PYTHON" "$SCRIPT_DIR/skybrush_bridge.py" \
    > "$LOG_DIR/skybrush_bridge.log" 2>&1 &
BRIDGE_PID=$!
echo -e "  Bridge PID: $BRIDGE_PID"
sleep 3

echo ""
echo -e "${GREEN}======================================"
echo -e "  DRONE SHOW STACK READY"
echo -e "======================================${NC}"
echo ""
echo -e "${CYAN}SITL Drones (Enhanced - Full Simulation):${NC}"
for i in $(seq 1 $NUM_DRONES); do
    PORT=$((5760 + (i - 1) * 10))
    echo -e "  Drone $i: tcp:127.0.0.1:$PORT"
done
echo ""
echo -e "${CYAN}Skybrush Bridge:${NC}"
echo -e "  Dashboard:  ${GREEN}http://127.0.0.1:$SKYBRUSH_PORT/${NC}"
echo -e "  API:        http://127.0.0.1:$SKYBRUSH_PORT/api/status"
echo -e "  WebSocket:  ws://127.0.0.1:$SKYBRUSH_PORT/ws"
echo ""
echo -e "${CYAN}Quick Start:${NC}"
echo -e "  1. Open dashboard: ${GREEN}http://127.0.0.1:$SKYBRUSH_PORT/${NC}"
echo -e "  2. Click 'Connect Drones'     -> connects to all SITL drones"
echo -e "  3. Click 'Preflight Check'    -> all checks should PASS"
echo -e "  4. Click 'Load Show'          -> loads 6-segment choreography"
echo -e "  5. Click 'Arm All'            -> arms all drones"
echo -e "  6. Click 'Takeoff'            -> synchronized takeoff to 10m"
echo -e "  7. Click 'START SHOW'         -> executes choreography"
echo -e "  8. Click 'Return to Launch'   -> RTL all drones"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

ALL_PIDS=("$SITL_PID" "$BRIDGE_PID")
echo "${ALL_PIDS[*]}" > "$LOG_DIR/all_pids.txt"

cleanup() {
    echo -e "\n${RED}Shutting down...${NC}"
    kill "${ALL_PIDS[@]}" 2>/dev/null || true
    pkill -f "enhanced_sitl" 2>/dev/null || true
    pkill -f "skybrush_bridge" 2>/dev/null || true
    echo -e "${GREEN}Done${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM
wait
