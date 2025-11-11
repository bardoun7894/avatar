# Docker Setup Checklist

Use this checklist to verify everything is properly configured.

## ✅ Pre-Setup Checklist

### Docker Installation
- [ ] Docker Desktop installed: `docker --version`
- [ ] Docker Compose installed: `docker-compose --version`
- [ ] Docker daemon running

### Credential Files
- [ ] `avatary/.env` exists and contains credentials
- [ ] `callCenter/.env` exists and contains credentials
- [ ] `frontend/.env.local` exists (or will use defaults)

### Environment Variables Verified
- [ ] TAVUS_API_KEY in avatary/.env
- [ ] OPENAI_API_KEY in avatary/.env
- [ ] SUPABASE_URL in callCenter/.env
- [ ] DATABASE_URL in callCenter/.env
- [ ] LIVEKIT_URL available somewhere

## ✅ Docker Setup Checklist

### Files Created
- [ ] `callCenter/Dockerfile` - ✅ Created
- [ ] `docker-compose.yml` updated - ✅ Updated
- [ ] `.env.example` created - ✅ Created
- [ ] `avatary/.env.example` created - ✅ Created
- [ ] `callCenter/.env.example` created - ✅ Created
- [ ] `frontend/.env.example` created - ✅ Created
- [ ] `docker-start.sh` created - ✅ Created
- [ ] Documentation created - ✅ Created

### Frontend Structure
- [ ] Frontend reorganized into separate apps
- [ ] `frontend/apps/avatar/` folder created
- [ ] `frontend/apps/callcenter/` folder created
- [ ] `frontend/apps/shared/` folder created
- [ ] `frontend/STRUCTURE.md` created

## ✅ Pre-Launch Checklist

### Port Availability
- [ ] Port 3000 available (Frontend): `lsof -i :3000`
- [ ] Port 8000 available (Call Center): `lsof -i :8000`
- [ ] Port 8080 available (Avatar Backend): `lsof -i :8080`
- [ ] Port 6379 available (Redis): `lsof -i :6379`

### Permissions
- [ ] `docker-start.sh` is executable: `ls -la docker-start.sh`
- [ ] Can read `.env` files: `cat avatary/.env | head`
- [ ] Can write to project directory: `touch test.txt && rm test.txt`

### Docker Compose Configuration
- [ ] `docker-compose.yml` is valid: `docker-compose config`
- [ ] All services defined in config:
  - [ ] `frontend` service
  - [ ] `backend` (avatary) service
  - [ ] `callcenter` service
  - [ ] `redis` service
- [ ] Volume mounts are correct
- [ ] Network is defined: `avatar-network`

## ✅ Launch Checklist

### Option A: Automated Script
```bash
cd /var/www/avatar
./docker-start.sh
```

**Verification:**
- [ ] Script runs without errors
- [ ] Docker images build successfully
- [ ] All services start
- [ ] Services are healthy (wait for health checks)

### Option B: Manual Commands
```bash
docker-compose build
docker-compose up -d
```

**Verification:**
- [ ] `docker-compose build` completes
- [ ] `docker-compose up -d` starts without errors

## ✅ Post-Launch Verification

### Service Status
```bash
docker-compose ps
```
- [ ] All 4 containers are running:
  - [ ] `avatar-frontend` (Up)
  - [ ] `avatar-backend` (Up)
  - [ ] `avatar-callcenter` (Up)
  - [ ] `avatar-redis` (Up)

### Health Checks
```bash
docker-compose ps
```
- [ ] Frontend health check passing
- [ ] Backend health check passing
- [ ] Call Center health check passing
- [ ] Redis health check passing

### Credential Verification
```bash
# Check credentials are loaded in containers
docker exec avatar-backend env | grep OPENAI_API_KEY
docker exec avatar-callcenter env | grep DATABASE_URL
```
- [ ] `OPENAI_API_KEY` present in backend
- [ ] `DATABASE_URL` present in call center
- [ ] `TAVUS_API_KEY` present in backend
- [ ] `SUPABASE_URL` present in call center

### Service Accessibility

#### Frontend
```bash
curl http://localhost:3000
```
- [ ] Frontend responds (HTTP 200)
- [ ] Can access in browser: http://localhost:3000

#### Avatar Backend
```bash
curl http://localhost:8080
```
- [ ] Backend accessible on port 8080

#### Call Center API
```bash
curl http://localhost:8000/health
```
- [ ] Health endpoint responds

#### Redis
```bash
redis-cli -p 6379 ping
```
- [ ] Returns "PONG"

### Log Verification
```bash
docker-compose logs frontend | head -20
docker-compose logs backend | head -20
docker-compose logs callcenter | head -20
```
- [ ] Frontend logs show initialization
- [ ] Backend logs show successful startup
- [ ] Call Center logs show database connection
- [ ] No ERROR or FAILED messages

## ✅ Usage Verification

### Access Applications
- [ ] Open http://localhost:3000
- [ ] Navigate to Avatar app
- [ ] Navigate to Call Center app
- [ ] Verify components load correctly

### Check Service Communication
```bash
# Frontend can reach backends
docker-compose exec frontend curl http://backend:8080
docker-compose exec frontend curl http://callcenter:8000

# Backends can reach Redis
docker-compose exec backend redis-cli -h redis ping
docker-compose exec callcenter redis-cli -h redis ping
```
- [ ] Frontend → Backend communication works
- [ ] Frontend → Call Center communication works
- [ ] Backend → Redis communication works
- [ ] Call Center → Redis communication works

### Monitor Logs in Real-Time
```bash
docker-compose logs -f
```
- [ ] Can see live logs from all services
- [ ] No errors appearing
- [ ] Services communicating successfully

## ✅ Troubleshooting Checklist

### If Services Won't Start

**Check Dockerfile syntax:**
```bash
docker build callCenter/
```
- [ ] Build succeeds without syntax errors

**Check docker-compose.yml:**
```bash
docker-compose config
```
- [ ] Configuration validates without errors

**Check logs:**
```bash
docker-compose logs [service_name]
```
- [ ] Identify specific error messages

### If Credentials Not Loading

**Verify env_file paths:**
```bash
docker-compose config | grep env_file
```
- [ ] Paths are correct and relative

**Check file permissions:**
```bash
ls -la avatary/.env
ls -la callCenter/.env
```
- [ ] Files are readable

**Check file content:**
```bash
cat avatary/.env | grep -v "^#" | grep -v "^$"
```
- [ ] File has actual content
- [ ] Variables are properly formatted

### If Ports Are Occupied

**Find process using port:**
```bash
lsof -i :3000
```
- [ ] Identify conflicting process
- [ ] Stop it or use different port

**Use different port:**
```bash
docker-compose -f docker-compose.yml -e "FRONTEND_PORT=3001" up -d
```
- [ ] Services start on alternative port

### If Services Exit Immediately

**Check service logs:**
```bash
docker logs avatar-callcenter
```
- [ ] Read error message in logs

**Verify entrypoint:**
```bash
grep "CMD\|ENTRYPOINT" callCenter/Dockerfile
```
- [ ] Entry command is correct

**Rebuild without cache:**
```bash
docker-compose build --no-cache callcenter
docker-compose up callcenter
```
- [ ] Service starts successfully

## ✅ Final Verification

Run this command to verify everything is working:

```bash
# Check all services running
docker-compose ps | grep -c "Up"
# Should output: 4 (all services)

# Check no errors in logs
docker-compose logs | grep -i "error" | wc -l
# Should output: 0 (no errors)

# Verify frontend accessible
curl -s http://localhost:3000 | head -c 100
# Should output HTML content
```

**All checks passing?** ✅ **Congratulations! Docker setup is complete!**

## ✅ Regular Maintenance Checklist

### Daily
- [ ] Services running: `docker-compose ps`
- [ ] Check logs for errors: `docker-compose logs --tail=100`
- [ ] Monitor resource usage: `docker stats`

### Weekly
- [ ] Update images: `docker-compose pull`
- [ ] Rebuild with new bases: `docker-compose build`
- [ ] Check for security updates

### Monthly
- [ ] Review logs for patterns
- [ ] Update documentation
- [ ] Backup important data
- [ ] Test disaster recovery

## Quick Reference Commands

```bash
# Start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f [service_name]

# Stop
docker-compose down

# Restart
docker-compose restart [service_name]

# Access container
docker-compose exec [service_name] bash

# Remove everything
docker-compose down -v
```

---

**Date Started**: ___________
**Setup Completed**: ___________
**Verified By**: ___________
**Issues Encountered**: ___________
**Resolution**: ___________

