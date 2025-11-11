#!/bin/bash

# ========================================
# Ornina Avatar - Production Deployment Script
# Deployment: https://184.174.37.148:3000/
# ========================================

set -e

echo "🚀 Ornina Avatar - Production Deployment"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PRODUCTION_IP="184.174.37.148"
PRODUCTION_DOMAIN="ornina.avatar"

# Step 1: Verify environment
echo -e "${YELLOW}[1/6] Verifying production environment...${NC}"
if [ ! -f ".env.production" ]; then
    echo -e "${RED}ERROR: .env.production not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Production environment file found${NC}"

# Step 2: Build Docker images
echo ""
echo -e "${YELLOW}[2/6] Building Docker images for production...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache
echo -e "${GREEN}✓ Docker images built successfully${NC}"

# Step 3: Stop existing services
echo ""
echo -e "${YELLOW}[3/6] Stopping existing services...${NC}"
docker-compose -f docker-compose.prod.yml down || true
sleep 2
echo -e "${GREEN}✓ Existing services stopped${NC}"

# Step 4: Start production services
echo ""
echo -e "${YELLOW}[4/6] Starting production services...${NC}"
docker-compose -f docker-compose.prod.yml up -d
sleep 15
echo -e "${GREEN}✓ Services started${NC}"

# Step 5: Verify services
echo ""
echo -e "${YELLOW}[5/6] Verifying service health...${NC}"

# Check frontend
if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend is healthy (port 3000)${NC}"
else
    echo -e "${RED}✗ Frontend is not responding${NC}"
fi

# Check backend
if curl -s -f http://localhost:8080 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is healthy (port 8080)${NC}"
else
    echo -e "${RED}✗ Backend is not responding${NC}"
fi

# Check redis
if docker exec avatar-redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is healthy (port 6379)${NC}"
else
    echo -e "${RED}✗ Redis is not responding${NC}"
fi

# Step 6: Display production information
echo ""
echo -e "${YELLOW}[6/6] Production Deployment Summary${NC}"
echo "=========================================="
echo ""
echo -e "${GREEN}Production Services Running:${NC}"
echo "  • Frontend (Next.js):    https://${PRODUCTION_IP}:3000/"
echo "  • Backend (LiveKit):     http://${PRODUCTION_IP}:8080"
echo "  • Call Center API:       http://${PRODUCTION_IP}:8000"
echo "  • Redis Cache:           ${PRODUCTION_IP}:6379"
echo ""
echo -e "${GREEN}Environment:${NC}"
echo "  • Configuration: .env.production"
echo "  • Compose File:  docker-compose.prod.yml"
echo ""
echo -e "${GREEN}Access the application:${NC}"
echo "  • URL: https://${PRODUCTION_IP}:3000/"
echo "  • Default Language: Arabic (ar)"
echo ""
echo -e "${GREEN}Useful Commands:${NC}"
echo "  • View logs:      docker-compose -f docker-compose.prod.yml logs -f"
echo "  • Stop services:  docker-compose -f docker-compose.prod.yml down"
echo "  • Check status:   docker-compose -f docker-compose.prod.yml ps"
echo ""
echo -e "${GREEN}✓ Production deployment complete!${NC}"
echo ""
