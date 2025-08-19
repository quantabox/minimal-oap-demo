#!/bin/bash

# Minimal OAP Demo - Stop All Agent Servers
# This script gracefully stops all running LangGraph servers

set -e

echo "🛑 Stopping Minimal OAP Demo - Multi-Agent System"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to stop agent server
stop_agent() {
    local agent_name=$1
    local pid_file="pids/${agent_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${BLUE}🛑 Stopping $agent_name (PID: $pid)...${NC}"
            kill "$pid"
            sleep 2
            
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${YELLOW}⚠️  Force stopping $agent_name...${NC}"
                kill -9 "$pid" 2>/dev/null || true
            fi
            
            echo -e "${GREEN}✅ $agent_name stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  $agent_name was not running (stale PID file)${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}⚠️  No PID file found for $agent_name${NC}"
    fi
}

# Stop all agents
if [ -d "pids" ]; then
    echo -e "${BLUE}🔍 Stopping all agent servers...${NC}"
    
    stop_agent "Math Agent"
    stop_agent "Text Agent"
    stop_agent "Supervisor Agent"
    
    # Clean up PID directory
    rmdir pids 2>/dev/null || true
else
    echo -e "${YELLOW}⚠️  No PID directory found - agents may not be running${NC}"
fi

# Also kill any langgraph processes on our ports (backup cleanup)
echo -e "${BLUE}🧹 Cleaning up any remaining processes on target ports...${NC}"

for port in 2024 2025 2026; do
    local pid=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pid" ]; then
        echo -e "${BLUE}🛑 Stopping process on port $port (PID: $pid)...${NC}"
        kill "$pid" 2>/dev/null || true
        sleep 1
        # Force kill if needed
        kill -9 "$pid" 2>/dev/null || true
    fi
done

echo ""
echo -e "${GREEN}🎉 All agents stopped successfully!${NC}"
echo "================================================"
echo -e "${BLUE}📋 Ports are now available:${NC}"
echo "  • Port 2024 (Supervisor)"
echo "  • Port 2025 (Math Agent)"
echo "  • Port 2026 (Text Agent)"
echo ""
echo -e "${YELLOW}💡 Log files preserved in logs/ directory${NC}"
echo -e "${GREEN}✨ System shutdown complete!${NC}"