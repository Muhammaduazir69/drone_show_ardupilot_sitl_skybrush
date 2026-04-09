#!/bin/bash
# ============================================================
# Launch ArduPilot SITL Instances for Drone Show
# Creates 3 simulated drones with unique SYSID and GPS positions
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Configuration
NUM_DRONES=${1:-3}
BASE_LAT=47.397742
BASE_LON=8.545594
BASE_ALT=488.0
DRONE_SPACING=0.00005  # ~5.5m spacing between drones

# Base ports
BASE_MASTER_PORT=5760
BASE_SITL_PORT=5501
BASE_OUT_PORT=14550

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Drone Show SITL Launcher${NC}"
echo -e "${GREEN}  Launching $NUM_DRONES drones${NC}"
echo -e "${GREEN}============================================${NC}"

# Create log directory
mkdir -p "$LOG_DIR"

# Kill any existing SITL instances
echo -e "${YELLOW}Cleaning up existing SITL instances...${NC}"
pkill -f "arducopter" 2>/dev/null || true
pkill -f "mavproxy" 2>/dev/null || true
sleep 2

# Function to calculate GPS offset for each drone
calc_gps_position() {
    local drone_id=$1
    local row=$((drone_id / 5))
    local col=$((drone_id % 5))
    local lat=$(echo "$BASE_LAT + ($row * $DRONE_SPACING)" | bc -l)
    local lon=$(echo "$BASE_LON + ($col * $DRONE_SPACING)" | bc -l)
    echo "$lat,$lon,$BASE_ALT,0"
}

# Launch each drone SITL instance
declare -a PIDS=()

for i in $(seq 1 $NUM_DRONES); do
    echo -e "${BLUE}--- Launching Drone $i ---${NC}"

    SYSID=$i
    MASTER_PORT=$((BASE_MASTER_PORT + (i - 1) * 10))
    SITL_PORT=$((BASE_SITL_PORT + (i - 1) * 10))
    OUT_PORT=$((BASE_OUT_PORT + (i - 1)))

    # Calculate GPS home position
    HOME_POS=$(calc_gps_position $((i - 1)))

    echo -e "  SYSID: ${GREEN}$SYSID${NC}"
    echo -e "  Master Port: ${GREEN}$MASTER_PORT${NC}"
    echo -e "  SITL Port: ${GREEN}$SITL_PORT${NC}"
    echo -e "  Output Port: ${GREEN}$OUT_PORT${NC}"
    echo -e "  Home Position: ${GREEN}$HOME_POS${NC}"

    # Launch SITL using dronekit-sitl
    dronekit-sitl copter \
        --home="$HOME_POS" \
        --instance $((i - 1)) \
        -I $((i - 1)) \
        --sysid $SYSID \
        > "$LOG_DIR/sitl_drone${i}.log" 2>&1 &
    PIDS+=($!)

    echo -e "  PID: ${GREEN}${PIDS[-1]}${NC}"
    sleep 2

    echo -e "${GREEN}  Drone $i SITL started${NC}"
done

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  All $NUM_DRONES SITL instances launched!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${YELLOW}Connection strings:${NC}"
for i in $(seq 1 $NUM_DRONES); do
    PORT=$((BASE_MASTER_PORT + (i - 1) * 10))
    echo -e "  Drone $i: tcp:127.0.0.1:$PORT"
done

echo ""
echo -e "${YELLOW}To connect MAVProxy to all drones:${NC}"
echo -e "  python3 scripts/mavproxy_multi.py"

echo ""
echo -e "${YELLOW}PIDs: ${PIDS[*]}${NC}"
echo "${PIDS[*]}" > "$LOG_DIR/sitl_pids.txt"

# Wait for all processes
echo -e "${YELLOW}Press Ctrl+C to stop all SITL instances${NC}"
trap "echo 'Stopping all SITL instances...'; kill ${PIDS[*]} 2>/dev/null; exit 0" SIGINT SIGTERM
wait
