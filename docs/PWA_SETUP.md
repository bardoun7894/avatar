# PWA Setup Guide

## Overview
The Ornina AI Avatar app is now configured as a Progressive Web App (PWA), allowing users to install it on their devices for a native app-like experience.

## Features Implemented

### 1. **Service Worker**
- Automatic caching of static assets
- Offline support with fallback page
- Background sync capabilities
- Smart caching strategies for different asset types

### 2. **Web App Manifest**
- App name, icons, and theme colors
- Standalone display mode
- Support for multiple icon sizes (72px to 512px)

### 3. **Install Prompt**
- Custom install prompt component
- Bilingual support (Arabic/English)
- Dismissible with "later" option

### 4. **Update Notifications**
- Automatic detection of new versions
- User prompt to reload and update

### 5. **Platform Support**
- iOS Safari (Add to Home Screen)
- Android Chrome (Install App)
- Desktop browsers (Chrome, Edge, etc.)

## Files Created/Modified

### New Files:
- `/public/manifest.json` - PWA manifest configuration
- `/public/browserconfig.xml` - Windows tile configuration
- `/public/icons/` - App icons (72px to 512px)
- `/frontend/pages/offline.tsx` - Offline fallback page
- `/frontend/components/PWAInstallPrompt.tsx` - Install prompt component
- `/scripts/generate-pwa-icons.sh` - Icon generation script

### Modified Files:
- `/frontend/next.config.js` - Added PWA configuration with next-pwa
- `/frontend/pages/_document.tsx` - Added PWA meta tags
- `/frontend/pages/_app.tsx` - Added install prompt and update handler
- `/frontend/.gitignore` - Added service worker files

## Installation Instructions

### For Users:

#### On Mobile (Android):
1. Open the app in Chrome
2. Tap the menu (three dots)
3. Select "Install app" or "Add to Home Screen"
4. Follow the prompts

#### On Mobile (iOS):
1. Open the app in Safari
2. Tap the Share button
3. Select "Add to Home Screen"
4. Tap "Add"

#### On Desktop:
1. Open the app in Chrome/Edge
2. Look for the install icon in the address bar
3. Click "Install"
4. Or use the custom prompt that appears

### For Developers:

#### Build the App:
```bash
cd /var/www/avatar/frontend
npm run build
npm start
```

#### Development Mode:
```bash
npm run dev
```
Note: PWA features are disabled in development mode for easier debugging.

#### Test PWA Features:
1. Build and run in production mode
2. Open Chrome DevTools
3. Go to Application tab
4. Check:
   - Manifest
   - Service Workers
   - Cache Storage
   - Lighthouse PWA audit

## Caching Strategy

### CacheFirst (Long-term caching):
- Google Fonts webfonts (1 year)
- Audio files (24 hours)

### StaleWhileRevalidate (Balance between fresh and fast):
- Google Fonts stylesheets (1 week)
- Font files (1 week)
- Images (24 hours)
- Next.js images (24 hours)
- JavaScript files (24 hours)
- CSS files (24 hours)
- Next.js data (24 hours)

### NetworkFirst (Prioritize fresh data):
- API routes (excluded from caching)
- JSON/XML/CSV data (24 hours)
- Other same-origin requests (24 hours, 10s timeout)

## Customization

### Update App Icons:
Replace the generated icons in `/public/icons/` with your custom designs. Recommended tool: [PWA Asset Generator](https://github.com/elegantapp/pwa-asset-generator)

```bash
npx pwa-asset-generator [source-image] /var/www/avatar/public/icons --manifest /var/www/avatar/public/manifest.json
```

### Update App Name/Colors:
Edit `/public/manifest.json`:
```json
{
  "name": "Your App Name",
  "short_name": "Short Name",
  "theme_color": "#your-color",
  "background_color": "#your-color"
}
```

### Modify Caching Strategy:
Edit `/frontend/next.config.js` in the `withPWA` configuration.

## Testing Checklist

- [ ] App installs on Android Chrome
- [ ] App installs on iOS Safari
- [ ] App installs on Desktop Chrome/Edge
- [ ] Offline page displays when network is unavailable
- [ ] Service worker caches assets correctly
- [ ] Install prompt appears and works
- [ ] Update notification works when new version deployed
- [ ] Icons display correctly on all platforms
- [ ] App launches in standalone mode (no browser UI)
- [ ] Lighthouse PWA score > 90

## Troubleshooting

### Service Worker Not Registering:
- Ensure you're using HTTPS (required for PWA)
- Check browser console for errors
- Clear browser cache and reload

### Install Prompt Not Showing:
- PWA criteria must be met (manifest, service worker, HTTPS)
- User must visit the site at least twice with 5 minutes between visits
- User hasn't previously dismissed the prompt

### Icons Not Displaying:
- Verify icon files exist in `/public/icons/`
- Check file sizes match manifest.json
- Clear cache and rebuild

### Offline Page Not Working:
- Check service worker is active
- Verify offline.tsx is built correctly
- Test by disabling network in DevTools

## Production Deployment

1. Build the app:
```bash
npm run build
```

2. Service worker files will be generated in `/public/`:
   - `sw.js` - Main service worker
   - `workbox-*.js` - Workbox runtime files

3. Deploy to production server with HTTPS enabled

4. Test PWA features in production environment

## Resources

- [Next PWA Documentation](https://github.com/shadowwalker/next-pwa)
- [PWA Builder](https://www.pwabuilder.com/)
- [Web.dev PWA Guide](https://web.dev/progressive-web-apps/)
- [MDN PWA Documentation](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)

## Notes

- PWA features are disabled in development mode (`NODE_ENV=development`)
- Service worker files are auto-generated during build and should not be committed to git
- Icons were generated with placeholder content - replace with actual app icons
- The app supports RTL (Arabic) layout as configured
