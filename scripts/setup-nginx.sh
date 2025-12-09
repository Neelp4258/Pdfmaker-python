#!/bin/bash
# Setup Nginx reverse proxy with SSL
# Usage: ./setup-nginx.sh yourdomain.com

set -e

if [ -z "$1" ]; then
    echo "Usage: ./setup-nginx.sh yourdomain.com"
    exit 1
fi

DOMAIN=$1

echo "🌐 Setting up Nginx for $DOMAIN"
echo "==============================="

# Install Nginx and Certbot
echo "📦 Installing Nginx and Certbot..."
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx

# Create Nginx config
echo "⚙️  Creating Nginx configuration..."
cat > /etc/nginx/sites-available/html2pdf << EOF
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 100M;
    client_body_timeout 600s;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:5000/health;
        access_log off;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/html2pdf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
echo "🧪 Testing Nginx configuration..."
nginx -t

# Reload Nginx
systemctl reload nginx

# Get SSL certificate
echo "🔐 Obtaining SSL certificate..."
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --register-unsafely-without-email

# Setup auto-renewal
echo "⏰ Setting up SSL auto-renewal..."
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo "✅ Nginx Setup Complete!"
echo "======================="
echo ""
echo "🌐 Your service is now available at: https://$DOMAIN"
echo "🔐 SSL certificate installed and will auto-renew"
echo ""
echo "📋 Test your setup:"
echo "  curl https://$DOMAIN/health"
echo ""
