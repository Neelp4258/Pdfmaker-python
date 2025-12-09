#!/bin/bash
# Quick fix script for Playwright installation issues
# Run this if you get error code 100

set -e

echo "🔧 Playwright Installation Fix Script"
echo "======================================"

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
    ARCH=$(uname -m)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    ARCH=$(uname -m)
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

echo "📊 Detected: $OS ($ARCH)"

# Function to install system dependencies on different platforms
install_deps() {
    if [[ "$OS" == "linux" ]]; then
        echo "📦 Installing system dependencies..."

        if command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            sudo apt-get update
            sudo apt-get install -y \
                libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
                libcups2 libdrm2 libdbus-1-3 libxkbcommon0 \
                libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
                libgbm1 libpango-1.0-0 libcairo2 libasound2 \
                libatspi2.0-0 libxshmfence1 fonts-liberation
        elif command -v yum &> /dev/null; then
            # RHEL/CentOS/Fedora
            sudo yum install -y \
                nss nspr atk at-spi2-atk cups-libs \
                libdrm libXcomposite libXdamage libXrandr \
                mesa-libgbm pango cairo alsa-lib liberation-fonts
        fi
    elif [[ "$OS" == "mac" ]]; then
        echo "📦 macOS detected - dependencies should be handled automatically"
    fi
}

# Install system dependencies
install_deps

# Install Playwright with system dependencies
echo "🎭 Installing Playwright and Chromium..."

# Method 1: Standard installation
echo "Attempting standard installation..."
if playwright install chromium --with-deps; then
    echo "✅ Installation successful!"
    exit 0
fi

# Method 2: Install deps first, then browser
echo "Attempting alternative method..."
playwright install-deps chromium
if playwright install chromium; then
    echo "✅ Installation successful!"
    exit 0
fi

# Method 3: Use Python to install
echo "Attempting Python method..."
if python3 -m playwright install chromium; then
    echo "✅ Installation successful!"
    exit 0
fi

# Method 4: For ARM/M1 Macs - use system Chromium
if [[ "$OS" == "mac" && "$ARCH" == "arm64" ]]; then
    echo "🍎 Detected Apple Silicon - installing via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Install from: https://brew.sh"
        exit 1
    fi

    brew install chromium
    echo "✅ Chromium installed via Homebrew"
    echo "⚙️  Set this environment variable:"
    echo "export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/opt/homebrew/bin/chromium"
    exit 0
fi

echo "❌ All installation methods failed"
echo ""
echo "🆘 Troubleshooting Steps:"
echo "1. Check internet connection"
echo "2. Try running with sudo: sudo ./scripts/fix-playwright.sh"
echo "3. Install dependencies manually:"
echo "   - Ubuntu/Debian: sudo apt-get install -y libnss3 libxss1 libasound2"
echo "   - macOS: brew install chromium"
echo "4. For Docker: Use the updated Dockerfile"
echo "5. For ARM/M1 Mac: Use Dockerfile.arm"
echo ""
echo "📚 See docs/TROUBLESHOOTING.md for more help"

exit 1
