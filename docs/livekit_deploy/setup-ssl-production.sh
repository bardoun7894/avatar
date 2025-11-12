#!/bin/bash

# ============================================================================
# SSL/HTTPS Setup for Avatar Production
# Domain: pro.beldify.com
# Server: 184.174.37.148
# ============================================================================

set -e

SERVER="root@184.174.37.148"
DOMAIN="pro.beldify.com"
EMAIL="admin@beldify.com"

echo "🔒 SSL/HTTPS Setup for Avatar Production"
echo "=========================================="
echo ""
echo "Domain: $DOMAIN"
echo "Server: 184.174.37.148"
echo ""

# Step 1: Upload Nginx configuration
echo "📤 Step 1: Uploading Nginx configuration..."
scp docs/livekit_deploy/nginx-pro.beldify.com.conf $SERVER:/tmp/nginx-avatar.conf
echo "✅ Nginx config uploaded"
echo ""

# Step 2: Run SSL setup on server
echo "🔧 Step 2: Setting up SSL on server..."
echo ""

ssh $SERVER << 'ENDSSH'
set -e

DOMAIN="pro.beldify.com"
EMAIL="admin@beldify.com"

echo "Installing required packages..."
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx ufw

echo ""
echo "Configuring firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 3001/tcp
ufw allow 8000/tcp
ufw allow 8080/tcp
ufw --force enable
echo "✅ Firewall configured"

echo ""
echo "Stopping Nginx temporarily..."
systemctl stop nginx || true

echo ""
echo "Requesting SSL certificate from Let's Encrypt..."
certbot certonly --standalone \
    -d $DOMAIN \
    -d www.$DOMAIN \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    --preferred-challenges http

if [ $? -eq 0 ]; then
    echo "✅ SSL certificate obtained successfully"
else
    echo "❌ Failed to obtain SSL certificate"
    echo "Please check:"
    echo "  1. DNS is pointing to this server: dig $DOMAIN"
    echo "  2. Port 80 is accessible from internet"
    echo "  3. No firewall blocking Let's Encrypt"
    exit 1
fi

echo ""
echo "Configuring Nginx..."

# Create Nginx configuration
cat > /etc/nginx/sites-available/avatar << 'EOF'
# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name pro.beldify.com www.pro.beldify.com;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name pro.beldify.com www.pro.beldify.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/pro.beldify.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pro.beldify.com/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/pro.beldify.com/chain.pem;

    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/avatar-access.log;
    error_log /var/log/nginx/avatar-error.log;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # Frontend (Next.js)
    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Call Center API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running requests
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket for LiveKit
    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Long timeouts for WebSocket
        proxy_connect_timeout 7200s;
        proxy_send_timeout 7200s;
        proxy_read_timeout 7200s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/avatar /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo ""
echo "Testing Nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration has errors"
    exit 1
fi

# Start Nginx
echo ""
echo "Starting Nginx..."
systemctl enable nginx
systemctl start nginx
systemctl status nginx --no-pager

# Setup auto-renewal
echo ""
echo "Setting up SSL certificate auto-renewal..."
systemctl enable certbot.timer
systemctl start certbot.timer

# Test renewal
certbot renew --dry-run

echo ""
echo "✅ SSL/HTTPS setup complete!"
echo ""
echo "Your application is now available at:"
echo "  🔒 https://pro.beldify.com"
echo "  🔒 https://www.pro.beldify.com"
echo ""
echo "Services:"
echo "  Frontend: https://pro.beldify.com"
echo "  API: https://pro.beldify.com/api/"
echo "  Health: https://pro.beldify.com/health"
echo ""
ENDSSH

echo ""
echo "🎉 SSL Setup Complete!"
echo ""
echo "Your application is now secured with HTTPS:"
echo "  🔒 https://pro.beldify.com"
echo ""
echo "Next steps:"
echo "1. Test the HTTPS site: https://pro.beldify.com"
echo "2. Check SSL rating: https://www.ssllabs.com/ssltest/analyze.html?d=pro.beldify.com"
echo "3. Verify auto-renewal: ssh $SERVER 'certbot renew --dry-run'"
echo ""
