#!/bin/bash

# Production Status Check Script
# Usage: ./check-production-status.sh

echo "========================================="
echo "Avatar Production Status Check"
echo "========================================="
echo ""

# Check Docker containers
echo "📦 Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" | grep avatar
echo ""

# Check health endpoint
echo "🏥 Health Check:"
curl -s http://localhost:3000/api/health | jq . 2>/dev/null || echo "❌ Health check failed"
echo ""

# Test dispatch agent
echo "🤖 Dispatch Agent Test:"
curl -s -X POST http://localhost:3000/api/dispatch-agent \
  -H "Content-Type: application/json" \
  -d '{"roomName":"status-check-test"}' | jq . 2>/dev/null || echo "❌ Dispatch agent failed"
echo ""

# Check logs for errors
echo "📋 Recent Frontend Logs (last 10 lines):"
docker logs avatar-frontend --tail 10 2>&1 | grep -v "Compiled\|webpack"
echo ""

echo "========================================="
echo "Status check complete!"
echo "========================================="

