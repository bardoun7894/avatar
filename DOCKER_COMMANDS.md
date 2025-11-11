# Docker Commands - Quick Reference Card

**Call Center Service**: `avatar-callcenter` (port 8000)

---

## Essential Commands

### Build & Deploy

```bash
# Build call center image with all fixes
docker-compose build callcenter

# Start call center container
docker-compose up -d callcenter

# Start all services
docker-compose up -d

# View live logs
docker-compose logs -f callcenter

# Stop and remove containers
docker-compose down
```

### Monitor

```bash
# Check service status
docker-compose ps

# View detailed logs (last 50 lines)
docker-compose logs --tail=50 callcenter

# Follow logs in real-time
docker-compose logs -f callcenter

# Check resource usage
docker stats avatar-callcenter

# Inspect container details
docker inspect avatar-callcenter
```

### Access Container

```bash
# Open shell in container
docker-compose exec callcenter /bin/bash

# Run Python commands
docker-compose exec callcenter python3 -c "print('Hello')"

# Check installed packages
docker-compose exec callcenter pip list | grep livekit

# Check environment variables
docker-compose exec callcenter env | grep LIVEKIT
```

---

## Troubleshooting Commands

### Container Issues

```bash
# Container won't start?
docker-compose logs callcenter | grep ERROR

# Port already in use?
lsof -i :8000

# Health check failing?
docker-compose exec callcenter curl http://localhost:8000/health

# Check disk space
docker system df
```

### Connection Issues

```bash
# Test OpenAI API
docker-compose exec callcenter python3 -c "
import openai, os
openai.api_key = os.getenv('OPENAI_API_KEY')
print('✅ OpenAI API accessible')
"

# Test Supabase
docker-compose exec callcenter python3 -c "
from supabase import create_client
import os
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
client = create_client(url, key)
print('✅ Supabase connected')
"

# Test LiveKit
docker-compose exec callcenter python3 -c "
import os
url = os.getenv('LIVEKIT_URL')
print(f'LiveKit URL: {url}')
"
```

### Database Issues

```bash
# Connect to PostgreSQL in container
docker-compose exec callcenter psql \
  -h ${SUPABASE_HOST} \
  -U postgres \
  -d postgres

# Check if tables exist in Supabase:
docker-compose exec callcenter python3 -c "
from supabase import create_client
import os
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
tables = client.table('customers').select('*').limit(0).execute()
print('✅ Customers table exists')
"
```

---

## Cleanup Commands

### Remove Everything (⚠️ WARNING)

```bash
# Stop all containers and remove volumes (data loss!)
docker-compose down -v

# Remove only stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Clean up everything
docker system prune -a --volumes
```

### Safe Cleanup

```bash
# Stop containers (keep data)
docker-compose stop

# Remove containers (keep volumes and images)
docker-compose down

# Just remove stopped containers
docker container prune
```

---

## Advanced Commands

### Scaling

```bash
# Run 3 instances of call center
docker-compose up -d --scale callcenter=3

# Note: Set ports to range in docker-compose:
# ports:
#   - "8000-8002:8000"
```

### Build Options

```bash
# Build without cache (clean rebuild)
docker-compose build --no-cache callcenter

# Build with build args
docker-compose build --build-arg PYTHON_VERSION=3.12 callcenter
```

### Exec Advanced

```bash
# Run command and exit
docker-compose exec -T callcenter python3 api.py

# Run with environment override
docker-compose exec -e LOG_LEVEL=DEBUG callcenter python3 api.py

# Run as different user
docker-compose exec -u root callcenter apt-get update
```

---

## Docker Compose File Validation

```bash
# Validate docker-compose.yml syntax
docker-compose config --quiet

# Show expanded config (with all overrides)
docker-compose config

# List all services
docker-compose config --services
```

---

## Logs & Debugging

### Advanced Log Options

```bash
# Show logs with timestamps
docker-compose logs -t callcenter

# Follow logs with 100 lines of history
docker-compose logs -f --tail=100 callcenter

# Show logs since 10 minutes ago
docker-compose logs --since 10m callcenter

# Grep logs for errors
docker-compose logs callcenter | grep ERROR

# Save logs to file
docker-compose logs callcenter > callcenter.log
```

### Real-time Monitoring

```bash
# Watch logs and stats simultaneously
watch -n 1 'docker-compose logs --tail=5 callcenter && docker stats avatar-callcenter --no-stream'

# Monitor resource usage
docker stats --no-stream

# Watch container events
docker events --filter "container=avatar-callcenter"
```

---

## Production Commands

### Health Monitoring

```bash
# Check health status
curl http://localhost:8000/health

# Monitor in loop
watch -n 2 'curl -s http://localhost:8000/health | python3 -m json.tool'

# From inside container
docker-compose exec callcenter curl http://localhost:8000/health
```

### Graceful Restart

```bash
# Restart specific container gracefully
docker-compose restart callcenter

# Graceful reload (stop, remove, start)
docker-compose stop callcenter
docker-compose up -d callcenter
```

### Backup & Restore

```bash
# Backup logs
tar -czf callcenter-logs-backup.tar.gz callCenter/logs/

# Backup volumes
docker run --rm \
  -v avatar-callcenter-data:/data \
  -v $(pwd):/backup \
  busybox tar czf /backup/backup.tar.gz /data

# Restore from backup
docker run --rm \
  -v avatar-callcenter-data:/data \
  -v $(pwd):/backup \
  busybox tar xzf /backup/backup.tar.gz -C /
```

---

## CI/CD Integration

### Jenkins Example

```bash
# Jenkinsfile
pipeline {
  stages {
    stage('Build') {
      steps {
        sh 'docker-compose build callcenter'
      }
    }
    stage('Test') {
      steps {
        sh 'docker-compose exec -T callcenter python3 -m pytest'
      }
    }
    stage('Deploy') {
      steps {
        sh 'docker-compose up -d callcenter'
      }
    }
  }
}
```

### GitHub Actions Example

```bash
# .github/workflows/deploy.yml
- name: Deploy Call Center
  run: |
    docker-compose build callcenter
    docker-compose up -d callcenter
    sleep 5
    curl http://localhost:8000/health
```

---

## Useful Aliases

Add to `.bashrc` or `.zshrc`:

```bash
# Quick commands
alias dc='docker-compose'
alias dcs='docker-compose stop'
alias dcu='docker-compose up -d'
alias dcl='docker-compose logs -f'
alias dcp='docker-compose ps'
alias dcb='docker-compose build'
alias dcd='docker-compose down'

# Call center specific
alias cc-logs='docker-compose logs -f callcenter'
alias cc-shell='docker-compose exec callcenter /bin/bash'
alias cc-health='curl http://localhost:8000/health'
alias cc-restart='docker-compose restart callcenter'
```

Then use:

```bash
cc-logs              # Follow call center logs
cc-shell             # Enter container shell
cc-health            # Check health
cc-restart           # Restart service
```

---

## Common Issues & Quick Fixes

### Port 8000 Already in Use

```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port in docker-compose.yml:
# ports:
#   - "8001:8000"
```

### Container Exits Immediately

```bash
# Check exit code
docker-compose logs callcenter

# 139 = segfault
# 137 = killed (OOM)
# 1 = general error

# Fix: Check logs and environment
docker-compose exec callcenter env | grep -i LIVEKIT
```

### Out of Disk Space

```bash
# Check space
docker system df

# Clean up
docker system prune -a --volumes

# Or increase Docker disk:
# Docker Desktop → Preferences → Resources → Disk Image Size
```

### Slow Performance

```bash
# Check resource limits
docker stats

# Increase limits in docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       cpus: '2'
#       memory: 2G
```

---

## Reference

- **Docker Docs**: https://docs.docker.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **Docker CLI**: https://docs.docker.com/engine/reference/commandline/

---

**Print this page and keep it handy!** 📋

Most used command:
```bash
docker-compose logs -f callcenter
```
