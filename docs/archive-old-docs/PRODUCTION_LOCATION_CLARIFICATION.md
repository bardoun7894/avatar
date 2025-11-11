# Production Location Clarification

## ⚠️ IMPORTANT - CORRECT WORKING DIRECTORY

After investigation, here's the actual setup:

### Production App Location (CORRECT)
**`/var/www/avatar /`** (WITH trailing space)

```
/var/www/avatar /
├── avatary/              ← BACKEND (Ornina Avatar System)
├── frontend/             ← FRONTEND (Running on port 3000)
├── .git/                 ← Git repository
└── [other files]
```

### Status of This Deployment
- ✅ **Frontend**: Running from `/var/www/avatar /frontend`
- ✅ **Backend**: Running from `/var/www/avatar /avatary`
- ✅ **Repository**: https://github.com/bardoun7894/avatar.git
- ✅ **Latest Commit**: 57949ad (on main branch)
- ✅ **All changes**: Committed and pushed

---

## The Other Folder (DO NOT USE)

**`/var/www/avatar/`** (WITHOUT space)

This is a **different, unused clone**:
- ❌ Has its own separate git repository
- ❌ Changes here are NOT part of the production system
- ❌ Should not be used or modified
- ❌ Not synced with production

---

## What I Created (Mistake Location)

I mistakenly created the Call Center system in `/var/www/avatar/` (without space):

```
/var/www/avatar/callCenter/     ← Created here by mistake
/var/www/avatar/frontend/       ← Created here by mistake
```

**These are NOT being used.**

---

## Correct Approach Going Forward

### 1. For Ornina Avatar (Video Call System)
```bash
cd "/var/www/avatar /"  # WITH trailing space - Production
# This is where avatary backend and frontend run
```

### 2. For Call Center System (If Needed)
Should be created in:
```bash
cd "/var/www/avatar /"  # WITH space - Same production directory
mkdir callCenter        # Add to this directory
# Not in the separate /var/www/avatar/ folder
```

---

## Git Information

### Production Repository
- **Path**: `/var/www/avatar /`
- **Remote**: https://github.com/bardoun7894/avatar.git
- **Branch**: main
- **Latest Commit**: 57949ad
- **Status**: All changes committed and pushed

### Unused Clone
- **Path**: `/var/www/avatar/` (without space)
- **Should be**: Deleted or ignored
- **Do not use for**: Any production work

---

## Directory Confusion - Summary

```
Two directories exist:

1. /var/www/avatar/       (UNUSED)
   └─ Separate clone
   └─ Created by mistake
   └─ Should not be modified

2. /var/www/avatar /      (PRODUCTION - USE THIS!)
   ├─ avatary/            ← Backend (Ornina Avatar)
   ├─ frontend/           ← Frontend
   └─ .git/               ← Repository
```

---

## What to Do Now

### ✅ All Work Should Be In
```bash
cd "/var/www/avatar /"    # WITH trailing space
# This is your production directory
```

### ❌ Do Not Work In
```bash
cd /var/www/avatar/       # WITHOUT space
# This is a separate, unused clone
```

---

## Call Center System Status

The Call Center system I created is in the **wrong location** (`/var/www/avatar/` without space).

### Options:
1. **Move it to production**: Copy from `/var/www/avatar/callCenter/` to `/var/www/avatar /callCenter/`
2. **Delete the unused folder**: Remove `/var/www/avatar/` entirely (since it's not production)
3. **Keep it separate**: If used for testing only, mark it clearly as non-production

---

## Important Notes

- ✅ Avatar video call system is running in correct location
- ✅ All commits are to the correct repository
- ✅ Production frontend and backend are active and working
- ⚠️ Call Center files are in wrong location (non-production clone)
- ⚠️ Do not confuse the two `/var/www/avatar` directories

---

## Cleanup Recommendation

Since `/var/www/avatar/` (without space) is not used for production:

```bash
# Option 1: List what's in non-production folder
ls -la /var/www/avatar/

# Option 2: Check if it's tracked by git
cd /var/www/avatar
git remote -v

# Option 3: If not needed, can be archived or deleted
# (Keep only /var/www/avatar / with space for production)
```

---

## Summary

| Item | Location | Status |
|------|----------|--------|
| **Production Avatar** | `/var/www/avatar /` | ✅ Active |
| **Git Repository** | `/var/www/avatar /` | ✅ Up to date |
| **Unused Clone** | `/var/www/avatar/` | ⚠️ Ignore |
| **Call Center Files** | `/var/www/avatar/` | ⚠️ Wrong location |

---

## Next Steps

1. **For Avatar Work**: Always use `/var/www/avatar /` (with space)
2. **For Call Center**: Either move to `/var/www/avatar /callCenter/` or implement differently
3. **For Cleanup**: Consider handling the `/var/www/avatar/` folder appropriately

---

**Last Updated**: November 8, 2025
**Status**: Clarification Document
**Action**: Update all workflows to use correct production directory
