#!/bin/bash
# Auto-generated fleet SITL launch script
# 150 drones

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
source "$PROJECT_DIR/venv/bin/activate"

PIDS=()

# Drone 1 (SYSID=1)
dronekit-sitl copter --home="47.397517422206256,8.545096321391643,488.0,0" --instance 0 -I 0 --sysid 1 > "$PROJECT_DIR/logs/sitl_drone1.log" 2>&1 &
PIDS+=($!)

# Drone 2 (SYSID=2)
dronekit-sitl copter --home="47.397517422206256,8.545162678539423,488.0,0" --instance 1 -I 1 --sysid 2 > "$PROJECT_DIR/logs/sitl_drone2.log" 2>&1 &
PIDS+=($!)

# Drone 3 (SYSID=3)
dronekit-sitl copter --home="47.397517422206256,8.545229035687205,488.0,0" --instance 2 -I 2 --sysid 3 > "$PROJECT_DIR/logs/sitl_drone3.log" 2>&1 &
PIDS+=($!)

# Drone 4 (SYSID=4)
dronekit-sitl copter --home="47.397517422206256,8.545295392834985,488.0,0" --instance 3 -I 3 --sysid 4 > "$PROJECT_DIR/logs/sitl_drone4.log" 2>&1 &
PIDS+=($!)

# Drone 5 (SYSID=5)
dronekit-sitl copter --home="47.397517422206256,8.545361749982767,488.0,0" --instance 4 -I 4 --sysid 5 > "$PROJECT_DIR/logs/sitl_drone5.log" 2>&1 &
PIDS+=($!)

# Drone 6 (SYSID=6)
dronekit-sitl copter --home="47.397517422206256,8.545428107130547,488.0,0" --instance 5 -I 5 --sysid 6 > "$PROJECT_DIR/logs/sitl_drone6.log" 2>&1 &
PIDS+=($!)

# Drone 7 (SYSID=7)
dronekit-sitl copter --home="47.397517422206256,8.545494464278327,488.0,0" --instance 6 -I 6 --sysid 7 > "$PROJECT_DIR/logs/sitl_drone7.log" 2>&1 &
PIDS+=($!)

# Drone 8 (SYSID=8)
dronekit-sitl copter --home="47.397517422206256,8.54556082142611,488.0,0" --instance 7 -I 7 --sysid 8 > "$PROJECT_DIR/logs/sitl_drone8.log" 2>&1 &
PIDS+=($!)

# Drone 9 (SYSID=9)
dronekit-sitl copter --home="47.397517422206256,8.54562717857389,488.0,0" --instance 8 -I 8 --sysid 9 > "$PROJECT_DIR/logs/sitl_drone9.log" 2>&1 &
PIDS+=($!)

# Drone 10 (SYSID=10)
dronekit-sitl copter --home="47.397517422206256,8.545693535721671,488.0,0" --instance 9 -I 9 --sysid 10 > "$PROJECT_DIR/logs/sitl_drone10.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 11 (SYSID=11)
dronekit-sitl copter --home="47.397517422206256,8.545759892869452,488.0,0" --instance 10 -I 10 --sysid 11 > "$PROJECT_DIR/logs/sitl_drone11.log" 2>&1 &
PIDS+=($!)

# Drone 12 (SYSID=12)
dronekit-sitl copter --home="47.397517422206256,8.545826250017232,488.0,0" --instance 11 -I 11 --sysid 12 > "$PROJECT_DIR/logs/sitl_drone12.log" 2>&1 &
PIDS+=($!)

# Drone 13 (SYSID=13)
dronekit-sitl copter --home="47.397517422206256,8.545892607165014,488.0,0" --instance 12 -I 12 --sysid 13 > "$PROJECT_DIR/logs/sitl_drone13.log" 2>&1 &
PIDS+=($!)

# Drone 14 (SYSID=14)
dronekit-sitl copter --home="47.397517422206256,8.545958964312794,488.0,0" --instance 13 -I 13 --sysid 14 > "$PROJECT_DIR/logs/sitl_drone14.log" 2>&1 &
PIDS+=($!)

# Drone 15 (SYSID=15)
dronekit-sitl copter --home="47.397517422206256,8.546025321460576,488.0,0" --instance 14 -I 14 --sysid 15 > "$PROJECT_DIR/logs/sitl_drone15.log" 2>&1 &
PIDS+=($!)

# Drone 16 (SYSID=16)
dronekit-sitl copter --home="47.397562337765,8.545096321391643,488.0,0" --instance 15 -I 15 --sysid 16 > "$PROJECT_DIR/logs/sitl_drone16.log" 2>&1 &
PIDS+=($!)

# Drone 17 (SYSID=17)
dronekit-sitl copter --home="47.397562337765,8.545162678539423,488.0,0" --instance 16 -I 16 --sysid 17 > "$PROJECT_DIR/logs/sitl_drone17.log" 2>&1 &
PIDS+=($!)

# Drone 18 (SYSID=18)
dronekit-sitl copter --home="47.397562337765,8.545229035687205,488.0,0" --instance 17 -I 17 --sysid 18 > "$PROJECT_DIR/logs/sitl_drone18.log" 2>&1 &
PIDS+=($!)

# Drone 19 (SYSID=19)
dronekit-sitl copter --home="47.397562337765,8.545295392834985,488.0,0" --instance 18 -I 18 --sysid 19 > "$PROJECT_DIR/logs/sitl_drone19.log" 2>&1 &
PIDS+=($!)

# Drone 20 (SYSID=20)
dronekit-sitl copter --home="47.397562337765,8.545361749982767,488.0,0" --instance 19 -I 19 --sysid 20 > "$PROJECT_DIR/logs/sitl_drone20.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 21 (SYSID=21)
dronekit-sitl copter --home="47.397562337765,8.545428107130547,488.0,0" --instance 20 -I 20 --sysid 21 > "$PROJECT_DIR/logs/sitl_drone21.log" 2>&1 &
PIDS+=($!)

# Drone 22 (SYSID=22)
dronekit-sitl copter --home="47.397562337765,8.545494464278327,488.0,0" --instance 21 -I 21 --sysid 22 > "$PROJECT_DIR/logs/sitl_drone22.log" 2>&1 &
PIDS+=($!)

# Drone 23 (SYSID=23)
dronekit-sitl copter --home="47.397562337765,8.54556082142611,488.0,0" --instance 22 -I 22 --sysid 23 > "$PROJECT_DIR/logs/sitl_drone23.log" 2>&1 &
PIDS+=($!)

# Drone 24 (SYSID=24)
dronekit-sitl copter --home="47.397562337765,8.54562717857389,488.0,0" --instance 23 -I 23 --sysid 24 > "$PROJECT_DIR/logs/sitl_drone24.log" 2>&1 &
PIDS+=($!)

# Drone 25 (SYSID=25)
dronekit-sitl copter --home="47.397562337765,8.545693535721671,488.0,0" --instance 24 -I 24 --sysid 25 > "$PROJECT_DIR/logs/sitl_drone25.log" 2>&1 &
PIDS+=($!)

# Drone 26 (SYSID=26)
dronekit-sitl copter --home="47.397562337765,8.545759892869452,488.0,0" --instance 25 -I 25 --sysid 26 > "$PROJECT_DIR/logs/sitl_drone26.log" 2>&1 &
PIDS+=($!)

# Drone 27 (SYSID=27)
dronekit-sitl copter --home="47.397562337765,8.545826250017232,488.0,0" --instance 26 -I 26 --sysid 27 > "$PROJECT_DIR/logs/sitl_drone27.log" 2>&1 &
PIDS+=($!)

# Drone 28 (SYSID=28)
dronekit-sitl copter --home="47.397562337765,8.545892607165014,488.0,0" --instance 27 -I 27 --sysid 28 > "$PROJECT_DIR/logs/sitl_drone28.log" 2>&1 &
PIDS+=($!)

# Drone 29 (SYSID=29)
dronekit-sitl copter --home="47.397562337765,8.545958964312794,488.0,0" --instance 28 -I 28 --sysid 29 > "$PROJECT_DIR/logs/sitl_drone29.log" 2>&1 &
PIDS+=($!)

# Drone 30 (SYSID=30)
dronekit-sitl copter --home="47.397562337765,8.546025321460576,488.0,0" --instance 29 -I 29 --sysid 30 > "$PROJECT_DIR/logs/sitl_drone30.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 31 (SYSID=31)
dronekit-sitl copter --home="47.397607253323756,8.545096321391643,488.0,0" --instance 30 -I 30 --sysid 31 > "$PROJECT_DIR/logs/sitl_drone31.log" 2>&1 &
PIDS+=($!)

# Drone 32 (SYSID=32)
dronekit-sitl copter --home="47.397607253323756,8.545162678539423,488.0,0" --instance 31 -I 31 --sysid 32 > "$PROJECT_DIR/logs/sitl_drone32.log" 2>&1 &
PIDS+=($!)

# Drone 33 (SYSID=33)
dronekit-sitl copter --home="47.397607253323756,8.545229035687205,488.0,0" --instance 32 -I 32 --sysid 33 > "$PROJECT_DIR/logs/sitl_drone33.log" 2>&1 &
PIDS+=($!)

# Drone 34 (SYSID=34)
dronekit-sitl copter --home="47.397607253323756,8.545295392834985,488.0,0" --instance 33 -I 33 --sysid 34 > "$PROJECT_DIR/logs/sitl_drone34.log" 2>&1 &
PIDS+=($!)

# Drone 35 (SYSID=35)
dronekit-sitl copter --home="47.397607253323756,8.545361749982767,488.0,0" --instance 34 -I 34 --sysid 35 > "$PROJECT_DIR/logs/sitl_drone35.log" 2>&1 &
PIDS+=($!)

# Drone 36 (SYSID=36)
dronekit-sitl copter --home="47.397607253323756,8.545428107130547,488.0,0" --instance 35 -I 35 --sysid 36 > "$PROJECT_DIR/logs/sitl_drone36.log" 2>&1 &
PIDS+=($!)

# Drone 37 (SYSID=37)
dronekit-sitl copter --home="47.397607253323756,8.545494464278327,488.0,0" --instance 36 -I 36 --sysid 37 > "$PROJECT_DIR/logs/sitl_drone37.log" 2>&1 &
PIDS+=($!)

# Drone 38 (SYSID=38)
dronekit-sitl copter --home="47.397607253323756,8.54556082142611,488.0,0" --instance 37 -I 37 --sysid 38 > "$PROJECT_DIR/logs/sitl_drone38.log" 2>&1 &
PIDS+=($!)

# Drone 39 (SYSID=39)
dronekit-sitl copter --home="47.397607253323756,8.54562717857389,488.0,0" --instance 38 -I 38 --sysid 39 > "$PROJECT_DIR/logs/sitl_drone39.log" 2>&1 &
PIDS+=($!)

# Drone 40 (SYSID=40)
dronekit-sitl copter --home="47.397607253323756,8.545693535721671,488.0,0" --instance 39 -I 39 --sysid 40 > "$PROJECT_DIR/logs/sitl_drone40.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 41 (SYSID=41)
dronekit-sitl copter --home="47.397607253323756,8.545759892869452,488.0,0" --instance 40 -I 40 --sysid 41 > "$PROJECT_DIR/logs/sitl_drone41.log" 2>&1 &
PIDS+=($!)

# Drone 42 (SYSID=42)
dronekit-sitl copter --home="47.397607253323756,8.545826250017232,488.0,0" --instance 41 -I 41 --sysid 42 > "$PROJECT_DIR/logs/sitl_drone42.log" 2>&1 &
PIDS+=($!)

# Drone 43 (SYSID=43)
dronekit-sitl copter --home="47.397607253323756,8.545892607165014,488.0,0" --instance 42 -I 42 --sysid 43 > "$PROJECT_DIR/logs/sitl_drone43.log" 2>&1 &
PIDS+=($!)

# Drone 44 (SYSID=44)
dronekit-sitl copter --home="47.397607253323756,8.545958964312794,488.0,0" --instance 43 -I 43 --sysid 44 > "$PROJECT_DIR/logs/sitl_drone44.log" 2>&1 &
PIDS+=($!)

# Drone 45 (SYSID=45)
dronekit-sitl copter --home="47.397607253323756,8.546025321460576,488.0,0" --instance 44 -I 44 --sysid 45 > "$PROJECT_DIR/logs/sitl_drone45.log" 2>&1 &
PIDS+=($!)

# Drone 46 (SYSID=46)
dronekit-sitl copter --home="47.3976521688825,8.545096321391643,488.0,0" --instance 45 -I 45 --sysid 46 > "$PROJECT_DIR/logs/sitl_drone46.log" 2>&1 &
PIDS+=($!)

# Drone 47 (SYSID=47)
dronekit-sitl copter --home="47.3976521688825,8.545162678539423,488.0,0" --instance 46 -I 46 --sysid 47 > "$PROJECT_DIR/logs/sitl_drone47.log" 2>&1 &
PIDS+=($!)

# Drone 48 (SYSID=48)
dronekit-sitl copter --home="47.3976521688825,8.545229035687205,488.0,0" --instance 47 -I 47 --sysid 48 > "$PROJECT_DIR/logs/sitl_drone48.log" 2>&1 &
PIDS+=($!)

# Drone 49 (SYSID=49)
dronekit-sitl copter --home="47.3976521688825,8.545295392834985,488.0,0" --instance 48 -I 48 --sysid 49 > "$PROJECT_DIR/logs/sitl_drone49.log" 2>&1 &
PIDS+=($!)

# Drone 50 (SYSID=50)
dronekit-sitl copter --home="47.3976521688825,8.545361749982767,488.0,0" --instance 49 -I 49 --sysid 50 > "$PROJECT_DIR/logs/sitl_drone50.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 51 (SYSID=51)
dronekit-sitl copter --home="47.3976521688825,8.545428107130547,488.0,0" --instance 50 -I 50 --sysid 51 > "$PROJECT_DIR/logs/sitl_drone51.log" 2>&1 &
PIDS+=($!)

# Drone 52 (SYSID=52)
dronekit-sitl copter --home="47.3976521688825,8.545494464278327,488.0,0" --instance 51 -I 51 --sysid 52 > "$PROJECT_DIR/logs/sitl_drone52.log" 2>&1 &
PIDS+=($!)

# Drone 53 (SYSID=53)
dronekit-sitl copter --home="47.3976521688825,8.54556082142611,488.0,0" --instance 52 -I 52 --sysid 53 > "$PROJECT_DIR/logs/sitl_drone53.log" 2>&1 &
PIDS+=($!)

# Drone 54 (SYSID=54)
dronekit-sitl copter --home="47.3976521688825,8.54562717857389,488.0,0" --instance 53 -I 53 --sysid 54 > "$PROJECT_DIR/logs/sitl_drone54.log" 2>&1 &
PIDS+=($!)

# Drone 55 (SYSID=55)
dronekit-sitl copter --home="47.3976521688825,8.545693535721671,488.0,0" --instance 54 -I 54 --sysid 55 > "$PROJECT_DIR/logs/sitl_drone55.log" 2>&1 &
PIDS+=($!)

# Drone 56 (SYSID=56)
dronekit-sitl copter --home="47.3976521688825,8.545759892869452,488.0,0" --instance 55 -I 55 --sysid 56 > "$PROJECT_DIR/logs/sitl_drone56.log" 2>&1 &
PIDS+=($!)

# Drone 57 (SYSID=57)
dronekit-sitl copter --home="47.3976521688825,8.545826250017232,488.0,0" --instance 56 -I 56 --sysid 57 > "$PROJECT_DIR/logs/sitl_drone57.log" 2>&1 &
PIDS+=($!)

# Drone 58 (SYSID=58)
dronekit-sitl copter --home="47.3976521688825,8.545892607165014,488.0,0" --instance 57 -I 57 --sysid 58 > "$PROJECT_DIR/logs/sitl_drone58.log" 2>&1 &
PIDS+=($!)

# Drone 59 (SYSID=59)
dronekit-sitl copter --home="47.3976521688825,8.545958964312794,488.0,0" --instance 58 -I 58 --sysid 59 > "$PROJECT_DIR/logs/sitl_drone59.log" 2>&1 &
PIDS+=($!)

# Drone 60 (SYSID=60)
dronekit-sitl copter --home="47.3976521688825,8.546025321460576,488.0,0" --instance 59 -I 59 --sysid 60 > "$PROJECT_DIR/logs/sitl_drone60.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 61 (SYSID=61)
dronekit-sitl copter --home="47.397697084441255,8.545096321391643,488.0,0" --instance 60 -I 60 --sysid 61 > "$PROJECT_DIR/logs/sitl_drone61.log" 2>&1 &
PIDS+=($!)

# Drone 62 (SYSID=62)
dronekit-sitl copter --home="47.397697084441255,8.545162678539423,488.0,0" --instance 61 -I 61 --sysid 62 > "$PROJECT_DIR/logs/sitl_drone62.log" 2>&1 &
PIDS+=($!)

# Drone 63 (SYSID=63)
dronekit-sitl copter --home="47.397697084441255,8.545229035687205,488.0,0" --instance 62 -I 62 --sysid 63 > "$PROJECT_DIR/logs/sitl_drone63.log" 2>&1 &
PIDS+=($!)

# Drone 64 (SYSID=64)
dronekit-sitl copter --home="47.397697084441255,8.545295392834985,488.0,0" --instance 63 -I 63 --sysid 64 > "$PROJECT_DIR/logs/sitl_drone64.log" 2>&1 &
PIDS+=($!)

# Drone 65 (SYSID=65)
dronekit-sitl copter --home="47.397697084441255,8.545361749982767,488.0,0" --instance 64 -I 64 --sysid 65 > "$PROJECT_DIR/logs/sitl_drone65.log" 2>&1 &
PIDS+=($!)

# Drone 66 (SYSID=66)
dronekit-sitl copter --home="47.397697084441255,8.545428107130547,488.0,0" --instance 65 -I 65 --sysid 66 > "$PROJECT_DIR/logs/sitl_drone66.log" 2>&1 &
PIDS+=($!)

# Drone 67 (SYSID=67)
dronekit-sitl copter --home="47.397697084441255,8.545494464278327,488.0,0" --instance 66 -I 66 --sysid 67 > "$PROJECT_DIR/logs/sitl_drone67.log" 2>&1 &
PIDS+=($!)

# Drone 68 (SYSID=68)
dronekit-sitl copter --home="47.397697084441255,8.54556082142611,488.0,0" --instance 67 -I 67 --sysid 68 > "$PROJECT_DIR/logs/sitl_drone68.log" 2>&1 &
PIDS+=($!)

# Drone 69 (SYSID=69)
dronekit-sitl copter --home="47.397697084441255,8.54562717857389,488.0,0" --instance 68 -I 68 --sysid 69 > "$PROJECT_DIR/logs/sitl_drone69.log" 2>&1 &
PIDS+=($!)

# Drone 70 (SYSID=70)
dronekit-sitl copter --home="47.397697084441255,8.545693535721671,488.0,0" --instance 69 -I 69 --sysid 70 > "$PROJECT_DIR/logs/sitl_drone70.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 71 (SYSID=71)
dronekit-sitl copter --home="47.397697084441255,8.545759892869452,488.0,0" --instance 70 -I 70 --sysid 71 > "$PROJECT_DIR/logs/sitl_drone71.log" 2>&1 &
PIDS+=($!)

# Drone 72 (SYSID=72)
dronekit-sitl copter --home="47.397697084441255,8.545826250017232,488.0,0" --instance 71 -I 71 --sysid 72 > "$PROJECT_DIR/logs/sitl_drone72.log" 2>&1 &
PIDS+=($!)

# Drone 73 (SYSID=73)
dronekit-sitl copter --home="47.397697084441255,8.545892607165014,488.0,0" --instance 72 -I 72 --sysid 73 > "$PROJECT_DIR/logs/sitl_drone73.log" 2>&1 &
PIDS+=($!)

# Drone 74 (SYSID=74)
dronekit-sitl copter --home="47.397697084441255,8.545958964312794,488.0,0" --instance 73 -I 73 --sysid 74 > "$PROJECT_DIR/logs/sitl_drone74.log" 2>&1 &
PIDS+=($!)

# Drone 75 (SYSID=75)
dronekit-sitl copter --home="47.397697084441255,8.546025321460576,488.0,0" --instance 74 -I 74 --sysid 75 > "$PROJECT_DIR/logs/sitl_drone75.log" 2>&1 &
PIDS+=($!)

# Drone 76 (SYSID=76)
dronekit-sitl copter --home="47.397742,8.545096321391643,488.0,0" --instance 75 -I 75 --sysid 76 > "$PROJECT_DIR/logs/sitl_drone76.log" 2>&1 &
PIDS+=($!)

# Drone 77 (SYSID=77)
dronekit-sitl copter --home="47.397742,8.545162678539423,488.0,0" --instance 76 -I 76 --sysid 77 > "$PROJECT_DIR/logs/sitl_drone77.log" 2>&1 &
PIDS+=($!)

# Drone 78 (SYSID=78)
dronekit-sitl copter --home="47.397742,8.545229035687205,488.0,0" --instance 77 -I 77 --sysid 78 > "$PROJECT_DIR/logs/sitl_drone78.log" 2>&1 &
PIDS+=($!)

# Drone 79 (SYSID=79)
dronekit-sitl copter --home="47.397742,8.545295392834985,488.0,0" --instance 78 -I 78 --sysid 79 > "$PROJECT_DIR/logs/sitl_drone79.log" 2>&1 &
PIDS+=($!)

# Drone 80 (SYSID=80)
dronekit-sitl copter --home="47.397742,8.545361749982767,488.0,0" --instance 79 -I 79 --sysid 80 > "$PROJECT_DIR/logs/sitl_drone80.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 81 (SYSID=81)
dronekit-sitl copter --home="47.397742,8.545428107130547,488.0,0" --instance 80 -I 80 --sysid 81 > "$PROJECT_DIR/logs/sitl_drone81.log" 2>&1 &
PIDS+=($!)

# Drone 82 (SYSID=82)
dronekit-sitl copter --home="47.397742,8.545494464278327,488.0,0" --instance 81 -I 81 --sysid 82 > "$PROJECT_DIR/logs/sitl_drone82.log" 2>&1 &
PIDS+=($!)

# Drone 83 (SYSID=83)
dronekit-sitl copter --home="47.397742,8.54556082142611,488.0,0" --instance 82 -I 82 --sysid 83 > "$PROJECT_DIR/logs/sitl_drone83.log" 2>&1 &
PIDS+=($!)

# Drone 84 (SYSID=84)
dronekit-sitl copter --home="47.397742,8.54562717857389,488.0,0" --instance 83 -I 83 --sysid 84 > "$PROJECT_DIR/logs/sitl_drone84.log" 2>&1 &
PIDS+=($!)

# Drone 85 (SYSID=85)
dronekit-sitl copter --home="47.397742,8.545693535721671,488.0,0" --instance 84 -I 84 --sysid 85 > "$PROJECT_DIR/logs/sitl_drone85.log" 2>&1 &
PIDS+=($!)

# Drone 86 (SYSID=86)
dronekit-sitl copter --home="47.397742,8.545759892869452,488.0,0" --instance 85 -I 85 --sysid 86 > "$PROJECT_DIR/logs/sitl_drone86.log" 2>&1 &
PIDS+=($!)

# Drone 87 (SYSID=87)
dronekit-sitl copter --home="47.397742,8.545826250017232,488.0,0" --instance 86 -I 86 --sysid 87 > "$PROJECT_DIR/logs/sitl_drone87.log" 2>&1 &
PIDS+=($!)

# Drone 88 (SYSID=88)
dronekit-sitl copter --home="47.397742,8.545892607165014,488.0,0" --instance 87 -I 87 --sysid 88 > "$PROJECT_DIR/logs/sitl_drone88.log" 2>&1 &
PIDS+=($!)

# Drone 89 (SYSID=89)
dronekit-sitl copter --home="47.397742,8.545958964312794,488.0,0" --instance 88 -I 88 --sysid 89 > "$PROJECT_DIR/logs/sitl_drone89.log" 2>&1 &
PIDS+=($!)

# Drone 90 (SYSID=90)
dronekit-sitl copter --home="47.397742,8.546025321460576,488.0,0" --instance 89 -I 89 --sysid 90 > "$PROJECT_DIR/logs/sitl_drone90.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 91 (SYSID=91)
dronekit-sitl copter --home="47.39778691555875,8.545096321391643,488.0,0" --instance 90 -I 90 --sysid 91 > "$PROJECT_DIR/logs/sitl_drone91.log" 2>&1 &
PIDS+=($!)

# Drone 92 (SYSID=92)
dronekit-sitl copter --home="47.39778691555875,8.545162678539423,488.0,0" --instance 91 -I 91 --sysid 92 > "$PROJECT_DIR/logs/sitl_drone92.log" 2>&1 &
PIDS+=($!)

# Drone 93 (SYSID=93)
dronekit-sitl copter --home="47.39778691555875,8.545229035687205,488.0,0" --instance 92 -I 92 --sysid 93 > "$PROJECT_DIR/logs/sitl_drone93.log" 2>&1 &
PIDS+=($!)

# Drone 94 (SYSID=94)
dronekit-sitl copter --home="47.39778691555875,8.545295392834985,488.0,0" --instance 93 -I 93 --sysid 94 > "$PROJECT_DIR/logs/sitl_drone94.log" 2>&1 &
PIDS+=($!)

# Drone 95 (SYSID=95)
dronekit-sitl copter --home="47.39778691555875,8.545361749982767,488.0,0" --instance 94 -I 94 --sysid 95 > "$PROJECT_DIR/logs/sitl_drone95.log" 2>&1 &
PIDS+=($!)

# Drone 96 (SYSID=96)
dronekit-sitl copter --home="47.39778691555875,8.545428107130547,488.0,0" --instance 95 -I 95 --sysid 96 > "$PROJECT_DIR/logs/sitl_drone96.log" 2>&1 &
PIDS+=($!)

# Drone 97 (SYSID=97)
dronekit-sitl copter --home="47.39778691555875,8.545494464278327,488.0,0" --instance 96 -I 96 --sysid 97 > "$PROJECT_DIR/logs/sitl_drone97.log" 2>&1 &
PIDS+=($!)

# Drone 98 (SYSID=98)
dronekit-sitl copter --home="47.39778691555875,8.54556082142611,488.0,0" --instance 97 -I 97 --sysid 98 > "$PROJECT_DIR/logs/sitl_drone98.log" 2>&1 &
PIDS+=($!)

# Drone 99 (SYSID=99)
dronekit-sitl copter --home="47.39778691555875,8.54562717857389,488.0,0" --instance 98 -I 98 --sysid 99 > "$PROJECT_DIR/logs/sitl_drone99.log" 2>&1 &
PIDS+=($!)

# Drone 100 (SYSID=100)
dronekit-sitl copter --home="47.39778691555875,8.545693535721671,488.0,0" --instance 99 -I 99 --sysid 100 > "$PROJECT_DIR/logs/sitl_drone100.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 101 (SYSID=101)
dronekit-sitl copter --home="47.39778691555875,8.545759892869452,488.0,0" --instance 100 -I 100 --sysid 101 > "$PROJECT_DIR/logs/sitl_drone101.log" 2>&1 &
PIDS+=($!)

# Drone 102 (SYSID=102)
dronekit-sitl copter --home="47.39778691555875,8.545826250017232,488.0,0" --instance 101 -I 101 --sysid 102 > "$PROJECT_DIR/logs/sitl_drone102.log" 2>&1 &
PIDS+=($!)

# Drone 103 (SYSID=103)
dronekit-sitl copter --home="47.39778691555875,8.545892607165014,488.0,0" --instance 102 -I 102 --sysid 103 > "$PROJECT_DIR/logs/sitl_drone103.log" 2>&1 &
PIDS+=($!)

# Drone 104 (SYSID=104)
dronekit-sitl copter --home="47.39778691555875,8.545958964312794,488.0,0" --instance 103 -I 103 --sysid 104 > "$PROJECT_DIR/logs/sitl_drone104.log" 2>&1 &
PIDS+=($!)

# Drone 105 (SYSID=105)
dronekit-sitl copter --home="47.39778691555875,8.546025321460576,488.0,0" --instance 104 -I 104 --sysid 105 > "$PROJECT_DIR/logs/sitl_drone105.log" 2>&1 &
PIDS+=($!)

# Drone 106 (SYSID=106)
dronekit-sitl copter --home="47.3978318311175,8.545096321391643,488.0,0" --instance 105 -I 105 --sysid 106 > "$PROJECT_DIR/logs/sitl_drone106.log" 2>&1 &
PIDS+=($!)

# Drone 107 (SYSID=107)
dronekit-sitl copter --home="47.3978318311175,8.545162678539423,488.0,0" --instance 106 -I 106 --sysid 107 > "$PROJECT_DIR/logs/sitl_drone107.log" 2>&1 &
PIDS+=($!)

# Drone 108 (SYSID=108)
dronekit-sitl copter --home="47.3978318311175,8.545229035687205,488.0,0" --instance 107 -I 107 --sysid 108 > "$PROJECT_DIR/logs/sitl_drone108.log" 2>&1 &
PIDS+=($!)

# Drone 109 (SYSID=109)
dronekit-sitl copter --home="47.3978318311175,8.545295392834985,488.0,0" --instance 108 -I 108 --sysid 109 > "$PROJECT_DIR/logs/sitl_drone109.log" 2>&1 &
PIDS+=($!)

# Drone 110 (SYSID=110)
dronekit-sitl copter --home="47.3978318311175,8.545361749982767,488.0,0" --instance 109 -I 109 --sysid 110 > "$PROJECT_DIR/logs/sitl_drone110.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 111 (SYSID=111)
dronekit-sitl copter --home="47.3978318311175,8.545428107130547,488.0,0" --instance 110 -I 110 --sysid 111 > "$PROJECT_DIR/logs/sitl_drone111.log" 2>&1 &
PIDS+=($!)

# Drone 112 (SYSID=112)
dronekit-sitl copter --home="47.3978318311175,8.545494464278327,488.0,0" --instance 111 -I 111 --sysid 112 > "$PROJECT_DIR/logs/sitl_drone112.log" 2>&1 &
PIDS+=($!)

# Drone 113 (SYSID=113)
dronekit-sitl copter --home="47.3978318311175,8.54556082142611,488.0,0" --instance 112 -I 112 --sysid 113 > "$PROJECT_DIR/logs/sitl_drone113.log" 2>&1 &
PIDS+=($!)

# Drone 114 (SYSID=114)
dronekit-sitl copter --home="47.3978318311175,8.54562717857389,488.0,0" --instance 113 -I 113 --sysid 114 > "$PROJECT_DIR/logs/sitl_drone114.log" 2>&1 &
PIDS+=($!)

# Drone 115 (SYSID=115)
dronekit-sitl copter --home="47.3978318311175,8.545693535721671,488.0,0" --instance 114 -I 114 --sysid 115 > "$PROJECT_DIR/logs/sitl_drone115.log" 2>&1 &
PIDS+=($!)

# Drone 116 (SYSID=116)
dronekit-sitl copter --home="47.3978318311175,8.545759892869452,488.0,0" --instance 115 -I 115 --sysid 116 > "$PROJECT_DIR/logs/sitl_drone116.log" 2>&1 &
PIDS+=($!)

# Drone 117 (SYSID=117)
dronekit-sitl copter --home="47.3978318311175,8.545826250017232,488.0,0" --instance 116 -I 116 --sysid 117 > "$PROJECT_DIR/logs/sitl_drone117.log" 2>&1 &
PIDS+=($!)

# Drone 118 (SYSID=118)
dronekit-sitl copter --home="47.3978318311175,8.545892607165014,488.0,0" --instance 117 -I 117 --sysid 118 > "$PROJECT_DIR/logs/sitl_drone118.log" 2>&1 &
PIDS+=($!)

# Drone 119 (SYSID=119)
dronekit-sitl copter --home="47.3978318311175,8.545958964312794,488.0,0" --instance 118 -I 118 --sysid 119 > "$PROJECT_DIR/logs/sitl_drone119.log" 2>&1 &
PIDS+=($!)

# Drone 120 (SYSID=120)
dronekit-sitl copter --home="47.3978318311175,8.546025321460576,488.0,0" --instance 119 -I 119 --sysid 120 > "$PROJECT_DIR/logs/sitl_drone120.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 121 (SYSID=121)
dronekit-sitl copter --home="47.397876746676246,8.545096321391643,488.0,0" --instance 120 -I 120 --sysid 121 > "$PROJECT_DIR/logs/sitl_drone121.log" 2>&1 &
PIDS+=($!)

# Drone 122 (SYSID=122)
dronekit-sitl copter --home="47.397876746676246,8.545162678539423,488.0,0" --instance 121 -I 121 --sysid 122 > "$PROJECT_DIR/logs/sitl_drone122.log" 2>&1 &
PIDS+=($!)

# Drone 123 (SYSID=123)
dronekit-sitl copter --home="47.397876746676246,8.545229035687205,488.0,0" --instance 122 -I 122 --sysid 123 > "$PROJECT_DIR/logs/sitl_drone123.log" 2>&1 &
PIDS+=($!)

# Drone 124 (SYSID=124)
dronekit-sitl copter --home="47.397876746676246,8.545295392834985,488.0,0" --instance 123 -I 123 --sysid 124 > "$PROJECT_DIR/logs/sitl_drone124.log" 2>&1 &
PIDS+=($!)

# Drone 125 (SYSID=125)
dronekit-sitl copter --home="47.397876746676246,8.545361749982767,488.0,0" --instance 124 -I 124 --sysid 125 > "$PROJECT_DIR/logs/sitl_drone125.log" 2>&1 &
PIDS+=($!)

# Drone 126 (SYSID=126)
dronekit-sitl copter --home="47.397876746676246,8.545428107130547,488.0,0" --instance 125 -I 125 --sysid 126 > "$PROJECT_DIR/logs/sitl_drone126.log" 2>&1 &
PIDS+=($!)

# Drone 127 (SYSID=127)
dronekit-sitl copter --home="47.397876746676246,8.545494464278327,488.0,0" --instance 126 -I 126 --sysid 127 > "$PROJECT_DIR/logs/sitl_drone127.log" 2>&1 &
PIDS+=($!)

# Drone 128 (SYSID=128)
dronekit-sitl copter --home="47.397876746676246,8.54556082142611,488.0,0" --instance 127 -I 127 --sysid 128 > "$PROJECT_DIR/logs/sitl_drone128.log" 2>&1 &
PIDS+=($!)

# Drone 129 (SYSID=129)
dronekit-sitl copter --home="47.397876746676246,8.54562717857389,488.0,0" --instance 128 -I 128 --sysid 129 > "$PROJECT_DIR/logs/sitl_drone129.log" 2>&1 &
PIDS+=($!)

# Drone 130 (SYSID=130)
dronekit-sitl copter --home="47.397876746676246,8.545693535721671,488.0,0" --instance 129 -I 129 --sysid 130 > "$PROJECT_DIR/logs/sitl_drone130.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 131 (SYSID=131)
dronekit-sitl copter --home="47.397876746676246,8.545759892869452,488.0,0" --instance 130 -I 130 --sysid 131 > "$PROJECT_DIR/logs/sitl_drone131.log" 2>&1 &
PIDS+=($!)

# Drone 132 (SYSID=132)
dronekit-sitl copter --home="47.397876746676246,8.545826250017232,488.0,0" --instance 131 -I 131 --sysid 132 > "$PROJECT_DIR/logs/sitl_drone132.log" 2>&1 &
PIDS+=($!)

# Drone 133 (SYSID=133)
dronekit-sitl copter --home="47.397876746676246,8.545892607165014,488.0,0" --instance 132 -I 132 --sysid 133 > "$PROJECT_DIR/logs/sitl_drone133.log" 2>&1 &
PIDS+=($!)

# Drone 134 (SYSID=134)
dronekit-sitl copter --home="47.397876746676246,8.545958964312794,488.0,0" --instance 133 -I 133 --sysid 134 > "$PROJECT_DIR/logs/sitl_drone134.log" 2>&1 &
PIDS+=($!)

# Drone 135 (SYSID=135)
dronekit-sitl copter --home="47.397876746676246,8.546025321460576,488.0,0" --instance 134 -I 134 --sysid 135 > "$PROJECT_DIR/logs/sitl_drone135.log" 2>&1 &
PIDS+=($!)

# Drone 136 (SYSID=136)
dronekit-sitl copter --home="47.397921662235,8.545096321391643,488.0,0" --instance 135 -I 135 --sysid 136 > "$PROJECT_DIR/logs/sitl_drone136.log" 2>&1 &
PIDS+=($!)

# Drone 137 (SYSID=137)
dronekit-sitl copter --home="47.397921662235,8.545162678539423,488.0,0" --instance 136 -I 136 --sysid 137 > "$PROJECT_DIR/logs/sitl_drone137.log" 2>&1 &
PIDS+=($!)

# Drone 138 (SYSID=138)
dronekit-sitl copter --home="47.397921662235,8.545229035687205,488.0,0" --instance 137 -I 137 --sysid 138 > "$PROJECT_DIR/logs/sitl_drone138.log" 2>&1 &
PIDS+=($!)

# Drone 139 (SYSID=139)
dronekit-sitl copter --home="47.397921662235,8.545295392834985,488.0,0" --instance 138 -I 138 --sysid 139 > "$PROJECT_DIR/logs/sitl_drone139.log" 2>&1 &
PIDS+=($!)

# Drone 140 (SYSID=140)
dronekit-sitl copter --home="47.397921662235,8.545361749982767,488.0,0" --instance 139 -I 139 --sysid 140 > "$PROJECT_DIR/logs/sitl_drone140.log" 2>&1 &
PIDS+=($!)
sleep 2

# Drone 141 (SYSID=141)
dronekit-sitl copter --home="47.397921662235,8.545428107130547,488.0,0" --instance 140 -I 140 --sysid 141 > "$PROJECT_DIR/logs/sitl_drone141.log" 2>&1 &
PIDS+=($!)

# Drone 142 (SYSID=142)
dronekit-sitl copter --home="47.397921662235,8.545494464278327,488.0,0" --instance 141 -I 141 --sysid 142 > "$PROJECT_DIR/logs/sitl_drone142.log" 2>&1 &
PIDS+=($!)

# Drone 143 (SYSID=143)
dronekit-sitl copter --home="47.397921662235,8.54556082142611,488.0,0" --instance 142 -I 142 --sysid 143 > "$PROJECT_DIR/logs/sitl_drone143.log" 2>&1 &
PIDS+=($!)

# Drone 144 (SYSID=144)
dronekit-sitl copter --home="47.397921662235,8.54562717857389,488.0,0" --instance 143 -I 143 --sysid 144 > "$PROJECT_DIR/logs/sitl_drone144.log" 2>&1 &
PIDS+=($!)

# Drone 145 (SYSID=145)
dronekit-sitl copter --home="47.397921662235,8.545693535721671,488.0,0" --instance 144 -I 144 --sysid 145 > "$PROJECT_DIR/logs/sitl_drone145.log" 2>&1 &
PIDS+=($!)

# Drone 146 (SYSID=146)
dronekit-sitl copter --home="47.397921662235,8.545759892869452,488.0,0" --instance 145 -I 145 --sysid 146 > "$PROJECT_DIR/logs/sitl_drone146.log" 2>&1 &
PIDS+=($!)

# Drone 147 (SYSID=147)
dronekit-sitl copter --home="47.397921662235,8.545826250017232,488.0,0" --instance 146 -I 146 --sysid 147 > "$PROJECT_DIR/logs/sitl_drone147.log" 2>&1 &
PIDS+=($!)

# Drone 148 (SYSID=148)
dronekit-sitl copter --home="47.397921662235,8.545892607165014,488.0,0" --instance 147 -I 147 --sysid 148 > "$PROJECT_DIR/logs/sitl_drone148.log" 2>&1 &
PIDS+=($!)

# Drone 149 (SYSID=149)
dronekit-sitl copter --home="47.397921662235,8.545958964312794,488.0,0" --instance 148 -I 148 --sysid 149 > "$PROJECT_DIR/logs/sitl_drone149.log" 2>&1 &
PIDS+=($!)

# Drone 150 (SYSID=150)
dronekit-sitl copter --home="47.397921662235,8.546025321460576,488.0,0" --instance 149 -I 149 --sysid 150 > "$PROJECT_DIR/logs/sitl_drone150.log" 2>&1 &
PIDS+=($!)
sleep 2


echo "Launched 150 SITL instances"
echo "${PIDS[*]}" > "$PROJECT_DIR/logs/fleet_pids.txt"
echo "PIDs saved to logs/fleet_pids.txt"

trap "kill ${PIDS[*]} 2>/dev/null; exit 0" SIGINT SIGTERM
wait
