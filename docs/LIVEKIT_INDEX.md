# LiveKit Connection - Documentation Index

## Quick Links

### 🚀 Get Started Fast
- **[LIVEKIT_QUICK_FIX.md](LIVEKIT_QUICK_FIX.md)** - 90-second solutions for common issues

### 🔍 Detailed Guides  
- **[LIVEKIT_TROUBLESHOOTING.md](LIVEKIT_TROUBLESHOOTING.md)** - Complete troubleshooting reference
- **[LIVEKIT_FIX_SUMMARY.md](LIVEKIT_FIX_SUMMARY.md)** - Technical details and implementation

### 🛠️ Tools & Scripts
- **Diagnostic Script**: `/var/www/avatar/scripts/diagnose-livekit.sh`
  ```bash
  /var/www/avatar/scripts/diagnose-livekit.sh
  ```
  Verifies all server-side configuration

---

## Problem: "Failed to connect to LiveKit: Failed to fetch"

### Solution Flowchart

```
Error occurs?
    ↓
Check browser console (F12 → Console)
    ↓
Look for error message with 🔌 or ❌ emoji
    ↓
Error message tells you what's wrong:
    ├─ Network error → Check internet/firewall
    ├─ 401 Unauthorized → Invalid credentials/token
    ├─ WebSocket error → Network/firewall blocking
    └─ Other error → See LIVEKIT_TROUBLESHOOTING.md
```

### Quick Fixes (in order)

1. **Hard refresh browser**
   ```
   Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)
   ```

2. **Restart frontend container**
   ```bash
   docker-compose down frontend
   docker-compose up -d frontend
   # Wait 30 seconds
   ```

3. **Check server configuration**
   ```bash
   /var/www/avatar/scripts/diagnose-livekit.sh
   ```

4. **Check browser console**
   - Open DevTools (F12)
   - Go to Console tab
   - Look for messages with 🔌 or ❌
   - Error message is now specific and actionable

5. **Review appropriate guide**
   - For quick fix: LIVEKIT_QUICK_FIX.md
   - For detailed help: LIVEKIT_TROUBLESHOOTING.md

---

## Common Issues & Solutions

| Issue | Solution | More Info |
|-------|----------|-----------|
| "Failed to fetch" | Check browser console for detailed error | Quick Fix §2 |
| Timeout | Check internet connection | Quick Fix §2A |
| 401 error | Wait 5min and retry, or rebuild frontend | Quick Fix §3B |
| Page won't load | Restart frontend container | Quick Fix §3B |
| Token endpoint fails | Check .env file | Troubleshooting §1 |
| DNS resolution fails | Check internet connection | Troubleshooting §5 |

---

## Browser Console Messages

### Success Sequence
```
🔌 Connecting to LiveKit...
📡 LiveKit URL: wss://tavus-agent-project-i82x78jc.livekit.cloud
🏠 Room: room_name
👤 User: user_name
🔑 Requesting token from /api/token...
📊 Token response status: 200
✅ Token received successfully
🔑 Connecting with token...
✅ Connected to LiveKit room: room_name
✅ Local video attached
🚀 Dispatching agent to room...
✅ Agent dispatch request sent
```

### Error Examples
```
❌ LiveKit connection error: Network error: Cannot reach LiveKit server...
Error type: TypeError
Error stack: [Full trace]
```

---

## For Different Users

### 👥 End Users
1. Check browser console (F12 → Console)
2. Look for error message starting with 🔌 or ❌
3. Follow [LIVEKIT_QUICK_FIX.md](LIVEKIT_QUICK_FIX.md)

### 👨‍💻 Developers
1. Run: `/var/www/avatar/scripts/diagnose-livekit.sh`
2. Check: `docker-compose logs frontend -f`
3. Read: [LIVEKIT_TROUBLESHOOTING.md](LIVEKIT_TROUBLESHOOTING.md)

### 🎯 Support/DevOps
1. Get user's exact error from browser console
2. Run diagnostic script
3. Check environment configuration
4. Review [LIVEKIT_FIX_SUMMARY.md](LIVEKIT_FIX_SUMMARY.md)

---

## Key Improvements Made

✅ **Better Error Messages**
- Before: "Failed to fetch" (no details)
- After: Specific error reason (network, auth, WebSocket, etc.)

✅ **Detailed Logging**
- Token generation steps with status codes
- Error type and stack trace
- Connection flow visualization

✅ **Diagnostic Tools**
- Script to verify server configuration
- Automated checks for common issues
- Clear pass/fail indicators

✅ **Comprehensive Documentation**
- Quick fix guide (90 seconds)
- Complete troubleshooting guide
- Technical implementation details

---

## When to Use Each Document

### LIVEKIT_QUICK_FIX.md
- **When**: Issue just occurred
- **Why**: Fastest path to solution (90 seconds)
- **Use if**: You want a quick checklist

### LIVEKIT_TROUBLESHOOTING.md
- **When**: Quick fix didn't work
- **Why**: Comprehensive guide with all scenarios
- **Use if**: You need detailed explanations

### LIVEKIT_FIX_SUMMARY.md
- **When**: Want to understand what was fixed
- **Why**: Technical details and context
- **Use if**: You're a developer reviewing changes

### diagnose-livekit.sh
- **When**: Need to verify server configuration
- **Why**: Automated checks for all components
- **Use if**: Troubleshooting isn't obvious

---

## File Locations

```
/var/www/avatar/
├── docs/
│   ├── LIVEKIT_INDEX.md ........................ This file
│   ├── LIVEKIT_QUICK_FIX.md ................... Quick solutions
│   ├── LIVEKIT_TROUBLESHOOTING.md ............ Detailed guide
│   └── LIVEKIT_FIX_SUMMARY.md ................ Technical details
├── scripts/
│   └── diagnose-livekit.sh ................... Diagnostic tool
└── frontend/
    ├── components/VideoCallInterface.tsx ... Main component
    └── apps/avatar/components/VideoCallInterface.tsx ... Avatar version
```

---

**Last Updated**: November 11, 2025  
**Status**: All checks passing ✅
