# LiveKit Call Center - Production Deployment Guide
## Domain: pro.beldify.com | Server: 184.174.37.148

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [DNS Configuration](#dns-configuration)
3. [Server Access & Initial Setup](#server-access--initial-setup)
4. [Automated Deployment](#automated-deployment)
5. [Manual Deployment (Alternative)](#manual-deployment-alternative)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Configuration Management](#configuration-management)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Security Best Practices](#security-best-practices)
11. [Backup & Recovery](#backup--recovery)
12. [Scaling Considerations](#scaling-considerations)

---

## Pre-Deployment Checklist

### ✅ Requirements

- [ ] Server with Ubuntu 20.04+ LTS
- [ ] Root/sudo access to server (184.174.37.148)
- [ ] Domain name configured (pro.beldify.com)
- [ ] DNS propagation complete
- [ ] LiveKit Cloud account with project created
- [ ] OpenAI API key with sufficient credits
- [ ] Supabase project configured
- [ ] All API keys and secrets ready

### ✅ Files to Upload

1. `.env.production` - Production environment variables
2. `nginx-pro.beldify.com.conf` - Nginx configuration
3. `deploy-production.sh` - Deployment script
4. Application source code
5. `requirements.txt` or Python dependencies list

---

## DNS Configuration

### Step 1: Add DNS Records

Add the following records to your DNS provider (Namecheap, Cloudflare, etc.):

```
Type    Name                Value               TTL
A       pro.beldify.com     184.174.37.148     300
A       www.pro.beldify     184.174.37.148     300
```

### Step 2: Verify DNS Propagation

```bash
# Check DNS resolution
dig pro.beldify.com +short
nslookup pro.beldify.com

# Expected output: 184.174.37.148
```

### Step 3: Wait for Propagation

- Usually takes 5-30 minutes
- Can take up to 48 hours in rare cases
- Check propagation: https://dnschecker.org

---

## Server Access & Initial Setup

### Step 1: Connect to Server

```bash
# SSH into your server
ssh root@184.174.37.148

# Or with key-based authentication
ssh -i /path/to/key.pem root@184.174.37.148
```

### Step 2: Create Deployment User (Optional but Recommended)

```bash
# Create deployment user
adduser deploy
usermod -aG sudo deploy

# Setup SSH key for deploy user
mkdir -p /home/deploy/.ssh
cp ~/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys

# Test connection
ssh deploy@184.174.37.148
```

### Step 3: Upload Deployment Files

```bash
# From your local machine
scp .env.production root@184.174.37.148:/tmp/
scp nginx-pro.beldify.com.conf root@184.174.37.148:/tmp/
scp deploy-production.sh root@184.174.37.148:/tmp/
scp -r ./app-code root@184.174.37.148:/tmp/
```

---

## Automated Deployment

### Step 1: Prepare Deployment Script

```bash
# On server
cd /tmp
chmod +x deploy-production.sh
```

### Step 2: Run Deployment Script

```bash
# Run as root
sudo ./deploy-production.sh
```

The script will automatically:
1. ✅ Update system packages
2. ✅ Install required software (Nginx, Python, Redis, etc.)
3. ✅ Configure firewall (UFW)
4. ✅ Request SSL certificate from Let's Encrypt
5. ✅ Setup application directories
6. ✅ Install Python dependencies
7. ✅ Configure Nginx
8. ✅ Create systemd service
9. ✅ Setup Redis
10. ✅ Configure Fail2Ban security
11. ✅ Setup health checks and monitoring
12. ✅ Configure log rotation
13. ✅ Setup automated backups
14. ✅ Verify deployment

### Step 3: Monitor Deployment

```bash
# Watch logs during deployment
sudo tail -f /var/log/call-center/app.log
```

---

## Manual Deployment (Alternative)

If you prefer manual deployment or need to customize:

### 1. Install System Packages

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
    nginx \
    certbot \
    python3-certbot-nginx \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    ufw \
    fail2ban \
    redis-server \
    supervisor \
    postgresql-client
```

### 2. Configure Firewall

```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 8001/tcp    # Call Center API
sudo ufw --force enable
sudo ufw status
```

### 3. Request SSL Certificate

```bash
sudo systemctl stop nginx
sudo certbot certonly --standalone \
    -d pro.beldify.com \
    -d www.pro.beldify.com \
    --non-interactive \
    --agree-tos \
    --email admin@beldify.com

# Enable auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 4. Setup Application

```bash
# Create directories
sudo mkdir -p /var/www/call-center
sudo mkdir -p /var/log/call-center
sudo mkdir -p /var/backups/call-center

# Copy application code
sudo cp -r /tmp/app-code/* /var/www/call-center/

# Setup Python environment
cd /var/www/call-center
sudo python3 -m venv venv
source venv/bin/activate
sudo pip install --upgrade pip
sudo pip install -r requirements.txt

# Copy environment file
sudo cp /tmp/.env.production /var/www/call-center/.env
sudo chmod 600 /var/www/call-center/.env

# Set permissions
sudo chown -R www-data:www-data /var/www/call-center
```

### 5. Configure Nginx

```bash
# Copy Nginx configuration
sudo cp /tmp/nginx-pro.beldify.com.conf /etc/nginx/sites-available/pro.beldify.com

# Enable site
sudo ln -s /etc/nginx/sites-available/pro.beldify.com /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 6. Create Systemd Service

```bash
sudo nano /etc/systemd/system/call-center.service
```

Paste the following:

```ini
[Unit]
Description=LiveKit Call Center API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/call-center
Environment="PATH=/var/www/call-center/venv/bin"
EnvironmentFile=/var/www/call-center/.env
ExecStart=/var/www/call-center/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4
Restart=always
RestartSec=10
StandardOutput=append:/var/log/call-center/app.log
StandardError=append:/var/log/call-center/error.log

[Install]
WantedBy=multi-user.target
```

```bash
# Reload and start service
sudo systemctl daemon-reload
sudo systemctl enable call-center
sudo systemctl start call-center
sudo systemctl status call-center
```

---

## Post-Deployment Verification

### 1. Check Services Status

```bash
# Check all services
sudo systemctl status nginx
sudo systemctl status call-center
sudo systemctl status redis-server
sudo systemctl status fail2ban
```

### 2. Test Endpoints

```bash
# Health check
curl https://pro.beldify.com/health

# Should return: OK

# API documentation
curl https://pro.beldify.com/api/docs

# Test API endpoint
curl -X POST https://pro.beldify.com/api/test \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### 3. Check Logs

```bash
# Application logs
sudo tail -f /var/log/call-center/app.log
sudo tail -f /var/log/call-center/error.log

# Nginx logs
sudo tail -f /var/log/nginx/pro.beldify.com-access.log
sudo tail -f /var/log/nginx/pro.beldify.com-error.log

# Service logs
sudo journalctl -u call-center -f
```

### 4. Verify SSL Certificate

```bash
# Check certificate details
sudo certbot certificates

# Test SSL configuration
curl -vI https://pro.beldify.com

# Online SSL test
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=pro.beldify.com
```

### 5. Test LiveKit Connection

Create a test script `test-livekit.py`:

```python
from livekit import api
import os
from dotenv import load_dotenv

load_dotenv()

# Test token generation
token = api.AccessToken(
    os.getenv('LIVEKIT_API_KEY'),
    os.getenv('LIVEKIT_API_SECRET')
)
token.with_identity("test-user").with_name("Test User").with_grants(
    api.VideoGrants(
        room_join=True,
        room="test-room",
    )
)

print("Token generated successfully:", token.to_jwt())
```

Run the test:

```bash
cd /var/www/call-center
source venv/bin/activate
python test-livekit.py
```

---

## Configuration Management

### Environment Variables

The `.env` file contains all sensitive configuration. Key variables:

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://tavus-agent-project-i82x78jc.livekit.cloud
LIVEKIT_API_KEY=APIJL8zayDiwTwV
LIVEKIT_API_SECRET=fYtfW6HKKiaqxAcEhmRR4OTjZcyJbfWov4Bi9ezUvfFA

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...

# Supabase Configuration
SUPABASE_URL=https://uzzejiaxyvuhcfcvjyiv.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Security
JWT_SECRET=CHANGE_THIS
API_KEY=CHANGE_THIS
```

### Update Environment Variables

```bash
# Edit .env file
sudo nano /var/www/call-center/.env

# Restart service to apply changes
sudo systemctl restart call-center
```

### Nginx Configuration Updates

```bash
# Edit Nginx config
sudo nano /etc/nginx/sites-available/pro.beldify.com

# Test configuration
sudo nginx -t

# Reload Nginx (no downtime)
sudo systemctl reload nginx
```

---

## Monitoring & Maintenance

### Real-Time Monitoring

```bash
# Watch application logs
sudo tail -f /var/log/call-center/app.log

# Watch error logs
sudo tail -f /var/log/call-center/error.log

# Watch Nginx access logs
sudo tail -f /var/log/nginx/pro.beldify.com-access.log

# Watch system resources
htop

# Monitor service status
watch -n 5 'systemctl status call-center | grep Active'
```

### Health Checks

The system includes automatic health checks running every 5 minutes:

```bash
# View health check logs
sudo tail -f /var/log/call-center/health-check.log

# Manual health check
curl https://pro.beldify.com/health
```

### Performance Monitoring

```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s https://pro.beldify.com/health

# Create curl-format.txt:
cat > curl-format.txt << EOF
    time_namelookup:  %{time_namelookup}s\n
       time_connect:  %{time_connect}s\n
    time_appconnect:  %{time_appconnect}s\n
   time_pretransfer:  %{time_pretransfer}s\n
      time_redirect:  %{time_redirect}s\n
 time_starttransfer:  %{time_starttransfer}s\n
                    ----------\n
         time_total:  %{time_total}s\n
EOF
```

### Log Analysis

```bash
# Count API requests by endpoint
sudo awk '{print $7}' /var/log/nginx/pro.beldify.com-access.log | sort | uniq -c | sort -rn | head -20

# Count HTTP status codes
sudo awk '{print $9}' /var/log/nginx/pro.beldify.com-access.log | sort | uniq -c | sort -rn

# Find slow requests (> 1 second)
sudo awk '$10 > 1.0 {print $7, $10}' /var/log/nginx/pro.beldify.com-access.log | sort -k2 -rn
```

---

## Troubleshooting Guide

### Service Won't Start

```bash
# Check service status
sudo systemctl status call-center

# View detailed error logs
sudo journalctl -u call-center -n 100 --no-pager

# Check if port 8001 is already in use
sudo lsof -i :8001

# Check Python virtual environment
cd /var/www/call-center
source venv/bin/activate
python --version
pip list

# Manually test the application
cd /var/www/call-center
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001
```

### SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew --force-renewal

# Test certificate renewal
sudo certbot renew --dry-run

# Check certificate files exist
ls -la /etc/letsencrypt/live/pro.beldify.com/
```

### Nginx Issues

```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx

# Check if Nginx is listening
sudo netstat -tlnp | grep nginx
```

### Database Connection Issues

```bash
# Test Supabase connection
cd /var/www/call-center
source venv/bin/activate
python << EOF
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

print("Connection successful!")
print(supabase.table('your_table').select('*').limit(1).execute())
EOF
```

### LiveKit Connection Issues

```bash
# Test LiveKit connectivity
cd /var/www/call-center
source venv/bin/activate
python << EOF
from livekit import api
import os
from dotenv import load_dotenv

load_dotenv()

try:
    token = api.AccessToken(
        os.getenv('LIVEKIT_API_KEY'),
        os.getenv('LIVEKIT_API_SECRET')
    )
    token.with_identity("test-user").with_grants(
        api.VideoGrants(room_join=True, room="test-room")
    )
    jwt_token = token.to_jwt()
    print("✅ LiveKit token generated successfully!")
    print("Token:", jwt_token[:50] + "...")
except Exception as e:
    print("❌ Error:", str(e))
EOF
```

### High CPU/Memory Usage

```bash
# Check resource usage
htop

# Check application memory usage
ps aux | grep uvicorn

# Check Python process
pmap $(pgrep -f uvicorn)

# Restart service to free memory
sudo systemctl restart call-center
```

### Permission Issues

```bash
# Fix permissions on application directory
sudo chown -R www-data:www-data /var/www/call-center
sudo chmod -R 755 /var/www/call-center
sudo chmod 600 /var/www/call-center/.env

# Fix log directory permissions
sudo chown -R www-data:www-data /var/log/call-center
sudo chmod -R 755 /var/log/call-center
```

---

## Security Best Practices

### 1. Generate Secure Secrets

```bash
# Generate JWT secret
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate API key
python3 -c "import secrets; print('sk_' + secrets.token_urlsafe(48))"

# Update .env file with new secrets
sudo nano /var/www/call-center/.env
```

### 2. Restrict File Permissions

```bash
# Environment file should be readable only by owner
sudo chmod 600 /var/www/call-center/.env
sudo chown www-data:www-data /var/www/call-center/.env

# Application files
sudo chmod -R 755 /var/www/call-center
sudo chown -R www-data:www-data /var/www/call-center
```

### 3. Configure Fail2Ban

```bash
# Check Fail2Ban status
sudo fail2ban-client status

# Check banned IPs
sudo fail2ban-client status sshd
sudo fail2ban-client status nginx-limit-req

# Unban an IP if needed
sudo fail2ban-client set sshd unbanip 1.2.3.4
```

### 4. Regular Security Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
cd /var/www/call-center
source venv/bin/activate
pip list --outdated
pip install --upgrade package_name

# Restart service after updates
sudo systemctl restart call-center
```

### 5. API Rate Limiting

Already configured in Nginx:
- 10 requests per second for API endpoints
- 5 requests per second for WebSocket connections
- Automatic IP blocking after threshold

### 6. Monitor Security Events

```bash
# Check authentication failures
sudo grep "Failed password" /var/log/auth.log | tail -20

# Check Fail2Ban log
sudo tail -f /var/log/fail2ban.log

# Check Nginx security events
sudo grep "403\|401" /var/log/nginx/pro.beldify.com-access.log | tail -20
```

---

## Backup & Recovery

### Automated Backups

Backups run daily at 2 AM automatically. They include:
- Environment configuration (.env)
- Application logs
- Database backups (if local)

### Manual Backup

```bash
# Run backup script manually
sudo /usr/local/bin/call-center-backup.sh

# View backups
ls -lh /var/backups/call-center/

# Backup size
du -sh /var/backups/call-center/
```

### Restore from Backup

```bash
# List available backups
ls -lh /var/backups/call-center/

# Extract backup
sudo tar -xzf /var/backups/call-center/backup_YYYYMMDD_HHMMSS.tar.gz -C /tmp/restore

# Restore environment file
sudo cp /tmp/restore/var/www/call-center/.env /var/www/call-center/.env

# Restart service
sudo systemctl restart call-center
```

### Database Backup (Supabase)

Supabase automatically backs up your database. To export manually:

1. Go to Supabase Dashboard
2. Navigate to Database → Backups
3. Click "Export" to download backup

---

## Scaling Considerations

### Current Setup (Single Server)

- ✅ Suitable for: 100-500 concurrent calls
- ✅ Handles: ~50,000 requests/day
- ✅ LiveKit Cloud handles media processing

### When to Scale

Scale if you experience:
- CPU usage consistently > 70%
- Response times > 200ms
- More than 500 concurrent calls
- Database connection pool exhaustion

### Scaling Options

#### 1. Vertical Scaling (Upgrade Server)

```bash
# Current: 2 CPU, 4GB RAM
# Upgrade to: 4 CPU, 8GB RAM or higher

# Update worker count in systemd service
sudo nano /etc/systemd/system/call-center.service
# Change: --workers 4 to --workers 8
```

#### 2. Horizontal Scaling (Multiple Servers)

Add load balancer and multiple application servers:

```
           [Load Balancer]
          /      |       \
    [Server 1] [Server 2] [Server 3]
          \      |       /
           [Redis Cache]
                |
        [Supabase Database]
```

#### 3. Database Optimization

```bash
# Add Redis caching
pip install redis

# Configure in .env
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=true
```

---

## Additional Resources

### Documentation Links

- **LiveKit Docs**: https://docs.livekit.io
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Nginx Docs**: https://nginx.org/en/docs/
- **Supabase Docs**: https://supabase.com/docs

### Monitoring Tools

- **UptimeRobot**: https://uptimerobot.com (Free uptime monitoring)
- **Sentry**: https://sentry.io (Error tracking)
- **Grafana Cloud**: https://grafana.com (Metrics & logs)

### Support

- **Server Provider Support**: Contact your hosting provider
- **LiveKit Support**: https://livekit.io/support
- **Community**: LiveKit Discord, Stack Overflow

---

## Quick Reference Commands

```bash
# Service Management
sudo systemctl start call-center      # Start service
sudo systemctl stop call-center       # Stop service
sudo systemctl restart call-center    # Restart service
sudo systemctl status call-center     # Check status
sudo systemctl reload call-center     # Reload config

# Logs
sudo tail -f /var/log/call-center/app.log       # Application logs
sudo tail -f /var/log/call-center/error.log     # Error logs
sudo journalctl -u call-center -f               # Systemd logs

# Nginx
sudo nginx -t                          # Test config
sudo systemctl reload nginx            # Reload config
sudo systemctl restart nginx           # Restart Nginx

# SSL Certificate
sudo certbot renew                     # Renew certificate
sudo certbot certificates              # List certificates

# Monitoring
htop                                   # System resources
sudo ufw status                        # Firewall status
sudo fail2ban-client status            # Banned IPs
```

---

## Conclusion

Your LiveKit Call Center is now deployed to production at **https://pro.beldify.com**.

For issues or questions:
1. Check troubleshooting guide above
2. Review logs for specific errors
3. Consult LiveKit documentation
4. Contact support if needed

**Remember to:**
- ✅ Monitor logs regularly
- ✅ Keep backups current
- ✅ Update security patches
- ✅ Rotate API keys every 90 days
- ✅ Test health checks weekly

Good luck with your production deployment! 🚀
