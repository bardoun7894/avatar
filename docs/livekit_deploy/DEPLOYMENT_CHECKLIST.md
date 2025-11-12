# Production Deployment Checklist
## LiveKit Call Center - pro.beldify.com

Use this checklist to ensure a smooth production deployment.

---

## Phase 1: Pre-Deployment (Before touching the server)

### DNS Configuration
- [ ] Add A record: `pro.beldify.com` → `184.174.37.148`
- [ ] Add A record: `www.pro.beldify.com` → `184.174.37.148`
- [ ] Wait for DNS propagation (check with `dig pro.beldify.com`)
- [ ] Verify DNS resolution working correctly

### Credentials Verification
- [ ] Test LiveKit Cloud credentials are valid
- [ ] Verify OpenAI API key has sufficient credits
- [ ] Test Supabase connection from local machine
- [ ] Confirm ElevenLabs API key active
- [ ] Generate new JWT_SECRET (production-ready)
- [ ] Generate new API_KEY for webhooks

### Files Preparation
- [ ] Review `.env.production` file
- [ ] Update JWT_SECRET with generated value
- [ ] Update API_KEY with generated value
- [ ] Verify all API keys are production keys (not dev/test)
- [ ] Double-check LIVEKIT_URL uses `wss://` not `ws://`
- [ ] Save secure backup of `.env.production` locally

### Application Code
- [ ] Test application locally with production .env
- [ ] Run all tests and ensure they pass
- [ ] Build/compile application if needed
- [ ] Create requirements.txt with exact versions
- [ ] Review code for any hardcoded credentials
- [ ] Remove all debug/console logs

---

## Phase 2: Server Initial Setup

### Server Access
- [ ] SSH into server: `ssh root@184.174.37.148`
- [ ] Update root password if needed
- [ ] Create deployment user (optional): `adduser deploy`
- [ ] Add deployment user to sudo: `usermod -aG sudo deploy`
- [ ] Setup SSH keys for secure access

### File Upload
- [ ] Upload `.env.production` to `/tmp/`
- [ ] Upload `nginx-pro.beldify.com.conf` to `/tmp/`
- [ ] Upload `deploy-production.sh` to `/tmp/`
- [ ] Upload application code to `/tmp/app-code/`
- [ ] Verify all files uploaded correctly: `ls -la /tmp/`

### Script Preparation
- [ ] Make deployment script executable: `chmod +x /tmp/deploy-production.sh`
- [ ] Review script contents: `cat /tmp/deploy-production.sh`
- [ ] Understand what script will do before running

---

## Phase 3: Automated Deployment

### Run Deployment Script
- [ ] Execute: `sudo /tmp/deploy-production.sh`
- [ ] Monitor output for errors
- [ ] Note any warnings that appear
- [ ] Wait for "Deployment Complete!" message

### Verify Each Component
- [ ] Check Nginx status: `sudo systemctl status nginx`
- [ ] Check Call Center status: `sudo systemctl status call-center`
- [ ] Check Redis status: `sudo systemctl status redis-server`
- [ ] Check Fail2Ban status: `sudo systemctl status fail2ban`
- [ ] Verify SSL certificate: `sudo certbot certificates`

---

## Phase 4: Post-Deployment Verification

### SSL Certificate
- [ ] Visit `https://pro.beldify.com` in browser
- [ ] Verify SSL padlock shows
- [ ] Check certificate details (valid, correct domain)
- [ ] Test auto-renewal: `sudo certbot renew --dry-run`

### API Endpoints
- [ ] Test health endpoint: `curl https://pro.beldify.com/health`
- [ ] Should return: "OK"
- [ ] Test API docs: `curl https://pro.beldify.com/api/docs`
- [ ] Should return HTML page

### LiveKit Connection
- [ ] Create test script to generate token
- [ ] Verify token generation succeeds
- [ ] Test WebSocket connection to LiveKit Cloud
- [ ] Confirm audio track can be published

### Database Connection
- [ ] Test Supabase connection from server
- [ ] Run simple SELECT query
- [ ] Verify database credentials work
- [ ] Check connection pooling

### Logs
- [ ] Check application logs: `sudo tail -50 /var/log/call-center/app.log`
- [ ] Look for startup messages
- [ ] Verify no critical errors
- [ ] Check Nginx logs: `sudo tail -50 /var/log/nginx/pro.beldify.com-access.log`

---

## Phase 5: Security Hardening

### Firewall
- [ ] Verify UFW is enabled: `sudo ufw status`
- [ ] Confirm only needed ports are open (22, 80, 443, 8001)
- [ ] Test that other ports are blocked

### Fail2Ban
- [ ] Check Fail2Ban is running: `sudo fail2ban-client status`
- [ ] Verify SSH jail is active
- [ ] Verify Nginx jails are active
- [ ] Review ban thresholds are appropriate

### File Permissions
- [ ] Check .env file: `ls -la /var/www/call-center/.env`
- [ ] Should be: `-rw------- (600) www-data:www-data`
- [ ] Verify application directory: `ls -la /var/www/call-center/`
- [ ] Should be: `drwxr-xr-x (755) www-data:www-data`

### Secrets Rotation
- [ ] Document all API keys used
- [ ] Set calendar reminder to rotate keys in 90 days
- [ ] Create procedure for key rotation
- [ ] Test key rotation process

---

## Phase 6: Monitoring Setup

### Health Checks
- [ ] Verify cron job created: `crontab -l`
- [ ] Should see health check running every 5 minutes
- [ ] Wait 5 minutes and check log: `tail /var/log/call-center/health-check.log`
- [ ] Verify automatic restart works

### Log Rotation
- [ ] Check logrotate config: `cat /etc/logrotate.d/call-center`
- [ ] Test manually: `sudo logrotate -f /etc/logrotate.d/call-center`
- [ ] Verify old logs are compressed

### Backups
- [ ] Verify backup script: `cat /usr/local/bin/call-center-backup.sh`
- [ ] Run manual backup: `sudo /usr/local/bin/call-center-backup.sh`
- [ ] Check backup created: `ls -lh /var/backups/call-center/`
- [ ] Verify cron job scheduled: `crontab -l`

### External Monitoring
- [ ] Setup UptimeRobot for `https://pro.beldify.com/health`
- [ ] Configure alert email
- [ ] Set check interval to 5 minutes
- [ ] Test alert by stopping service

---

## Phase 7: Performance Testing

### Load Testing
- [ ] Test with 10 concurrent requests
- [ ] Test with 50 concurrent requests
- [ ] Test with 100 concurrent requests
- [ ] Monitor CPU and memory during tests

### Response Time
- [ ] Measure `/health` endpoint response time
- [ ] Should be < 100ms
- [ ] Measure API endpoint response times
- [ ] Should be < 500ms for most operations

### WebSocket Performance
- [ ] Test WebSocket connection stability
- [ ] Run connection for 5 minutes without drops
- [ ] Test reconnection after disconnect
- [ ] Verify no memory leaks over time

---

## Phase 8: Integration Testing

### Full Call Flow
- [ ] Initiate test call from client
- [ ] Verify LiveKit connection establishes
- [ ] Test audio is transmitted
- [ ] Verify speech recognition works
- [ ] Test TTS audio plays correctly
- [ ] Confirm transcript is saved
- [ ] Verify call ends gracefully

### Database Operations
- [ ] Test customer data retrieval
- [ ] Verify order lookup works
- [ ] Test search functionality
- [ ] Confirm data is saved correctly

### Webhooks
- [ ] Test webhook endpoint receives events
- [ ] Verify webhook signature validation
- [ ] Test webhook retry logic
- [ ] Confirm events are logged

---

## Phase 9: Documentation

### Server Documentation
- [ ] Document server IP and credentials location
- [ ] List all installed services and versions
- [ ] Document firewall rules
- [ ] Note any custom configurations

### Runbook Creation
- [ ] Document restart procedure
- [ ] Create troubleshooting guide
- [ ] Document backup/restore process
- [ ] Create emergency contact list

### Access Management
- [ ] Document who has server access
- [ ] List all API keys and their purpose
- [ ] Create secure password manager entry
- [ ] Share access info with team securely

---

## Phase 10: Go-Live

### Final Checks
- [ ] All previous phases completed
- [ ] No critical errors in logs
- [ ] All tests passing
- [ ] Team briefed on new system
- [ ] Monitoring alerts configured

### Gradual Rollout
- [ ] Start with internal testing (team calls)
- [ ] Move to beta users (small group)
- [ ] Monitor metrics closely
- [ ] Gradually increase traffic
- [ ] Monitor for issues

### Communication
- [ ] Notify stakeholders of go-live
- [ ] Update status page
- [ ] Announce new system to customers
- [ ] Prepare support team

---

## Phase 11: Post-Launch Monitoring (First 24 Hours)

### Hour 1
- [ ] Monitor logs every 5 minutes
- [ ] Check health endpoint
- [ ] Verify calls are completing successfully
- [ ] Monitor error rates

### Hour 6
- [ ] Review access logs
- [ ] Check error logs for patterns
- [ ] Verify backups running
- [ ] Monitor server resources (CPU, RAM, disk)

### Hour 24
- [ ] Generate metrics report
- [ ] Review all alerts
- [ ] Check call quality
- [ ] Verify no degradation

---

## Phase 12: Week 1 Maintenance

### Daily Tasks
- [ ] Review logs for errors
- [ ] Check health check results
- [ ] Monitor API rate limits
- [ ] Verify backups completing

### Weekly Tasks
- [ ] Review performance metrics
- [ ] Analyze call patterns
- [ ] Check disk space usage
- [ ] Update documentation if needed

---

## Common Issues Checklist

If deployment fails, check:

### Service Won't Start
- [ ] Check logs: `sudo journalctl -u call-center -n 100`
- [ ] Verify .env file exists and readable
- [ ] Check Python virtual environment
- [ ] Verify port 8001 not in use
- [ ] Test dependencies: `pip list`

### SSL Certificate Issues
- [ ] DNS resolving correctly
- [ ] Port 80 accessible from internet
- [ ] Certbot can write to /var/www
- [ ] No firewall blocking Let's Encrypt

### Connection Issues
- [ ] LiveKit Cloud accessible: `curl -I https://tavus-agent-project-i82x78jc.livekit.cloud`
- [ ] API keys correct in .env
- [ ] Token generation working
- [ ] No proxy/firewall blocking WebSocket

### Database Issues
- [ ] Supabase URL correct
- [ ] Database credentials valid
- [ ] IP not blocked by Supabase
- [ ] Connection pool not exhausted

---

## Success Criteria

Deployment is successful when:

✅ All services running without errors
✅ SSL certificate valid and auto-renewing
✅ Health endpoint returns "OK"
✅ API documentation accessible
✅ LiveKit connection establishes
✅ Test calls complete successfully
✅ Logs show no critical errors
✅ Monitoring alerts working
✅ Backups running automatically
✅ Security hardening complete

---

## Emergency Rollback

If critical issues occur:

1. **Stop the service**
   ```bash
   sudo systemctl stop call-center
   ```

2. **Restore from backup**
   ```bash
   sudo tar -xzf /var/backups/call-center/backup_LATEST.tar.gz -C /tmp/restore
   sudo cp /tmp/restore/var/www/call-center/.env /var/www/call-center/.env
   ```

3. **Restart service**
   ```bash
   sudo systemctl start call-center
   ```

4. **Verify health**
   ```bash
   curl https://pro.beldify.com/health
   ```

5. **Investigate issue**
   - Review logs
   - Identify root cause
   - Plan fix
   - Test in staging

---

## Contact Information

**Server Provider**: [Your hosting provider]
**DNS Provider**: [Your DNS provider]
**LiveKit Support**: https://livekit.io/support
**Emergency Contact**: [Your emergency contact]

---

## Next Steps After Deployment

1. **Week 1**: Monitor closely, fix any issues
2. **Week 2**: Optimize performance, tune parameters
3. **Month 1**: Review metrics, plan improvements
4. **Month 3**: Security audit, key rotation
5. **Month 6**: Capacity planning, scaling evaluation

---

## Deployment Sign-Off

- [ ] Technical lead reviewed
- [ ] Security team approved
- [ ] Operations team briefed
- [ ] Documentation complete
- [ ] Monitoring active
- [ ] Backups verified

**Deployed by**: ___________________
**Date**: ___________________
**Time**: ___________________
**Version**: ___________________

---

## Notes

Use this space for deployment-specific notes, issues encountered, or lessons learned:

```
[Your notes here]
```

---

**Remember**: Take your time with each step. It's better to be thorough than fast. Good luck with your deployment! 🚀
