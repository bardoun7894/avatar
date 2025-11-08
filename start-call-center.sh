#!/bin/bash

# Call Center System Start Script
# Starts both backend API and frontend servers

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Call Center System Startup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

# Setup backend
echo -e "${YELLOW}Setting up backend API...${NC}"
cd "$SCRIPT_DIR/callCenter"

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -q -r requirements.txt

# Setup frontend
echo -e "${YELLOW}Setting up frontend...${NC}"
cd "$SCRIPT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    npm install -q
fi

# Create environment file if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}Creating .env.local...${NC}"
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
fi

# Start services
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Starting Services${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Start backend in background
echo -e "${YELLOW}Starting backend API on port 8000...${NC}"
cd "$SCRIPT_DIR/callCenter"
source venv/bin/activate
python main.py > /tmp/call-center-backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend PID: $BACKEND_PID${NC}"

# Wait for backend to be ready
sleep 2

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend failed to start. Check /tmp/call-center-backend.log${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✓ Backend API is running${NC}"

# Start frontend in background
echo -e "${YELLOW}Starting frontend on port 3000...${NC}"
cd "$SCRIPT_DIR/frontend"
npm run dev > /tmp/call-center-frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend PID: $FRONTEND_PID${NC}"

# Wait for frontend to be ready
sleep 3

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Services Started Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${GREEN}📱 Frontend:${NC}    http://localhost:3000"
echo -e "${GREEN}⚙️  API:${NC}         http://localhost:8000"
echo -e "${GREEN}📚 API Docs:${NC}     http://localhost:8000/docs"
echo -e "${GREEN}🔌 WebSocket:${NC}    ws://localhost:8000/ws/updates"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo "  Backend:  tail -f /tmp/call-center-backend.log"
echo "  Frontend: tail -f /tmp/call-center-frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop services${NC}"
echo ""

# Trap SIGINT to cleanup
trap "cleanup" INT

cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✓ Services stopped${NC}"
    exit 0
}

# Keep script running
wait
