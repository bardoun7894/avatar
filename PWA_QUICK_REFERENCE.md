# PWA Quick Reference Card

## 🚀 Quick Start

### Build & Run
```bash
# Using PWA Manager (Recommended)
./scripts/pwa-manager.sh build    # Build with PWA
./scripts/pwa-manager.sh start    # Start production
./scripts/pwa-manager.sh dev      # Development mode

# Or manually
cd frontend
npm run build && npm start
```

## 📋 Common Commands

### PWA Manager
```bash
./scripts/pwa-manager.sh status   # Check PWA status
./scripts/pwa-manager.sh verify   # Verify installation
./scripts/pwa-manager.sh clean    # Clean service worker
./scripts/pwa-manager.sh icons    # Regenerate icons
./scripts/pwa-manager.sh help     # Show all commands
```

### Manual Commands
```bash
# Build
cd /var/www/avatar/frontend && npm run build

# Start production
npm start

# Development (PWA disabled)
npm run dev

# Verify PWA
/var/www/avatar/scripts/verify-pwa.sh
```

## 📱 Installation Instructions

### Android
1. Chrome → Menu (⋮) → "Install app"
2. Or use custom prompt in app

### iOS
1. Safari → Share (□↑) → "Add to Home Screen"
2. Tap "Add"

### Desktop
1. Chrome/Edge → Install icon in address bar
2. Or use custom prompt

## 🔧 Key Files

### Configuration
- `/public/manifest.json` - App manifest
- `/frontend/next.config.js` - PWA config
- `/frontend/pages/_document.tsx` - Meta tags

### Components
- `/frontend/components/PWAInstallPrompt.tsx` - Install prompt
- `/frontend/pages/offline.tsx` - Offline page

### Auto-Generated (Don't Edit)
- `/frontend/public/sw.js` - Service worker
- `/frontend/public/workbox-*.js` - Workbox runtime

## 🎨 Customization

### Update App Name/Colors
Edit `/public/manifest.json`:
```json
{
  "name": "Your App Name",
  "short_name": "Short",
  "theme_color": "#000000",
  "background_color": "#000000"
}
```

### Replace Icons
```bash
# Option 1: Use PWA Asset Generator
npx pwa-asset-generator logo.png public/icons \
  --manifest public/manifest.json

# Option 2: Manual replacement
# Replace files in /public/icons/
# Sizes: 72, 96, 128, 144, 152, 192, 384, 512
```

### Modify Caching
Edit `/frontend/next.config.js` → `withPWA` → `runtimeCaching`

## 🐛 Troubleshooting

### Install Prompt Not Showing
- ✅ Check HTTPS enabled
- ✅ Visit site twice (5 min gap)
- ✅ Check DevTools → Application → Manifest

### Service Worker Not Working
```bash
# Clean and rebuild
./scripts/pwa-manager.sh clean
./scripts/pwa-manager.sh build
```

### Offline Page Not Working
- Check service worker active in DevTools
- Test: DevTools → Network → Offline

### Build Errors
```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

## 📊 Testing

### Chrome DevTools
1. F12 → Application tab
2. Check:
   - Manifest ✓
   - Service Workers ✓
   - Cache Storage ✓

### Lighthouse Audit
1. F12 → Lighthouse tab
2. Select "Progressive Web App"
3. Click "Generate report"
4. Target score: >90

### Manual Testing
- [ ] Install on Android
- [ ] Install on iOS
- [ ] Install on Desktop
- [ ] Test offline mode
- [ ] Test update notification
- [ ] Verify icons display

## 📦 Production Deployment

```bash
# 1. Build
cd /var/www/avatar/frontend
npm run build

# 2. Verify
/var/www/avatar/scripts/verify-pwa.sh

# 3. Deploy
# Ensure HTTPS is enabled
# Copy build files to production server

# 4. Test
# Visit site and test installation
```

## ⚙️ Environment Variables

PWA is disabled in development:
```bash
NODE_ENV=development  # PWA disabled
NODE_ENV=production   # PWA enabled
```

## 📚 Documentation

- Full Guide: `/docs/PWA_SETUP.md`
- Installation Summary: `/PWA_INSTALLATION_COMPLETE.md`
- This Reference: `/PWA_QUICK_REFERENCE.md`

## 🔗 Useful Links

- [Next PWA](https://github.com/shadowwalker/next-pwa)
- [PWA Builder](https://www.pwabuilder.com/)
- [Web.dev PWA](https://web.dev/progressive-web-apps/)
- [Workbox](https://developers.google.com/web/tools/workbox)

## ✅ Checklist

Before deploying:
- [ ] Replace placeholder icons with actual designs
- [ ] Update manifest.json with app details
- [ ] Test on multiple devices/browsers
- [ ] Verify HTTPS is enabled
- [ ] Run Lighthouse PWA audit
- [ ] Test offline functionality
- [ ] Test update mechanism

---

**Quick Help:** `./scripts/pwa-manager.sh help`

**Status Check:** `./scripts/pwa-manager.sh status`
