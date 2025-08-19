#!/bin/bash

# Minimal OAP Demo - Start All Agent Servers
# This script starts three separate LangGraph servers:
# 1. Math Agent (port 2025)
# 2. Text Agent (port 2026)  
# 3. Supervisor Agent (port 2024)

set -e

echo "🚀 Starting Minimal OAP Demo - Multi-Agent System"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please create a .env file with your API keys:"
    echo "OPENAI_API_KEY=your_key_here"
    echo "ANTHROPIC_API_KEY=your_key_here"
    exit 1
fi

# Source environment variables
source .env

# Validate API keys
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo -e "${YELLOW}⚠️  Warning: OPENAI_API_KEY not set or using placeholder${NC}"
fi

if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_anthropic_api_key_here" ]; then
    echo -e "${YELLOW}⚠️  Warning: ANTHROPIC_API_KEY not set or using placeholder${NC}"
fi

# Function to start agent server
start_agent() {
    local agent_name=$1
    local port=$2
    local directory=$3
    
    echo -e "${BLUE}📊 Starting $agent_name on port $port...${NC}"
    cd "$directory"
    
    # Start LangGraph server using UV environment in background
    uv run langgraph dev --port "$port" --no-browser > "../logs/${agent_name}.log" 2>&1 &
    local pid=$!
    echo $pid > "../pids/${agent_name}.pid"
    
    echo -e "${GREEN}✅ $agent_name started (PID: $pid)${NC}"
    cd ..
}

# Create directories for logs and PIDs
mkdir -p logs pids

# Clean up any existing PID files
rm -f pids/*.pid

echo -e "${BLUE}📁 Installing dependencies with UV...${NC}"
uv sync > logs/install.log 2>&1

echo -e "${BLUE}🎯 Starting individual agent servers...${NC}"

# Start agents in order (specialist agents first, then supervisor)
start_agent "Math Agent" 2025 "math_agent"
sleep 3

start_agent "Text Agent" 2026 "text_agent"  
sleep 3

start_agent "Supervisor Agent" 2024 "supervisor"
sleep 5

echo ""
echo -e "${GREEN}🎉 All agents started successfully!${NC}"
echo "=============================================="
echo -e "${BLUE}📋 Agent Endpoints:${NC}"
echo "  • Math Agent:       http://localhost:2025"
echo "  • Text Agent:       http://localhost:2026"  
echo "  • Supervisor Agent: http://localhost:2024"
echo ""
echo -e "${BLUE}📖 Documentation:${NC}"
echo "  • Math Agent API:       http://localhost:2025/docs"
echo "  • Text Agent API:       http://localhost:2026/docs"
echo "  • Supervisor Agent API: http://localhost:2024/docs"
echo ""
echo -e "${BLUE}🎮 LangGraph Studio (Optional):${NC}"
echo "  • Math Agent:    https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2025"
echo "  • Text Agent:    https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2026"
echo "  • Supervisor:    https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"
echo ""
echo -e "${YELLOW}💡 Usage Tips:${NC}"
echo "  • The supervisor automatically delegates to appropriate agents"
echo "  • Try: 'What is 25 + 17 and convert the result to uppercase text?'"
echo "  • Check logs/ directory for server output"
echo "  • Use stop_agents.sh to shut down all servers"
echo ""
echo -e "${GREEN}✨ Ready to demonstrate OAP-like multi-agent capabilities!${NC}"