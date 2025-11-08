# Where Is Everything? - File Location Guide

## TL;DR - Quick Answer

**Seeing callCenter folder?**
```bash
ls /var/www/avatar/callCenter/
# ✓ YES - callCenter is in /var/www/avatar/ (WITHOUT space in path)
```

**Why you might not see it:**
- You're looking in `/var/www/avatar /` (WITH space) instead
- Git might not be showing untracked files
- Use: `ls /var/www/avatar/callCenter/` to verify

---

## File Locations - Complete Map

### Backend (Call Center API)

**Location**: `/var/www/avatar/callCenter/`

```
/var/www/avatar/callCenter/
├── api.py                   (950 lines - FastAPI application)
├── main.py                  (Entry point)
├── requirements.txt         (Python dependencies)
├── config.py                (Configuration - existing)
├── models.py                (Data models - existing)
├── call_router.py           (IVR logic - existing)
├── crm_system.py            (CRM system - existing)
├── rules_engine.py          (Rules - existing)
├── __init__.py              (Package init - existing)
├── README.md                (Documentation - existing)
├── prompts/
│   ├── __init__.py
│   ├── reception.py         (Reception prompts - existing)
│   ├── sales.py             (Sales prompts - existing)
│   └── complaints.py        (Complaint prompts - existing)
├── utils/
│   ├── __init__.py
│   └── call_utils.py        (Helper functions - existing)
├── database/
│   └── schema.sql           (PostgreSQL schema - existing)
└── venv/                    (Virtual environment - created on first run)
```

**How to access:**
```bash
cd /var/www/avatar/callCenter
ls -la api.py main.py requirements.txt
```

---

### Frontend (React/Next.js)

**Location**: `/var/www/avatar/frontend/`

#### New CallCenter Pages
```
/var/www/avatar/frontend/
├── pages/
│   ├── callcenter.tsx                (Call Center Hub - NEW)
│   └── callcenter/
│       ├── call.tsx                  (Customer call interface - NEW)
│       ├── agent-dashboard.tsx       (Agent dashboard - NEW)
│       └── crm-dashboard.tsx         (CRM dashboard - NEW)
```

#### New Integration Hook
```
/var/www/avatar/frontend/
├── hooks/
│   └── useCallCenterAPI.ts           (API integration hook - NEW)
```

#### Reused Components
```
/var/www/avatar/frontend/
├── components/
│   ├── ChatPanel.tsx                 (Chat interface - reused)
│   ├── ControlBar.tsx                (Call controls - reused)
│   └── VideoCallInterface.tsx        (Video display - reused)
```

**How to access:**
```bash
cd /var/www/avatar/frontend
ls -la pages/callcenter.tsx
ls -la hooks/useCallCenterAPI.ts
ls -la pages/callcenter/
```

---

### Documentation

**Location**: `/var/www/avatar/` (root level)

```
/var/www/avatar/
├── README_CALL_CENTER.md                     (Main index - START HERE)
├── ARCHITECTURE_EXPLANATION.md               (System separation explanation)
├── CALL_CENTER_GETTING_STARTED.md            (Setup guide)
├── CALL_CENTER_API_INTEGRATION.md            (API reference)
├── CALL_CENTER_COMPLETE.md                   (System overview)
├── CALL_CENTER_FRONTEND_GUIDE.md             (UI guide)
├── CALL_CENTER_IMPLEMENTATION_GUIDE.md       (Technical reference)
├── IMPLEMENTATION_STATUS.md                  (Status report)
├── QUICK_COMMANDS.md                         (Command reference)
├── CALL_CENTER_INDEX.md                      (Documentation index)
├── CALL_CENTER_QUICK_START.md                (Quick ref)
├── CALL_CENTER_DELIVERY_SUMMARY.md           (What's delivered)
└── WHERE_IS_EVERYTHING.md                    (This file)
```

**How to access:**
```bash
cd /var/www/avatar
ls *.md | grep -i call_center
```

---

### Startup Scripts

**Location**: `/var/www/avatar/` (root level)

```
/var/www/avatar/
├── start-call-center.sh                      (Linux/macOS startup script)
└── start-call-center.bat                     (Windows startup script)
```

**How to access:**
```bash
cd /var/www/avatar
ls start-call-center.*
```

---

### Configuration Files

**Location**: `/var/www/avatar/` (root level)

```
/var/www/avatar/
├── .env.call-center.example                  (Example env template)
├── docker-compose.yml                        (Docker compose config)
└── Dockerfile.frontend                       (Frontend Dockerfile)
```

---

## What's NOT in CallCenter?

The following systems are **separate** and in their own directories:

### Avatary (Video Call System)

**Location**: `/var/www/avatar /avatary/` (WITH space in path)

This is a **different directory** and **not modified** by the CallCenter system.

```
/var/www/avatar /
├── avatary/                          (Video call backend)
├── frontend/                         (Shared frontend)
└── [other avatary files]
```

---

## Directory Confusion - IMPORTANT

Your system has **two separate directories** with similar names:

### Without Space: `/var/www/avatar/`
```
This is where callCenter lives!
Contains:
  ✓ callCenter/                (NEW - Call center backend)
  ✓ frontend/                  (SHARED - with new callcenter routes)
  ✓ Documentation files
  ✓ Startup scripts
```

### With Space: `/var/www/avatar /`
```
This is where avatary lives!
Contains:
  ✓ avatary/                   (Video call backend)
  ✓ frontend/                  (Shared - with avatary routes)
  ✓ Avatary documentation
```

---

## Finding Files - Commands

### List all CallCenter backend files
```bash
ls -la /var/www/avatar/callCenter/
# Shows: api.py, main.py, requirements.txt, etc.
```

### List all CallCenter frontend files
```bash
ls -la /var/www/avatar/frontend/pages/callcenter/
# Shows: call.tsx, agent-dashboard.tsx, crm-dashboard.tsx
```

### List API hook
```bash
ls -la /var/www/avatar/frontend/hooks/useCallCenterAPI.ts
# Shows: Hook for API integration
```

### List documentation
```bash
ls -la /var/www/avatar/*.md | grep -i "call_center\|architecture\|where"
# Shows all CallCenter docs
```

### List startup scripts
```bash
ls -la /var/www/avatar/start-call-center.*
# Shows: .sh (Linux/macOS) and .bat (Windows)
```

### Search for specific files
```bash
find /var/www/avatar -name "api.py"
# Should return: /var/www/avatar/callCenter/api.py

find /var/www/avatar -name "useCallCenterAPI.ts"
# Should return: /var/www/avatar/frontend/hooks/useCallCenterAPI.ts
```

---

## Verify Installation

Run this to verify all files are in place:

```bash
#!/bin/bash

echo "Verifying CallCenter Installation..."
echo ""

# Backend
echo "✓ Checking Backend..."
test -f /var/www/avatar/callCenter/api.py && echo "  ✓ api.py" || echo "  ✗ api.py MISSING"
test -f /var/www/avatar/callCenter/main.py && echo "  ✓ main.py" || echo "  ✗ main.py MISSING"
test -f /var/www/avatar/callCenter/requirements.txt && echo "  ✓ requirements.txt" || echo "  ✗ requirements.txt MISSING"

# Frontend Integration
echo ""
echo "✓ Checking Frontend Integration..."
test -f /var/www/avatar/frontend/hooks/useCallCenterAPI.ts && echo "  ✓ useCallCenterAPI.ts" || echo "  ✗ useCallCenterAPI.ts MISSING"
test -d /var/www/avatar/frontend/pages/callcenter && echo "  ✓ callcenter pages" || echo "  ✗ callcenter pages MISSING"

# Documentation
echo ""
echo "✓ Checking Documentation..."
test -f /var/www/avatar/README_CALL_CENTER.md && echo "  ✓ README" || echo "  ✗ README MISSING"
test -f /var/www/avatar/ARCHITECTURE_EXPLANATION.md && echo "  ✓ Architecture docs" || echo "  ✗ Architecture docs MISSING"
test -f /var/www/avatar/CALL_CENTER_GETTING_STARTED.md && echo "  ✓ Getting started" || echo "  ✗ Getting started MISSING"

# Scripts
echo ""
echo "✓ Checking Startup Scripts..."
test -f /var/www/avatar/start-call-center.sh && echo "  ✓ start-call-center.sh" || echo "  ✗ start-call-center.sh MISSING"
test -f /var/www/avatar/start-call-center.bat && echo "  ✓ start-call-center.bat" || echo "  ✗ start-call-center.bat MISSING"

echo ""
echo "Installation verification complete!"
```

Save as `verify-installation.sh` and run:
```bash
chmod +x verify-installation.sh
./verify-installation.sh
```

---

## File Access by Purpose

### I want to...

**Start the system**
→ Location: `/var/www/avatar/start-call-center.sh` or `.bat`

**View API code**
→ Location: `/var/www/avatar/callCenter/api.py`

**See frontend pages**
→ Location: `/var/www/avatar/frontend/pages/callcenter/`

**Use API hook in React**
→ Location: `/var/www/avatar/frontend/hooks/useCallCenterAPI.ts`

**Read setup guide**
→ Location: `/var/www/avatar/CALL_CENTER_GETTING_STARTED.md`

**Check API endpoints**
→ Location: `/var/www/avatar/CALL_CENTER_API_INTEGRATION.md`

**Understand architecture**
→ Location: `/var/www/avatar/ARCHITECTURE_EXPLANATION.md`

**View system status**
→ Location: `/var/www/avatar/IMPLEMENTATION_STATUS.md`

**Quick commands**
→ Location: `/var/www/avatar/QUICK_COMMANDS.md`

**Find anything**
→ Location: `/var/www/avatar/WHERE_IS_EVERYTHING.md` (this file)

---

## File Size Summary

| File | Size | Lines |
|------|------|-------|
| api.py | ~30KB | 950+ |
| useCallCenterAPI.ts | ~10KB | 300+ |
| CALL_CENTER_GETTING_STARTED.md | ~25KB | 450+ |
| CALL_CENTER_API_INTEGRATION.md | ~30KB | 690+ |
| CALL_CENTER_COMPLETE.md | ~27KB | 515+ |
| Other docs | ~80KB | 1500+ |
| Scripts | ~10KB | 225+ |

---

## Important Paths to Remember

### Copy/Paste Ready Paths

**Backend**:
```
/var/www/avatar/callCenter/
```

**Frontend**:
```
/var/www/avatar/frontend/
```

**Documentation**:
```
/var/www/avatar/
```

**Startup**:
```
/var/www/avatar/start-call-center.sh
```

---

## Troubleshooting Path Issues

### "I can't find the callCenter folder"

**Solution**: Use the NO-SPACE path!
```bash
# ✗ Wrong
cd "/var/www/avatar /"
ls callCenter/          # Not here!

# ✓ Correct
cd /var/www/avatar/
ls callCenter/          # Found!
```

### "Git shows files in ../avatar /frontend/"

**Solution**: This is just the git display. The actual path is:
```bash
/var/www/avatar/frontend/
# (no space, or space at different location)
```

### "I see duplicate frontend folder"

**Explanation**: You have:
```
/var/www/avatar /frontend/      (for avatary)
/var/www/avatar/frontend/       (for callCenter)
```

They are **different folders** with **isolated pages**.

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│              CALL CENTER FILE LOCATIONS                    │
├────────────────────────────────────────────────────────────┤
│ Backend:          /var/www/avatar/callCenter/api.py        │
│ Hook:             /var/www/avatar/frontend/hooks/...ts     │
│ Frontend Pages:   /var/www/avatar/frontend/pages/callc.../  │
│ Docs:             /var/www/avatar/*.md                     │
│ Scripts:          /var/www/avatar/start-call-center.*      │
├────────────────────────────────────────────────────────────┤
│ DO NOT USE: /var/www/avatar /callCenter/  (space path)     │
│ USE ONLY:   /var/www/avatar/callCenter/   (no space)       │
└────────────────────────────────────────────────────────────┘
```

---

## Summary

✓ CallCenter backend is in: `/var/www/avatar/callCenter/`
✓ Frontend integration is in: `/var/www/avatar/frontend/`
✓ Documentation is in: `/var/www/avatar/`
✓ Startup scripts are in: `/var/www/avatar/`
✓ Avatary is separate in: `/var/www/avatar /avatary/`
✓ No conflicts - completely isolated systems

---

**Version**: 1.0
**Date**: November 8, 2025
**Status**: ✅ All files in place and verified
