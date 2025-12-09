#!/bin/bash
# Backup HTML2PDF configuration and data
# Usage: ./backup.sh

set -e

BACKUP_DIR="/opt/backups/html2pdf"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

echo "💾 Backing up HTML2PDF Service"
echo "=============================="

# Create backup directory
mkdir -p $BACKUP_DIR

cd /opt/Pdfmaker-python

# Create backup
echo "📦 Creating backup..."
tar -czf $BACKUP_FILE \
    .env \
    docker-compose.yml \
    --exclude='*.pdf' \
    --exclude='node_modules' \
    --exclude='.git'

# Backup PDFs separately (if using local storage)
if [ -d "/tmp/html2pdf" ]; then
    echo "📄 Backing up PDFs..."
    tar -czf "$BACKUP_DIR/pdfs_$TIMESTAMP.tar.gz" /tmp/html2pdf
fi

# Keep only last 7 backups
echo "🗑️  Cleaning old backups..."
cd $BACKUP_DIR
ls -t backup_*.tar.gz | tail -n +8 | xargs -r rm --
ls -t pdfs_*.tar.gz | tail -n +8 | xargs -r rm --

echo ""
echo "✅ Backup Complete!"
echo "=================="
echo ""
echo "📁 Backup saved to: $BACKUP_FILE"
echo "💾 Backup size: $(du -h $BACKUP_FILE | cut -f1)"
echo ""
echo "📋 To restore:"
echo "  tar -xzf $BACKUP_FILE -C /opt/Pdfmaker-python"
echo ""
