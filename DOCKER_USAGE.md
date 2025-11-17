# Docker Usage Guide

## Overview

This project uses separate Docker configurations for **development** and **production** deployments.

## Development (Testing)

**File:** `docker-compose.yml`

**Image Tags:** `:dev`
- `ornina-avatar-backend:dev`
- `ornina-avatar-frontend:dev`
- `ornina-avatar-callcenter:dev`

**Usage:**
```bash
# Build and start dev containers
docker-compose up --build

# Start in background
docker-compose up -d --build

# Stop containers
docker-compose down

# View logs
docker-compose logs -f backend
```

**Features:**
- Code mounted as volumes for hot-reload
- Uses `.env` files from respective directories
- Restart policy: `unless-stopped`
- Suitable for local development and testing

## Production (Deployment)

**File:** `docker-compose.prod.yml`

**Image Tags:** `:latest`
- `ornina-avatar-backend:latest`
- `ornina-avatar-frontend:latest`
- `ornina-avatar-callcenter:latest`

**Usage:**
```bash
# Build and start production containers
docker-compose -f docker-compose.prod.yml up --build -d

# Stop production containers
docker-compose -f docker-compose.prod.yml down

# View logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

**Features:**
- No code volumes (code baked into image)
- Uses `.env.production` file
- Restart policy: `always`
- Optimized for production deployment

## Image Management

**List all images:**
```bash
docker images | grep ornina-avatar
```

**Remove dev images:**
```bash
docker rmi ornina-avatar-backend:dev ornina-avatar-frontend:dev ornina-avatar-callcenter:dev
```

**Remove production images:**
```bash
docker rmi ornina-avatar-backend:latest ornina-avatar-frontend:latest ornina-avatar-callcenter:latest
```

**Clean up unused images:**
```bash
docker image prune -a
```

## Key Differences

| Feature | Development | Production |
|---------|------------|------------|
| Image Tag | `:dev` | `:latest` |
| Code Volumes | ✅ Mounted | ❌ Baked in |
| Env File | `./avatary/.env` | `./.env.production` |
| Restart Policy | `unless-stopped` | `always` |
| Use Case | Local testing | Deployment |

