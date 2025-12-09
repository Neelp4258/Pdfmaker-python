#!/bin/bash
# Update HTML2PDF service
# Usage: ./update.sh

set -e

echo "🔄 Updating HTML2PDF Service"
echo "============================"

cd /opt/Pdfmaker-python

# Pull latest code
echo "📥 Pulling latest code..."
git pull

# Rebuild and restart
echo "🔨 Rebuilding containers..."
docker-compose build

echo "🔄 Restarting services..."
docker-compose down
docker-compose up -d

# Wait for health check
echo "⏳ Waiting for service to be ready..."
sleep 10

# Check health
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Update successful! Service is healthy."
else
    echo "⚠️  Service may not be ready yet. Check logs:"
    echo "  docker-compose logs -f"
fi
