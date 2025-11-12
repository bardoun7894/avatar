#!/bin/bash

# PWA Manager Script for Ornina AI Avatar
# Provides easy commands for PWA management

FRONTEND_DIR="/var/www/avatar/frontend"
PUBLIC_DIR="/var/www/avatar/public"

show_help() {
    echo "PWA Manager - Ornina AI Avatar"
    echo ""
    echo "Usage: ./pwa-manager.sh [command]"
    echo ""
    echo "Commands:"
    echo "  build       - Build the app with PWA support"
    echo "  start       - Start production server"
    echo "  dev         - Start development server (PWA disabled)"
    echo "  verify      - Verify PWA installation"
    echo "  clean       - Clean service worker files"
    echo "  icons       - Regenerate placeholder icons"
    echo "  status      - Show PWA status"
    echo "  help        - Show this help message"
    echo ""
}

build_app() {
    echo "Building app with PWA support..."
    cd "$FRONTEND_DIR" || exit
    npm run build
    echo ""
    echo "Build complete! Service worker generated."
}

start_production() {
    echo "Starting production server..."
    cd "$FRONTEND_DIR" || exit
    npm start
}

start_dev() {
    echo "Starting development server (PWA disabled)..."
    cd "$FRONTEND_DIR" || exit
    npm run dev
}

verify_pwa() {
    /var/www/avatar/scripts/verify-pwa.sh
}

clean_sw() {
    echo "Cleaning service worker files..."
    rm -f "$FRONTEND_DIR/public/sw.js"
    rm -f "$FRONTEND_DIR/public/sw.js.map"
    rm -f "$FRONTEND_DIR/public/workbox-"*.js
    rm -f "$FRONTEND_DIR/public/workbox-"*.js.map
    rm -f "$FRONTEND_DIR/public/worker-"*.js
    rm -f "$FRONTEND_DIR/public/worker-"*.js.map
    echo "Service worker files cleaned."
    echo "Run 'build' command to regenerate."
}

regenerate_icons() {
    /var/www/avatar/scripts/generate-pwa-icons.sh
}

show_status() {
    echo "==================================="
    echo "PWA Status"
    echo "==================================="
    echo ""
    
    # Check if service worker exists
    if [ -f "$FRONTEND_DIR/public/sw.js" ]; then
        echo "✓ Service Worker: Generated"
        sw_size=$(du -h "$FRONTEND_DIR/public/sw.js" | cut -f1)
        echo "  Size: $sw_size"
    else
        echo "✗ Service Worker: Not found (run 'build' command)"
    fi
    
    # Check manifest
    if [ -f "$PUBLIC_DIR/manifest.json" ]; then
        echo "✓ Manifest: Present"
    else
        echo "✗ Manifest: Missing"
    fi
    
    # Check icons
    icon_count=$(find "$PUBLIC_DIR/icons" -name "icon-*.png" 2>/dev/null | wc -l)
    echo "✓ Icons: $icon_count files"
    
    # Check if next-pwa is installed
    if grep -q "next-pwa" "$FRONTEND_DIR/package.json"; then
        echo "✓ next-pwa: Installed"
    else
        echo "✗ next-pwa: Not installed"
    fi
    
    echo ""
    echo "==================================="
}

# Main script
case "$1" in
    build)
        build_app
        ;;
    start)
        start_production
        ;;
    dev)
        start_dev
        ;;
    verify)
        verify_pwa
        ;;
    clean)
        clean_sw
        ;;
    icons)
        regenerate_icons
        ;;
    status)
        show_status
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
