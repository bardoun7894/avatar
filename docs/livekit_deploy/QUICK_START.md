# 🚀 Quick Start Deployment Guide
## Get Your LiveKit Call Center Live in 30 Minutes

This is your fast-track guide to deploying to **pro.beldify.com** (184.174.37.148).

---

## Prerequisites (5 minutes)

You need:
- ✅ Root access to server `184.174.37.148`
- ✅ Domain `pro.beldify.com` pointed to `184.174.37.148`
- ✅ All files from outputs folder
- ✅ LiveKit Cloud account (already configured)

---

## Step 1: DNS Setup (5 minutes)

```bash
# Add these records to your DNS:
A     pro.beldify.com      184.174.37.148
A     www.pro.beldify.com  184.174.37.148
```

**Verify DNS**:
```bash
dig pro.beldify.com +short
# Should show: 184.174.37.148
```

⏳ If DNS not propagated yet, wait 5-15 minutes.

---

## Step 2: Connect to Server (1 minute)

```bash
ssh root@184.174.37.148
```

---

## Step 3: Upload Files (2 minutes)

**From your local machine** (in a new terminal):

```bash
# Navigate to outputs folder
cd /path/to/outputs/

# Upload deployment files
scp .env.production root@184.174.37.148:/tmp/
scp nginx-pro.beldify.com.conf root@184.174.37.148:/tmp/
scp deploy-production.sh root@184.174.37.148:/tmp/

# Upload your application code
scp -r /path/to/your/app root@184.174.37.148:/tmp/app-code/
```

**Verify upload** (back on server):
```bash
ls -la /tmp/
# Should see: .env.production, nginx-pro.beldify.com.conf, deploy-production.sh, app-code/
```

---

## Step 4: Update Environment Variables (2 minutes)

Edit production environment file:

```bash
nano /tmp/.env.production
```

**Required changes** (use generated values):
```bash
# Generate these with:
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(64))"
python3 -c "import secrets; print('API_KEY=sk_' + secrets.token_urlsafe(48))"

# Update in .env.production:
JWT_SECRET=YOUR_GENERATED_JWT_SECRET_HERE
API_KEY=YOUR_GENERATED_API_KEY_HERE
WEBHOOK_SECRET=YOUR_GENERATED_WEBHOOK_SECRET_HERE
```

Save and exit (Ctrl+X, Y, Enter)

---

## Step 5: Run Automated Deployment (15 minutes)

```bash
# Make script executable
chmod +x /tmp/deploy-production.sh

# Run deployment
sudo /tmp/deploy-production.sh
```

**What happens**:
1. ✅ System updates
2. ✅ Installs Nginx, Python, Redis, etc.
3. ✅ Configures firewall
4. ✅ Gets SSL certificate
5. ✅ Sets up application
6. ✅ Configures Nginx
7. ✅ Creates systemd service
8. ✅ Sets up monitoring
9. ✅ Configures backups
10. ✅ Verifies everything

⏳ This takes ~15 minutes. Watch for any errors.

---

## Step 6: Verify Deployment (3 minutes)

### Check Services
```bash
sudo systemctl status call-center
sudo systemctl status nginx
sudo systemctl status redis-server
```

All should show: **active (running)** in green

### Test Endpoints
```bash
# Health check
curl https://pro.beldify.com/health
# Should return: OK

# Check SSL
curl -I https://pro.beldify.com
# Should show: HTTP/2 200
```

### Check Logs
```bash
# No errors should appear
sudo tail -20 /var/log/call-center/app.log
sudo tail -20 /var/log/nginx/pro.beldify.com-error.log
```

---

## Step 7: Test LiveKit Connection (2 minutes)

```bash
cd /var/www/call-center
source venv/bin/activate
python3 << 'EOF'
from livekit import api
import os
from dotenv import load_dotenv

load_dotenv()

token = api.AccessToken(
    os.getenv('LIVEKIT_API_KEY'),
    os.getenv('LIVEKIT_API_SECRET')
)
token.with_identity("test-user").with_grants(
    api.VideoGrants(
        room_join=True,
        room="test-room",
    )
)
print("✅ LiveKit token generated!")
print("Token:", token.to_jwt()[:50] + "...")
EOF
```

Should print: **✅ LiveKit token generated!**

---

## 🎉 Deployment Complete!

Your Call Center is now live at:
- 🌐 **https://pro.beldify.com**
- 🏥 **Health**: https://pro.beldify.com/health
- 📚 **API Docs**: https://pro.beldify.com/api/docs

---

## What's Running?

- ✅ **Nginx**: Reverse proxy with SSL
- ✅ **FastAPI**: Call center backend (port 8001)
- ✅ **Redis**: Caching layer
- ✅ **Fail2Ban**: Security protection
- ✅ **Systemd**: Auto-restart on failure
- ✅ **Certbot**: Auto-renewing SSL certificates
- ✅ **Cron Jobs**: Health checks and backups

---

## Useful Commands

```bash
# Service Management
sudo systemctl restart call-center    # Restart app
sudo systemctl status call-center     # Check status
sudo systemctl reload nginx            # Reload Nginx config

# View Logs
sudo tail -f /var/log/call-center/app.log         # App logs
sudo tail -f /var/log/call-center/error.log       # Error logs
sudo journalctl -u call-center -f                 # Live logs

# Monitor System
htop                                   # System resources
sudo ufw status                        # Firewall status
sudo fail2ban-client status            # Security status

# Check SSL
sudo certbot certificates              # Certificate info
sudo certbot renew --dry-run           # Test renewal
```

---

## Daily Monitoring (First Week)

### Morning Check (5 minutes)
```bash
# 1. Check services
sudo systemctl status call-center nginx redis-server

# 2. Review logs for errors
sudo grep -i error /var/log/call-center/app.log | tail -20

# 3. Test health endpoint
curl https://pro.beldify.com/health

# 4. Check disk space
df -h
```

### Evening Check (5 minutes)
```bash
# 1. Check access logs
sudo tail -50 /var/log/nginx/pro.beldify.com-access.log

# 2. Review error counts
sudo grep -c "ERROR" /var/log/call-center/error.log

# 3. Check resource usage
free -h
uptime
```

---

## Troubleshooting

### Service Won't Start
```bash
# Check logs
sudo journalctl -u call-center -n 50

# Check if port is in use
sudo lsof -i :8001

# Restart service
sudo systemctl restart call-center
```

### SSL Issues
```bash
# Check certificate
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal

# Test Nginx config
sudo nginx -t
```

### Connection Issues
```bash
# Test LiveKit connectivity
curl -I https://tavus-agent-project-i82x78jc.livekit.cloud

# Check environment variables
cd /var/www/call-center
cat .env | grep LIVEKIT

# Test token generation
source venv/bin/activate
python test-livekit.py
```

### High Load
```bash
# Check what's using resources
htop
ps aux --sort=-%cpu | head -10
ps aux --sort=-%mem | head -10

# Restart if needed
sudo systemctl restart call-center
```

---

## Security Checklist

- [ ] Changed JWT_SECRET from default
- [ ] Changed API_KEY from default
- [ ] Changed WEBHOOK_SECRET from default
- [ ] Firewall enabled (UFW)
- [ ] Fail2Ban running
- [ ] SSL certificate valid
- [ ] .env file permissions: 600
- [ ] Regular backups enabled

---

## Maintenance Schedule

### Daily
- Check service status
- Review error logs
- Test health endpoint

### Weekly
- Review access logs
- Check disk usage
- Test backups
- Monitor performance

### Monthly
- Update system packages
- Review security logs
- Test disaster recovery
- Optimize performance

### Quarterly
- Rotate API keys
- Security audit
- Capacity planning
- Update documentation

---

## Getting Help

### Documentation
- 📖 Full guide: `DEPLOYMENT_GUIDE.md`
- ✅ Checklist: `DEPLOYMENT_CHECKLIST.md`
- 🤖 AI prompt: `AI_AGENT_SYSTEM_PROMPT.md`

### LiveKit Resources
- 📚 Docs: https://docs.livekit.io
- 💬 Discord: https://discord.gg/livekit
- 📧 Support: https://livekit.io/support

### Server Issues
- Check logs first
- Search error messages online
- Ask in LiveKit Discord
- Contact hosting provider

---

## Next Steps

1. **Test thoroughly**
   - Make test calls
   - Try different scenarios
   - Test error conditions

2. **Setup monitoring**
   - Configure UptimeRobot
   - Setup Sentry (optional)
   - Create alert rules

3. **Document everything**
   - Note any custom changes
   - Document issues found
   - Update runbook

4. **Train team**
   - Show how to use system
   - Explain monitoring
   - Practice troubleshooting

5. **Plan scaling**
   - Monitor usage patterns
   - Identify bottlenecks
   - Plan capacity upgrades

---

## Success Indicators

✅ Services running without errors
✅ Health endpoint returns "OK"
✅ SSL certificate valid (A+ rating)
✅ No critical errors in logs
✅ Test calls complete successfully
✅ Response times < 500ms
✅ Uptime > 99.9%
✅ Monitoring alerts working
✅ Backups completing daily
✅ Team trained and confident

---

## Final Checklist

Before considering deployment complete:

- [ ] All services running
- [ ] SSL certificate valid
- [ ] DNS resolving correctly
- [ ] Firewall configured
- [ ] Backups scheduled
- [ ] Monitoring active
- [ ] Documentation updated
- [ ] Team notified
- [ ] Test calls successful
- [ ] No critical errors

---

## 🎯 Pro Tips

1. **Keep it simple first**
   - Don't overcomplicate
   - Add features gradually
   - Monitor before optimizing

2. **Monitor everything**
   - Logs are your friend
   - Set up alerts early
   - Review metrics daily

3. **Document as you go**
   - Note all changes
   - Update runbooks
   - Share with team

4. **Test, test, test**
   - Test in staging first
   - Have rollback plan
   - Keep backups current

5. **Stay updated**
   - Follow LiveKit updates
   - Update dependencies
   - Apply security patches

---

## Emergency Contacts

**Technical Issues**:
- LiveKit Support: support@livekit.io
- Your Team Lead: [Add contact]

**Server Issues**:
- Hosting Provider: [Add contact]
- DNS Provider: [Add contact]

**Security Issues**:
- Security Team: [Add contact]
- Incident Response: [Add contact]

---

## You Did It! 🎉

Your LiveKit Call Center is now **LIVE**!

- 🌟 You've deployed a production-grade system
- 🔒 With enterprise security
- 📈 Fully monitored
- 🚀 Ready to scale
- 🤖 Powered by AI

**Next**: Make your first test call and celebrate! 🎊

---

**Questions?** Review the full `DEPLOYMENT_GUIDE.md` for detailed information.

**Issues?** Check logs, review troubleshooting guide, or ask for help.

**Success?** Document what worked and share with your team!

Good luck! 💪
