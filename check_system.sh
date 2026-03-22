#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# פונקציה לתיקון שירות תקוע
fix_service() {
    local service=$1
    echo -e "${YELLOW}[FIXING]${NC} Attempting to restart $service..."
    docker compose restart $service
    sleep 5 # זמן חסד לאפליקציה לעלות
}

echo "--- Starting Self-Healing Health Check ---"

# 1. בדיקת זמינות הטריוויה (פורט 8000)
status_trivia=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)

if [ $status_trivia -eq 200 ]; then
    echo -e "${GREEN}[OK]${NC} Trivia App is healthy."
else
    echo -e "${RED}[FAIL]${NC} Trivia App is down (Status: $status_trivia)."
    fix_service "trivia-app"
    # בדיקה חוזרת אחרי התיקון
    if [ $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/) -eq 200 ]; then
        echo -e "${GREEN}[FIXED]${NC} Trivia App is back online!"
    fi
fi

# 2. בדיקת זמינות פרומתאוס (פורט 9090)
status_prom=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9090/-/healthy)

if [ $status_prom -eq 200 ]; then
    echo -e "${GREEN}[OK]${NC} Prometheus is healthy."
else
    echo -e "${RED}[FAIL]${NC} Prometheus is down."
    fix_service "prometheus"
fi

echo "--- System Check Completed ---"