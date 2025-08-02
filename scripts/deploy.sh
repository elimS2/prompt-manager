#!/bin/bash
# Deployment script for Prompt Manager

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Configuration
APP_DIR="/var/www/prompt-manager"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="/var/log/prompt-manager"
USER="www-data"
GROUP="www-data"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root"
   exit 1
fi

# Create directories if they don't exist
echo "📁 Creating directories..."
mkdir -p $APP_DIR
mkdir -p $LOG_DIR
chown $USER:$GROUP $LOG_DIR

# Navigate to app directory
cd $APP_DIR

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main || print_error "Failed to pull latest code"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv $VENV_DIR
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source $VENV_DIR/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements-prod.txt

# Run database migrations
echo "🗄️ Running database migrations..."
flask db upgrade || print_error "Failed to run migrations"

# Collect static files (if using Flask-Assets or similar)
# echo "📂 Collecting static files..."
# flask collect-static

# Set permissions
echo "🔒 Setting permissions..."
chown -R $USER:$GROUP $APP_DIR
chmod -R 755 $APP_DIR

# Restart services
echo "🔄 Restarting services..."

# Restart Gunicorn
if systemctl is-active --quiet prompt-manager; then
    systemctl restart prompt-manager
    print_success "Gunicorn restarted"
else
    print_error "Prompt Manager service not found. Please ensure systemd service is configured."
fi

# Restart Nginx
if systemctl is-active --quiet nginx; then
    systemctl reload nginx
    print_success "Nginx reloaded"
fi

# Clear application cache (if implemented)
# flask clear-cache

echo "✅ Deployment complete!"

# Show service status
echo ""
echo "📊 Service Status:"
systemctl status prompt-manager --no-pager || true