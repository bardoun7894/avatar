#!/bin/bash

# ============================================================================
# Avatar Production Deployment Script
# Target: pro.beldify.com (184.174.37.148)
# ============================================================================

set -e

SERVER="root@184.174.37.148"
REMOTE_DIR="/tmp/avatar-deploy"

echo "🚀 Avatar Production Deployment"
echo "================================"
echo ""
echo "Target Server: 184.174.37.148"
echo "Domain: pro.beldify.com"
echo ""

# Step 1: Create deployment package
echo "📦 Step 1: Creating deployment package..."
mkdir -p /tmp/avatar-deploy-package
cd /var/www/avatar

# Copy application code
echo "  - Copying application code..."
rsync -av --exclude='node_modules' --exclude='venv' --exclude='.git' \
  --exclude='__pycache__' --exclude='.next' --exclude='logs' \
  avatary/ /tmp/avatar-deploy-package/avatary/

rsync -av --exclude='node_modules' --exclude='venv' --exclude='.git' \
  --exclude='__pycache__' --exclude='logs' \
  callCenter/ /tmp/avatar-deploy-package/callCenter/

rsync -av --exclude='node_modules' --exclude='.git' --exclude='.next' \
  frontend/ /tmp/avatar-deploy-package/frontend/

# Copy configuration files
echo "  - Copying configuration files..."
cp .env.production /tmp/avatar-deploy-package/.env
cp docker-compose.prod.yml /tmp/avatar-deploy-package/docker-compose.yml
cp -r docs/livekit_deploy /tmp/avatar-deploy-package/

echo "✅ Deployment package created"
echo ""

# Step 2: Upload to server
echo "📤 Step 2: Uploading to server..."
ssh $SERVER "mkdir -p $REMOTE_DIR"

rsync -avz --progress /tmp/avatar-deploy-package/ $SERVER:$REMOTE_DIR/

echo "✅ Files uploaded successfully"
echo ""

# Step 3: Run deployment on server
echo "🔧 Step 3: Running deployment on server..."
echo ""

ssh $SERVER << 'ENDSSH'
cd /tmp/avatar-deploy
echo "Current directory: $(pwd)"
echo "Files present:"
ls -la

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Stop existing containers if any
echo "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build and start services
echo "Building Docker images..."
docker-compose build

echo "Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 30

# Check service status
echo ""
echo "Service Status:"
docker-compose ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Access your application at:"
echo "  Frontend: http://184.174.37.148:3000"
echo "  Call Center API: http://184.174.37.148:8000"
echo "  Avatar Backend: http://184.174.37.148:8080"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
ENDSSH

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Test the application: http://184.174.37.148:3000"
echo "2. Check logs: ssh $SERVER 'cd $REMOTE_DIR && docker-compose logs -f'"
echo "3. Setup domain and SSL (optional): Follow docs/livekit_deploy/DEPLOYMENT_GUIDE.md"
echo ""
