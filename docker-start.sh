#!/bin/bash

# Docker Quick Start Script
# This script starts the Avatar application with Docker using existing credentials

set -e  # Exit on error

echo "🐳 Avatar Docker Setup & Start"
echo "=============================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Check if Docker is installed
echo "Step 1: Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    echo "Please install Docker from https://www.docker.com/products/docker-desktop"
    exit 1
fi
print_success "Docker is installed: $(docker --version)"

# Step 2: Check if Docker Compose is installed
echo ""
echo "Step 2: Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
print_success "Docker Compose is installed: $(docker-compose --version)"

# Step 3: Verify .env files exist
echo ""
echo "Step 3: Checking environment files..."

if [ ! -f "./avatary/.env" ]; then
    print_error "avatary/.env not found"
    exit 1
fi
print_success "avatary/.env exists"

if [ ! -f "./callCenter/.env" ]; then
    print_error "callCenter/.env not found"
    exit 1
fi
print_success "callCenter/.env exists"

if [ ! -f "./.env" ]; then
    print_warning ".env not found at root level"
    echo "Creating from .env.example..."
    if [ -f "./.env.example" ]; then
        cp ./.env.example ./.env
        print_success "Created .env from .env.example"
    else
        print_warning "No .env.example found, creating minimal .env..."
        cat > ./.env << 'EOF'
# Extract these from avatary/.env and callCenter/.env
LIVEKIT_URL=
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
OPENAI_API_KEY=
EOF
        print_warning "Please fill in .env with values from avatary/.env and callCenter/.env"
    fi
else
    print_success ".env exists"
fi

# Step 4: Check for required credentials
echo ""
echo "Step 4: Verifying credentials..."

# Check avatary .env
if grep -q "TAVUS_API_KEY=" ./avatary/.env && [ -n "$(grep 'TAVUS_API_KEY=' ./avatary/.env | cut -d'=' -f2)" ]; then
    print_success "Tavus API Key configured"
else
    print_warning "Tavus API Key might not be configured"
fi

if grep -q "OPENAI_API_KEY=" ./avatary/.env && [ -n "$(grep 'OPENAI_API_KEY=' ./avatary/.env | cut -d'=' -f2)" ]; then
    print_success "Avatar OpenAI API Key configured"
else
    print_warning "Avatar OpenAI API Key might not be configured"
fi

# Check callCenter .env
if grep -q "SUPABASE_URL=" ./callCenter/.env && [ -n "$(grep 'SUPABASE_URL=' ./callCenter/.env | cut -d'=' -f2)" ]; then
    print_success "Supabase URL configured"
else
    print_warning "Supabase URL might not be configured"
fi

if grep -q "DATABASE_URL=" ./callCenter/.env && [ -n "$(grep 'DATABASE_URL=' ./callCenter/.env | cut -d'=' -f2)" ]; then
    print_success "Database URL configured"
else
    print_warning "Database URL might not be configured"
fi

# Step 5: Check available ports
echo ""
echo "Step 5: Checking required ports..."

check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port $port ($service) is already in use"
        return 1
    else
        print_success "Port $port ($service) is available"
        return 0
    fi
}

check_port 3000 "Frontend" || true
check_port 8000 "Call Center" || true
check_port 8080 "Avatar Backend" || true
check_port 6379 "Redis" || true

# Step 6: Build images
echo ""
echo "Step 6: Building Docker images..."
echo "(This may take a few minutes on first run)"
echo ""

if docker-compose build; then
    print_success "Docker images built successfully"
else
    print_error "Failed to build Docker images"
    echo "Check the error messages above"
    exit 1
fi

# Step 7: Start services
echo ""
echo "Step 7: Starting services..."
echo ""

if docker-compose up -d; then
    print_success "Services started successfully"
else
    print_error "Failed to start services"
    exit 1
fi

# Step 8: Wait for services to be healthy
echo ""
echo "Step 8: Waiting for services to be ready..."
echo "(This may take 30-60 seconds)"
echo ""

# Give services time to start
sleep 10

# Check service health
max_attempts=20
attempt=1

while [ $attempt -le $max_attempts ]; do
    echo -n "."

    # Check if all services are healthy or running
    if docker-compose ps | grep -q "avatar-frontend" && \
       docker-compose ps | grep -q "avatar-backend" && \
       docker-compose ps | grep -q "avatar-callcenter" && \
       docker-compose ps | grep -q "avatar-redis"; then

        # Quick health check
        if timeout 5 curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo ""
            print_success "All services are ready!"
            break
        fi
    fi

    sleep 3
    ((attempt++))
done

# Step 9: Display service information
echo ""
echo "=============================="
echo "🚀 Services are running!"
echo "=============================="
echo ""
echo "Frontend:"
echo "  URL: http://localhost:3000"
echo "  App: Avatar & Call Center"
echo ""
echo "Avatar Backend:"
echo "  Port: 8080"
echo "  Container: avatar-backend"
echo ""
echo "Call Center Backend:"
echo "  Port: 8000"
echo "  Container: avatar-callcenter"
echo "  API: http://localhost:8000"
echo ""
echo "Redis:"
echo "  Port: 6379"
echo "  Container: avatar-redis"
echo ""
echo "=============================="
echo "Useful Commands:"
echo "=============================="
echo ""
echo "View logs:"
echo "  docker-compose logs -f frontend          # Frontend logs"
echo "  docker-compose logs -f backend           # Avatar backend logs"
echo "  docker-compose logs -f callcenter        # Call center logs"
echo "  docker-compose logs -f                   # All logs"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""
echo "Restart services:"
echo "  docker-compose restart"
echo ""
echo "Access container:"
echo "  docker-compose exec frontend bash"
echo "  docker-compose exec backend bash"
echo "  docker-compose exec callcenter bash"
echo ""
echo "Check service status:"
echo "  docker-compose ps"
echo ""
echo "View environment variables in container:"
echo "  docker exec avatar-backend env | grep -i api"
echo "  docker exec avatar-callcenter env | grep -i supabase"
echo ""
print_success "Setup complete! 🎉"
