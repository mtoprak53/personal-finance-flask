#!/bin/bash
# Environment setup script

ENV_DIR="environments"

echo "🔧 Environment Setup Utility"
echo "=========================="

case "$1" in
    init)
        echo "Initializing environments..."
        mkdir -p $ENV_DIR
        
        # Template'i kopyala
        cp $ENV_DIR/.env.example $ENV_DIR/.env.development
        cp $ENV_DIR/.env.example $ENV_DIR/.env.testing
        
        echo "✅ Created .env.development and .env.testing"
        echo "📝 Edit $ENV_DIR/.env.development with your settings"
        ;;
        
    create-local)
        echo "Creating local override..."
        if [ ! -f "$ENV_DIR/.env.local" ]; then
            echo "# Local overrides" > $ENV_DIR/.env.local
            echo "DEV_DATABASE_URL=postgresql://user:pass@localhost/dbname" >> $ENV_DIR/.env.local
            echo "✅ Created $ENV_DIR/.env.local"
        else
            echo "⚠️  $ENV_DIR/.env.local already exists"
        fi
        ;;
        
    check)
        echo "Checking environments..."
        export FLASK_ENV=development
        python -c "
import sys
sys.path.insert(0, '.')
from config import load_environment
print('✅ Environment loaded successfully')
        "
        ;;
        
    list)
        echo "Available environment files:"
        ls -la $ENV_DIR/.* | grep -v "^d"
        ;;
        
    *)
        echo "Usage: $0 {init|create-local|check|list}"
        echo ""
        echo "Commands:"
        echo "  init         Initialize environment files"
        echo "  create-local Create local override file"
        echo "  check        Check environment loading"
        echo "  list         List environment files"
        exit 1
        ;;
esac