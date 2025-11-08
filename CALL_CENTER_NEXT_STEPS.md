# Call Center Implementation - Next Steps

## Current Situation

I created the Call Center system in the **wrong directory**:
- ❌ Created in: `/var/www/avatar/callCenter/` (non-production)
- ✅ Should be in: `/var/www/avatar /callCenter/` (production, with space)

Your production system uses the **space-path directory**:
```
/var/www/avatar /  (WITH trailing space)
├── avatary/        ← Avatar video call backend
├── frontend/       ← Shared frontend
└── .git/
```

---

## Options for Call Center

### Option 1: Move to Production (Recommended)

Move the Call Center files to the correct production directory:

```bash
# Copy Call Center backend to production
cp -r /var/www/avatar/callCenter/ "/var/www/avatar /callCenter/"

# Copy Call Center frontend pages to production (merge)
cp /var/www/avatar/frontend/pages/callcenter.tsx "/var/www/avatar /frontend/pages/"
cp -r /var/www/avatar/frontend/pages/callcenter/ "/var/www/avatar /frontend/pages/"

# Copy integration hook
cp /var/www/avatar/frontend/hooks/useCallCenterAPI.ts "/var/www/avatar /frontend/hooks/"

# Add to git in production directory
cd "/var/www/avatar /"
git add callCenter/ frontend/pages/callcenter* frontend/hooks/useCallCenterAPI.ts
git commit -m "Add Call Center system (IVR, CRM, agent dashboard)"
git push
```

### Option 2: Keep Separate (Testing Only)

If keeping as separate system:
- Mark `/var/www/avatar/callCenter/` as **non-production testing**
- Do not deploy to production
- Use only for development/testing

### Option 3: Delete Non-Production Folder

If the non-space folder is not needed:
```bash
# Backup first
tar -czf /tmp/avatar-backup.tar.gz /var/www/avatar/

# Remove non-production clone
rm -rf /var/www/avatar/
```

---

## Recommended: Option 1 (Move to Production)

### Step-by-Step

#### 1. Verify Production Directory Exists
```bash
ls -la "/var/www/avatar /"
# Should show: avatary/, frontend/, .git/, etc.
```

#### 2. Copy Call Center Backend
```bash
mkdir -p "/var/www/avatar /callCenter"
cp -r /var/www/avatar/callCenter/* "/var/www/avatar /callCenter/"
```

#### 3. Copy Frontend Integration
```bash
# Copy new pages
cp /var/www/avatar/frontend/pages/callcenter.tsx "/var/www/avatar /frontend/pages/"
cp -r /var/www/avatar/frontend/pages/callcenter/ "/var/www/avatar /frontend/pages/"

# Copy hook
mkdir -p "/var/www/avatar /frontend/hooks"
cp /var/www/avatar/frontend/hooks/useCallCenterAPI.ts "/var/www/avatar /frontend/hooks/"
```

#### 4. Copy Documentation
```bash
cp /var/www/avatar/CALL_CENTER*.md "/var/www/avatar /"
cp /var/www/avatar/ARCHITECTURE*.md "/var/www/avatar /"
cp /var/www/avatar/README_CALL_CENTER.md "/var/www/avatar /"
cp /var/www/avatar/WHERE_IS_EVERYTHING.md "/var/www/avatar /"
cp /var/www/avatar/QUICK_COMMANDS.md "/var/www/avatar /"
cp /var/www/avatar/START_HERE.txt "/var/www/avatar /"
```

#### 5. Copy Startup Scripts
```bash
cp /var/www/avatar/start-call-center.* "/var/www/avatar /"
chmod +x "/var/www/avatar /start-call-center.sh"
```

#### 6. Commit to Production Repository
```bash
cd "/var/www/avatar /"

# Add all new files
git add callCenter/
git add frontend/pages/callcenter*
git add frontend/hooks/useCallCenterAPI.ts
git add CALL_CENTER*.md
git add ARCHITECTURE*.md
git add README_CALL_CENTER.md
git add WHERE_IS_EVERYTHING.md
git add QUICK_COMMANDS.md
git add START_HERE.txt
git add start-call-center.*

# Commit
git commit -m "Add Call Center system (IVR, CRM, agent dashboard, API, WebSocket)"

# Push to production
git push origin main
```

#### 7. Verify in Production
```bash
cd "/var/www/avatar /"
ls callCenter/api.py
ls frontend/pages/callcenter/
ls CALL_CENTER_GETTING_STARTED.md
```

---

## After Moving to Production

### Update Production Startup
```bash
cd "/var/www/avatar /"  # WITH space

# Start Call Center
./start-call-center.sh

# Or manually:
cd callCenter
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

# In another terminal:
cd ../frontend
npm install
npm run dev
```

### Access Production Call Center
- Frontend: http://localhost:3000/callcenter
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## Clean Up Non-Production Folder

After moving everything to production:

```bash
# Option 1: Backup first
tar -czf /tmp/avatar-non-prod-backup.tar.gz /var/www/avatar/

# Option 2: Remove
rm -rf /var/www/avatar/

# Verify only production remains
ls "/var/www/avatar /"
# Should show: avatary/, frontend/, callCenter/, .git/, docs/, etc.
```

---

## Integration with Existing Avatar System

### Frontend Routes
```
/avatar/*         → Existing Ornina Avatar pages
/callcenter/*     → New Call Center pages
```

Both systems share the same Next.js frontend on port 3000, but use different routes.

### Backend APIs
```
Avatary API:      [Existing custom port]
CallCenter API:   http://localhost:8000
```

Both run independently on different ports.

---

## Files to Keep in Non-Production (If Archiving)

These are documentation/analysis files created during development:

- `PRODUCTION_LOCATION_CLARIFICATION.md` - Keep in production for reference
- `CALL_CENTER_NEXT_STEPS.md` - Keep in production (this file)
- Analysis files from initial implementation

---

## Summary of Changes

### Current State (Before Moving)
```
/var/www/avatar/callCenter/              ← Non-production
/var/www/avatar/frontend/pages/callc*/   ← Non-production
/var/www/avatar/frontend/hooks/...ts     ← Non-production
```

### Desired State (After Moving)
```
/var/www/avatar /callCenter/             ← Production
/var/www/avatar /frontend/pages/callc*/  ← Production
/var/www/avatar /frontend/hooks/...ts    ← Production
✅ Committed to main repository
✅ Deployed to production
```

---

## Checklist

- [ ] Verify production directory exists (`/var/www/avatar /`)
- [ ] Copy Call Center backend
- [ ] Copy frontend pages and hook
- [ ] Copy documentation
- [ ] Copy startup scripts
- [ ] Commit to git in production directory
- [ ] Push to origin/main
- [ ] Verify files in production
- [ ] Delete non-production folder (or archive)
- [ ] Test Call Center system in production
- [ ] Update documentation links

---

## Support

If you need help with any step:

1. **Moving files**: Use the commands above
2. **Git operations**: Verify you're in correct directory first
3. **Testing**: Run from `/var/www/avatar /` (with space)
4. **Troubleshooting**: Check PRODUCTION_LOCATION_CLARIFICATION.md

---

**Important Note**: All work should be in `/var/www/avatar /` (WITH trailing space) for production deployment.

---

**Document Created**: November 8, 2025
**Status**: Action Plan - Pending Execution
**Next Action**: Execute Option 1 to move Call Center to production
