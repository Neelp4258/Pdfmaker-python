#!/bin/bash
# Quick install script for DigitalOcean Droplet
# Usage: curl -fsSL https://raw.githubusercontent.com/.../install-do.sh | bash

set -e

echo "🚀 HTML2PDF Installation Script for DigitalOcean"
echo "================================================"

# Update system
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Install docker-compose
echo "📦 Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install git
echo "📦 Installing Git..."
apt-get install -y git

# Clone repository
echo "📥 Cloning HTML2PDF repository..."
cd /opt
if [ -d "Pdfmaker-python" ]; then
    echo "⚠️  Directory exists, pulling latest..."
    cd Pdfmaker-python
    git pull
else
    git clone https://github.com/yourusername/Pdfmaker-python.git
    cd Pdfmaker-python
fi

# Create .env file
echo "⚙️  Creating environment configuration..."
cp .env.example .env

# Generate secure keys
API_KEY=$(openssl rand -hex 16)
SECRET_KEY=$(openssl rand -hex 32)

# Update .env
sed -i "s/API_KEYS=.*/API_KEYS=$API_KEY/" .env
sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
sed -i "s/API_KEY_REQUIRED=.*/API_KEY_REQUIRED=True/" .env

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check health
echo "🏥 Checking service health..."
curl -f http://localhost:5000/health || echo "⚠️  Service not responding yet, check logs with: docker-compose logs"

# Display info
echo ""
echo "✅ Installation Complete!"
echo "========================"
echo ""
echo "📝 Your API Key: $API_KEY"
echo "🔐 Your Secret Key: $SECRET_KEY"
echo ""
echo "⚠️  IMPORTANT: Save these keys somewhere safe!"
echo ""
echo "🌐 Service is running on: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "📋 Useful Commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Restart: docker-compose restart"
echo "  - Stop: docker-compose down"
echo "  - Update: cd /opt/Pdfmaker-python && git pull && docker-compose up -d --build"
echo ""
echo "🔧 Next Steps:"
echo "  1. Set up a domain name pointing to this server"
echo "  2. Install Nginx and SSL: ./scripts/setup-nginx.sh yourdomain.com"
echo "  3. Configure firewall: ufw allow 80 && ufw allow 443"
echo ""
