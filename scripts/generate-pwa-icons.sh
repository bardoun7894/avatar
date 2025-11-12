#!/bin/bash

# Create icons directory
mkdir -p /var/www/avatar/public/icons

# Generate placeholder icons using ImageMagick (if available)
# If ImageMagick is not installed, you'll need to provide your own icons

SIZES=(72 96 128 144 152 192 384 512)
ICON_DIR="/var/www/avatar/public/icons"

# Check if ImageMagick is installed
if command -v convert &> /dev/null; then
    echo "Generating PWA icons..."
    for size in "${SIZES[@]}"; do
        convert -size ${size}x${size} xc:black \
                -gravity center \
                -pointsize $((size/3)) \
                -fill white \
                -annotate +0+0 "O" \
                "${ICON_DIR}/icon-${size}x${size}.png"
        echo "Created icon-${size}x${size}.png"
    done
    echo "Icons generated successfully!"
else
    echo "ImageMagick not found. Creating placeholder files..."
    echo "Please replace these with your actual app icons."
    for size in "${SIZES[@]}"; do
        touch "${ICON_DIR}/icon-${size}x${size}.png"
        echo "Created placeholder for icon-${size}x${size}.png"
    done
fi

# Create favicon
if command -v convert &> /dev/null; then
    convert -size 32x32 xc:black \
            -gravity center \
            -pointsize 16 \
            -fill white \
            -annotate +0+0 "O" \
            /var/www/avatar/public/favicon.ico
    echo "Created favicon.ico"
else
    touch /var/www/avatar/public/favicon.ico
    echo "Created placeholder favicon.ico"
fi

echo ""
echo "Note: Replace the generated icons with your actual app icons for production use."
