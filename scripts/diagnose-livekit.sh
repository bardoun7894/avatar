#!/bin/bash

# LiveKit Connection Diagnostic Script
# This script helps identify why the avatar video connection is failing

set -e

echo "🔍 LiveKit Connection Diagnostic Tool"
echo "====================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_check() {
  echo -e "${BLUE}✓${NC} $1"
}

print_error() {
  echo -e "${RED}✗${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
}

print_success() {
  echo -e "${GREEN}✅${NC} $1"
}

print_section() {
  echo ""
  echo -e "${BLUE}=== $1 ===${NC}"
}

# Check 1: .env file
print_section "1. Environment Configuration"

if [ -f "/var/www/avatar/.env" ]; then
  print_success ".env file exists"

  # Extract values
  LIVEKIT_URL=$(grep "^LIVEKIT_URL=" /var/www/avatar/.env | cut -d '=' -f2 || echo "NOT SET")
  NEXT_PUBLIC_LIVEKIT_URL=$(grep "^NEXT_PUBLIC_LIVEKIT_URL=" /var/www/avatar/.env | cut -d '=' -f2 || echo "NOT SET")

  if [ "$LIVEKIT_URL" != "NOT SET" ]; then
    print_check "LIVEKIT_URL: ${LIVEKIT_URL:0:30}..."
  else
    print_error "LIVEKIT_URL not set in .env"
  fi

  if [ "$NEXT_PUBLIC_LIVEKIT_URL" != "NOT SET" ]; then
    print_check "NEXT_PUBLIC_LIVEKIT_URL: ${NEXT_PUBLIC_LIVEKIT_URL:0:30}..."
  else
    print_error "NEXT_PUBLIC_LIVEKIT_URL not set in .env"
  fi
else
  print_error ".env file not found at /var/www/avatar/.env"
  exit 1
fi

# Check 2: Docker containers
print_section "2. Docker Containers"

if command -v docker-compose &> /dev/null; then
  echo "Checking container status..."
  docker-compose -f /var/www/avatar/docker-compose.yml ps --format "table {{.Names}}\t{{.Status}}" 2>/dev/null || true

  # Check specific containers
  if docker ps | grep -q "avatar-frontend"; then
    print_success "Frontend container is running"
  else
    print_error "Frontend container is not running"
  fi
else
  print_warning "docker-compose not found in PATH"
fi

# Check 3: Environment variables in container
print_section "3. Frontend Container Environment"

if docker exec avatar-frontend env | grep -q "NEXT_PUBLIC_LIVEKIT_URL"; then
  CONTAINER_LIVEKIT_URL=$(docker exec avatar-frontend env | grep "NEXT_PUBLIC_LIVEKIT_URL" | cut -d '=' -f2)
  print_success "Frontend has NEXT_PUBLIC_LIVEKIT_URL: ${CONTAINER_LIVEKIT_URL:0:30}..."
else
  print_error "NEXT_PUBLIC_LIVEKIT_URL not set in frontend container"
fi

# Check 4: Token API endpoint
print_section "4. Token Generation Endpoint"

if curl -s http://localhost:3000/api/token -X POST \
  -H "Content-Type: application/json" \
  -d '{"roomName":"test-room","identity":"test-user"}' > /tmp/token_response.json 2>&1; then

  if grep -q "token" /tmp/token_response.json; then
    print_success "Token generation endpoint is working"
    TOKEN=$(grep -o '"token":"[^"]*' /tmp/token_response.json | cut -d '"' -f4)
    echo "  Sample token: ${TOKEN:0:50}..."
  else
    print_error "Token endpoint returned invalid response"
    cat /tmp/token_response.json
  fi
else
  print_error "Cannot reach token endpoint at http://localhost:3000/api/token"
fi

# Check 5: Network connectivity
print_section "5. Network Connectivity"

# Extract domain from URL
DOMAIN=$(echo "$NEXT_PUBLIC_LIVEKIT_URL" | sed -E 's|wss?://||; s|/.+||')

if [ -n "$DOMAIN" ]; then
  echo "Testing DNS resolution for: $DOMAIN"

  if docker exec avatar-frontend nslookup "$DOMAIN" &>/dev/null; then
    print_success "DNS resolution works for $DOMAIN"

    # Get IP addresses
    IPS=$(docker exec avatar-frontend nslookup "$DOMAIN" 2>/dev/null | grep "Address:" | tail -2 | awk '{print $2}' | tr '\n' ', ')
    echo "  Resolved to: $IPS"
  else
    print_error "Cannot resolve DNS for $DOMAIN"
    print_warning "Check internet connection or DNS settings"
  fi
else
  print_warning "Could not extract domain from NEXT_PUBLIC_LIVEKIT_URL"
fi

# Check 6: Frontend logs
print_section "6. Recent Frontend Logs"

FRONTEND_LOGS=$(docker-compose -f /var/www/avatar/docker-compose.yml logs frontend --tail 20 2>/dev/null || echo "Cannot fetch logs")

if echo "$FRONTEND_LOGS" | grep -q "error\|Error\|ERROR"; then
  print_warning "Errors found in recent logs:"
  echo "$FRONTEND_LOGS" | grep -i "error" | head -5
else
  print_success "No obvious errors in recent logs"
fi

# Summary
print_section "Summary & Recommendations"

echo ""
echo "If you're still experiencing connection issues:"
echo ""
echo "1️⃣  Open browser DevTools (F12) and check Console tab"
echo "2️⃣  Look for messages with 🔌 or ❌ emoji for details"
echo "3️⃣  Check full error message in browser console"
echo "4️⃣  Verify LiveKit credentials are still valid"
echo "5️⃣  Check internet connectivity on the host"
echo "6️⃣  Review LIVEKIT_TROUBLESHOOTING.md for detailed help"
echo ""
echo "Documentation: /var/www/avatar/docs/LIVEKIT_TROUBLESHOOTING.md"
echo ""
