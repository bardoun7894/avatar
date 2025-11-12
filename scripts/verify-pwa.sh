#!/bin/bash

echo "==================================="
echo "PWA Installation Verification"
echo "==================================="
echo ""

# Check if required files exist
echo "Checking required files..."
echo ""

files=(
    "/var/www/avatar/public/manifest.json"
    "/var/www/avatar/public/browserconfig.xml"
    "/var/www/avatar/frontend/public/sw.js"
    "/var/www/avatar/public/icons/icon-192x192.png"
    "/var/www/avatar/public/icons/icon-512x512.png"
    "/var/www/avatar/frontend/pages/offline.tsx"
    "/var/www/avatar/frontend/components/PWAInstallPrompt.tsx"
)

all_exist=true
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file (MISSING)"
        all_exist=false
    fi
done

echo ""
echo "Checking icon files..."
echo ""

icon_sizes=(72 96 128 144 152 192 384 512)
for size in "${icon_sizes[@]}"; do
    icon_file="/var/www/avatar/public/icons/icon-${size}x${size}.png"
    if [ -f "$icon_file" ]; then
        echo "✓ icon-${size}x${size}.png"
    else
        echo "✗ icon-${size}x${size}.png (MISSING)"
        all_exist=false
    fi
done

echo ""
echo "Checking package.json..."
if grep -q "next-pwa" /var/www/avatar/frontend/package.json; then
    echo "✓ next-pwa package installed"
else
    echo "✗ next-pwa package NOT found"
    all_exist=false
fi

echo ""
echo "==================================="
if [ "$all_exist" = true ]; then
    echo "✓ PWA Setup Complete!"
    echo ""
    echo "Next steps:"
    echo "1. Build the app: cd /var/www/avatar/frontend && npm run build"
    echo "2. Start production server: npm start"
    echo "3. Access via HTTPS (required for PWA)"
    echo "4. Test installation on mobile/desktop"
else
    echo "✗ Some files are missing. Please check the setup."
fi
echo "==================================="
