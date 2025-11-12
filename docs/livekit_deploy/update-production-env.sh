#!/bin/bash

# Quick script to update production environment and rebuild frontend

SERVER="root@184.174.37.148"

echo "🔄 Updating production environment..."

# Upload updated .env file
scp .env.production $SERVER:/tmp/avatar-deploy/.env
scp .env.production $SERVER:/tmp/avatar-deploy/.env.production

# Rebuild and restart frontend with new env vars
ssh $SERVER << 'ENDSSH'
cd /tmp/avatar-deploy

# Stop frontend
docker-compose stop frontend

# Rebuild frontend with new environment variables
docker-compose build --no-cache frontend

# Start frontend
docker-compose up -d frontend

# Wait for it to be healthy
echo "Waiting for frontend to be healthy..."
sleep 10

# Check status
docker-compose ps frontend
docker logs --tail 20 avatar-frontend

echo ""
echo "✅ Frontend updated with new configuration"
echo ""
echo "Test at: https://pro.beldify.com"
ENDSSH

echo ""
echo "✅ Update complete!"
