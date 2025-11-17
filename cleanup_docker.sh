#!/bin/bash
# Script to clean up Docker containers and images while preserving avatar-deploy_avatar-network

echo "🔍 Identifying Docker resources to clean up..."

# Check if avatar-deploy_avatar-network exists
if ! docker network inspect avatar-deploy_avatar-network &>/dev/null; then
  echo "❌ Error: avatar-deploy_avatar-network doesn't exist. Aborting."
  exit 1
fi

echo "✅ Found avatar-deploy_avatar-network - this will be preserved"

# Stop and remove containers connected to production networks (except those on avatar-deploy_avatar-network)
echo "🧹 Stopping and removing production containers..."

# Find containers on prod network
PROD_CONTAINERS=$(docker container ls -a --filter network=avatar-prod_avatar-network -q)

if [ -n "$PROD_CONTAINERS" ]; then
  echo "🛑 Stopping production containers..."
  docker stop $PROD_CONTAINERS
  echo "🗑️ Removing production containers..."
  docker rm $PROD_CONTAINERS
else
  echo "ℹ️ No containers found on avatar-prod_avatar-network"
fi

# Remove production network (except avatar-deploy_avatar-network)
echo "🧹 Removing production networks (except avatar-deploy_avatar-network)..."
if docker network ls | grep -q "avatar-prod_avatar-network"; then
  echo "🗑️ Removing avatar-prod_avatar-network..."
  docker network rm avatar-prod_avatar-network
fi

# Remove production Docker images (tagged with latest)
echo "🧹 Removing production images..."
# List of production image prefixes
PROD_IMAGES=("ornina-avatar-backend:latest" "ornina-avatar-frontend:latest" "ornina-avatar-callcenter:latest" "avatar-backend:latest" "avatar-frontend:latest" "avatar-callcenter:latest")

for IMAGE in "${PROD_IMAGES[@]}"; do
  if docker images -q $IMAGE &>/dev/null; then
    echo "🗑️ Removing image: $IMAGE"
    docker rmi $IMAGE
  else
    echo "ℹ️ Image not found: $IMAGE"
  fi
done

# Remove dangling images (untagged)
echo "🧹 Cleaning up dangling images..."
if docker images -f "dangling=true" -q | grep -q .; then
  docker rmi $(docker images -f "dangling=true" -q)
else
  echo "ℹ️ No dangling images to remove"
fi

echo "✨ Cleanup completed. The avatar-deploy_avatar-network has been preserved."
echo "📊 Current Docker status:"
echo "----------------------"
echo "🔹 Networks:"
docker network ls | grep avatar
echo "🔹 Containers:"
docker ps -a
echo "🔹 Images:"
docker images | grep -E 'ornina|avatar'

echo ""
echo "💡 To start fresh with avatar-deploy, use: docker-compose -f your-deploy-compose.yml up -d"
