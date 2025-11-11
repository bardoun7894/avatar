# System Architecture & Conflict Analysis

## The Issue: Directory Space

Your system has **two separate directories**:

1. **`/var/www/avatar/`** (WITHOUT space)
2. **`/var/www/avatar /`** (WITH space at the end)

This is why you weren't seeing the callCenter folder - it's in the no-space directory!

---

## Directory Structure

### Path WITHOUT Space: `/var/www/avatar/`
```
/var/www/avatar/
├── callCenter/              ← CALL CENTER BACKEND (New)
│   ├── api.py
│   ├── main.py
│   ├── requirements.txt
│   ├── config.py
│   ├── models.py
│   ├── call_router.py
│   ├── crm_system.py
│   ├── rules_engine.py
│   ├── prompts/
│   ├── utils/
│   ├── database/
│   └── [other modules]
│
├── frontend/                ← SHARED FRONTEND
│   ├── pages/
│   │   ├── [avatary pages]
│   │   ├── callcenter.tsx   ← NEW (Call Center Hub)
│   │   └── callcenter/      ← NEW
│   │       ├── call.tsx
│   │       ├── agent-dashboard.tsx
│   │       └── crm-dashboard.tsx
│   ├── hooks/
│   │   └── useCallCenterAPI.ts  ← NEW
│   ├── components/
│   ├── package.json
│   └── [other files]
│
└── [documentation & config files]
```

### Path WITH Space: `/var/www/avatar /`
```
/var/www/avatar /
├── avatary/                 ← AVATARY BACKEND (Video Call System)
│   ├── backend/
│   ├── frontend/
│   ├── [avatar-related code]
│   └── [other modules]
│
├── frontend/                ← COPY/LINK to shared frontend
│   └── [same as no-space version]
│
└── [other avatary files]
```

---

## System Separation

### ✅ Two Completely Independent Systems

#### System 1: AVATAR (Video Call System)
- **Location**: `/var/www/avatar /avatary/`
- **Purpose**: Avatar video calling with Tavus
- **Backend**: Python (avatary)
- **Frontend**: React (in `/var/www/avatar /frontend/`)
- **Ports**: Custom (check avatary config)
- **Features**:
  - Video call interface
  - Avatar management
  - Speech synthesis
  - Tavus integration

#### System 2: CALL CENTER (IVR + CRM System)
- **Location**: `/var/www/avatar/callCenter/`
- **Purpose**: Intelligent call center with IVR, routing, CRM
- **Backend**: Python (FastAPI)
- **Frontend**: React (in `/var/www/avatar/frontend/`)
- **Ports**: 8000 (API) & 3000 (Frontend)
- **Features**:
  - 9-stage IVR system
  - Smart call routing
  - Ticket management
  - Agent dashboard
  - Real-time WebSocket updates

---

## NO CONFLICTS - Here's Why

### 1. Different Directories
```
avatary code:       /var/www/avatar /avatary/
callCenter code:    /var/www/avatar/callCenter/
They are in different parent directories (one has a space)
```

### 2. Different Ports
```
Avatary:      Uses its own configured ports
CallCenter:   Uses ports 8000 (API) and 3000 (Frontend)
No port conflicts
```

### 3. Different Backend Technologies
```
Avatary:      Custom Python backend
CallCenter:   FastAPI backend
Different frameworks, can coexist
```

### 4. Different Frontend Routes
```
Avatary:      Uses /avatar/* routes
CallCenter:   Uses /callcenter/* routes
No route conflicts
```

### 5. Shared Frontend - But Isolated Pages
```
Frontend code location: /var/www/avatar/frontend/

Pages for Avatary:
  /                  ← avatary main page
  /avatar/*          ← avatary routes
  [other routes]

Pages for CallCenter:
  /callcenter        ← Call Center Hub (NEW)
  /callcenter/call   ← Customer call interface (NEW)
  /callcenter/agent-dashboard
  /callcenter/crm-dashboard

No route conflicts - different root paths
```

---

## How to Run Both Systems

### Important: They Use Different Directories!

#### Run Avatary (Video Call System)
```bash
cd "/var/www/avatar /"  # WITH space
# Follow avatary setup instructions
```

#### Run Call Center (IVR + CRM System)
```bash
cd /var/www/avatar/     # WITHOUT space
chmod +x start-call-center.sh
./start-call-center.sh
```

---

## Backend Port Configuration

### Current Setup

**CallCenter Backend**: Port 8000
```bash
# Terminal 1
cd /var/www/avatar/callCenter
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
# → Running on http://localhost:8000
```

**CallCenter Frontend**: Port 3000
```bash
# Terminal 2
cd /var/www/avatar/frontend
npm install
npm run dev
# → Running on http://localhost:3000
```

### If You Run Avatary Separately

Check avatary's port configuration (usually different ports):
```bash
cd "/var/www/avatar /"
# Run avatary as per its instructions
# Ports: [Check avatary docs]
```

---

## Conflict Prevention Checklist

✅ **Ports**: CallCenter uses 8000 & 3000 (standard)
✅ **Routes**: Avatary uses `/avatar/*`, CallCenter uses `/callcenter/*`
✅ **Directories**: Separated with space in directory name
✅ **Databases**: Ready to use separate databases
✅ **APIs**: Separate FastAPI instance for CallCenter
✅ **Frontend**: Shared code, but isolated pages
✅ **Dependencies**: Separate Python environments (venv)

---

## File Locations Quick Reference

### CallCenter Files (NO SPACE path)

**Backend**:
```
/var/www/avatar/callCenter/api.py
/var/www/avatar/callCenter/main.py
/var/www/avatar/callCenter/requirements.txt
/var/www/avatar/callCenter/config.py
/var/www/avatar/callCenter/models.py
/var/www/avatar/callCenter/call_router.py
/var/www/avatar/callCenter/crm_system.py
/var/www/avatar/callCenter/rules_engine.py
```

**Frontend Integration**:
```
/var/www/avatar/frontend/hooks/useCallCenterAPI.ts
/var/www/avatar/frontend/pages/callcenter.tsx
/var/www/avatar/frontend/pages/callcenter/call.tsx
/var/www/avatar/frontend/pages/callcenter/agent-dashboard.tsx
/var/www/avatar/frontend/pages/callcenter/crm-dashboard.tsx
```

**Documentation**:
```
/var/www/avatar/CALL_CENTER_GETTING_STARTED.md
/var/www/avatar/CALL_CENTER_API_INTEGRATION.md
/var/www/avatar/CALL_CENTER_COMPLETE.md
/var/www/avatar/README_CALL_CENTER.md
/var/www/avatar/QUICK_COMMANDS.md
```

**Scripts**:
```
/var/www/avatar/start-call-center.sh
/var/www/avatar/start-call-center.bat
```

### Avatary Files (WITH SPACE path)

**Backend**:
```
/var/www/avatar /avatary/
/var/www/avatar /frontend/  (shared)
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    Browser / Client                │
└────────┬────────────────────────────────────────────┘
         │
    ┌────┴────────────────────────────────────────┐
    │         Frontend (Shared Next.js)           │
    │         /var/www/avatar/frontend/           │
    │                                             │
    │  ┌──────────────┬──────────────────────┐   │
    │  │ Avatary      │ Call Center          │   │
    │  │ Routes       │ Routes               │   │
    │  │ /avatar/*    │ /callcenter/*        │   │
    │  │ (existing)   │ (NEW)                │   │
    │  └──────────────┴──────────────────────┘   │
    │            Port 3000                        │
    └────┬─────────────────────┬──────────────────┘
         │                     │
    ┌────▼──────────┐    ┌─────▼──────────────┐
    │ Avatary API   │    │ CallCenter API     │
    │               │    │ (FastAPI)          │
    │ /var/www/     │    │ /var/www/avatar/   │
    │ avatar /      │    │ callCenter/        │
    │ avatary/      │    │ api.py             │
    │ [backend]     │    │                    │
    │               │    │ Port 8000          │
    │ Ports: [?]    │    │                    │
    └────┬──────────┘    └─────┬──────────────┘
         │                     │
    ┌────▼─────────────────────▼────────┐
    │      Database Layer (Future)       │
    │                                    │
    │  Avatary DB  │  CallCenter DB      │
    │  (separate)  │  (PostgreSQL ready) │
    └────────────────────────────────────┘
```

---

## Environment Setup

### For CallCenter

Create `/var/www/avatar/frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Create `/var/www/avatar/callCenter/.env`:
```env
DEBUG=true
DATABASE_URL=postgresql://user:pass@localhost/call_center
```

### For Avatary

Check `/var/www/avatar /.env` or avatary's configuration

---

## Running Both Systems Simultaneously

### Option 1: Different Terminals (Recommended)

**Terminal 1 - Avatary**:
```bash
cd "/var/www/avatar /"
# Run avatary backend
```

**Terminal 2 - CallCenter API**:
```bash
cd /var/www/avatar/callCenter
python main.py
```

**Terminal 3 - Shared Frontend**:
```bash
cd /var/www/avatar/frontend
npm run dev
```

### Option 2: Docker Compose

Use separate compose files or single compose with multiple services:
```bash
docker-compose up -d
# Both systems start with different ports
```

---

## Summary

| Aspect | Avatary | CallCenter |
|--------|---------|-----------|
| **Directory** | `/var/www/avatar /` (WITH space) | `/var/www/avatar/` (NO space) |
| **Backend** | Custom Python | FastAPI |
| **Backend Location** | `/var/www/avatar /avatary/` | `/var/www/avatar/callCenter/` |
| **Frontend** | Shared in `/var/www/avatar /frontend/` | Shared in `/var/www/avatar/frontend/` |
| **Frontend Routes** | `/avatar/*` | `/callcenter/*` |
| **API Port** | Custom (check config) | 8000 |
| **Frontend Port** | 3000 (shared) | 3000 (shared) |
| **Database** | Separate (existing) | PostgreSQL ready |
| **Conflict** | ✅ NONE | ✅ NONE |

---

## Key Takeaway

✅ **No conflicts** - The systems are completely separated:
- Different directories (one has a space in path)
- Different backend codebases
- Different API endpoints
- Different frontend routes
- Can run independently or together

Both systems can coexist peacefully in the same project!

---

**Document Version**: 1.0
**Date**: November 8, 2025
