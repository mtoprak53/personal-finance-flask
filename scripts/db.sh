#!/bin/bash
# Database yönetim script'i

set -e  # Hata durumunda dur

ENV_FILE="environments/.env.development"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Environment kontrolü
check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        print_error "$ENV_FILE bulunamadı!"
        echo "Kopyalayın: cp environments/.env.example $ENV_FILE"
        echo "Düzenleyin: nano $ENV_FILE"
        exit 1
    fi
    
    source $ENV_FILE
    print_success "Environment yüklendi"
}

case "$1" in
    init)
        check_env
        print_info "Database tabloları oluşturuluyor..."
        FLASK_ENV=development python scripts/init_db.py init
        ;;
        
    reset)
        check_env
        print_info "Database sıfırlanıyor (DİKKAT!)..."
        FLASK_ENV=development python scripts/init_db.py reset
        ;;
        
    check)
        check_env
        print_info "Database kontrol ediliyor..."
        FLASK_ENV=development python scripts/init_db.py check
        ;;
        
    sample)
        check_env
        print_info "Örnek veriler ekleniyor..."
        ADD_SAMPLE_DATA=true FLASK_ENV=development python scripts/init_db.py init
        ;;
        
    railway-init)
        print_info "Railway'de database oluşturuluyor..."
        railway run python scripts/init_db.py init
        ;;
        
    railway-check)
        print_info "Railway database kontrolü..."
        railway run python scripts/init_db.py check
        ;;
        
    backup)
        check_env
        print_info "Database backup alınıyor..."
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
        pg_dump "$DATABASE_URL" > "backups/$BACKUP_FILE"
        print_success "Backup oluşturuldu: backups/$BACKUP_FILE"
        ;;
        
    *)
        echo "Kullanım: $0 {init|reset|check|sample|railway-init|railway-check|backup}"
        echo ""
        echo "Komutlar:"
        echo "  init           Local database tablolarını oluştur"
        echo "  reset          Local database'i sıfırla (DİKKAT!)"
        echo "  check          Database bağlantısını kontrol et"
        echo "  sample         Örnek veriler ekle"
        echo "  railway-init   Railway'de database oluştur"
        echo "  railway-check  Railway database'ini kontrol et"
        echo "  backup         Local database backup al"
        exit 1
        ;;
esac