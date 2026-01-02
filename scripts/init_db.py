#!/usr/bin/env python3
"""
Database Initialization Script
Railway ve local development için database tablolarını oluşturur.
"""

import os
import sys
from pathlib import Path

# Proje kök dizinini ekle
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask
from config import get_config
from models import db, Account, Transaction
from datetime import datetime
import pytz


def create_app_for_db():
    """Database işlemleri için Flask app oluştur"""
    app = Flask(__name__)
    
    # Environment'ı kontrol et
    env = os.getenv('FLASK_ENV', 'development')
    print(f"🔧 Environment: {env}")
    
    # Config'i yükle
    config_class = get_config()
    app.config.from_object(config_class)
    
    # DATABASE_URL kontrolü
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        print("❌ DATABASE_URL bulunamadı!")
        print("Lütfen environment değişkenlerini kontrol edin.")
        print("Local için: environments/.env.development dosyasını düzenleyin")
        print("Railway için: Railway dashboard -> Variables")
        sys.exit(1)
    
    # Database'i başlat
    db.init_app(app)
    
    return app


def init_database():
    """Database tablolarını oluştur"""
    app = create_app_for_db()
    
    with app.app_context():
        try:
            print("🗄️  Database bağlantısı kuruluyor...")
            print(f"📊 Database URL: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
            
            # Tüm tabloları oluştur
            db.create_all()
            print("✅ Tablolar başarıyla oluşturuldu!")
            
            # Örnek veri ekleme (isteğe bağlı)
            if os.getenv('ADD_SAMPLE_DATA', 'false').lower() == 'true':
                add_sample_data()
                print("📝 Örnek veriler eklendi!")
            
            # Tablo bilgilerini göster
            show_table_info()
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            sys.exit(1)


def add_sample_data():
    """Örnek veriler ekle (development için)"""
    from models import Account, Transaction
    from decimal import Decimal
    
    # Hesap ekle (eğer yoksa)
    if Account.query.count() == 0:
        accounts = [
            Account(name='Ana Hesap', balance=Decimal('5000.00'), currency='USD'),
            Account(name='Tasarruf Hesabı', balance=Decimal('15000.00'), currency='USD'),
            Account(name='Günlük Harcama', balance=Decimal('1000.00'), currency='TRY'),
        ]
        
        for acc in accounts:
            db.session.add(acc)
        
        db.session.commit()
        print(f"   ➕ {len(accounts)} hesap eklendi")
    
    # İşlem ekle (eğer yoksa)
    if Transaction.query.count() == 0:
        nyc_tz = pytz.timezone('America/New_York')
        
        transactions = [
            Transaction(
                title='Market Alışverişi',
                account_id=1,
                amount=Decimal('125.50'),
                type='expense',
                category='Market',
                date=nyc_tz.localize(datetime.now()),
                description='Haftalık market alışverişi'
            ),
            Transaction(
                title='Maaş',
                account_id=1,
                amount=Decimal('3500.00'),
                type='income',
                category='Maaş',
                date=nyc_tz.localize(datetime.now()),
                description='Aylık maaş ödemesi'
            ),
            Transaction(
                title='Elektrik Faturası',
                account_id=3,
                amount=Decimal('250.75'),
                type='expense',
                category='Fatura',
                date=nyc_tz.localize(datetime.now()),
                description='Aralık ayı elektrik faturası'
            ),
        ]
        
        for trans in transactions:
            db.session.add(trans)
        
        db.session.commit()
        print(f"   ➕ {len(transactions)} işlem eklendi")


def show_table_info():
    """Oluşturulan tablolar hakkında bilgi göster"""
    from sqlalchemy import inspect
    
    inspector = inspect(db.engine)
    
    print("\n📋 OLUŞTURULAN TABLOLAR:")
    print("-" * 50)
    
    for table_name in inspector.get_table_names():
        print(f"\n📊 Tablo: {table_name}")
        print("   Kolonlar:")
        
        for column in inspector.get_columns(table_name):
            col_info = f"     • {column['name']}: {column['type']}"
            if column.get('nullable') is False:
                col_info += " (NOT NULL)"
            if column.get('primary_key'):
                col_info += " (PRIMARY KEY)"
            print(col_info)


def reset_database():
    """Database'i sıfırla (DİKKAT: Tüm veriler silinir!)"""
    app = create_app_for_db()
    
    with app.app_context():
        confirm = input("⚠️  TÜM VERİLER SİLİNECEK! Devam etmek istiyor musunuz? (evet/hayır): ")
        
        if confirm.lower() != 'evet':
            print("❌ İşlem iptal edildi.")
            return
        
        try:
            print("🗑️  Tablolar siliniyor...")
            db.drop_all()
            print("✅ Tüm tablolar silindi!")
            
            print("🔄 Yeni tablolar oluşturuluyor...")
            db.create_all()
            print("✅ Tablolar yeniden oluşturuldu!")
            
        except Exception as e:
            print(f"❌ Hata: {e}")


def check_database():
    """Database bağlantısını ve tabloları kontrol et"""
    app = create_app_for_db()
    
    with app.app_context():
        try:
            # Bağlantı testi
            db.session.execute('SELECT 1')
            print("✅ Database bağlantısı başarılı!")
            
            # Tablo bilgileri
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"📊 Mevcut tablolar ({len(tables)} adet):")
            for table in tables:
                print(f"   • {table}")
            
            # Kayıt sayıları
            if 'accounts' in tables:
                acc_count = db.session.query(Account).count()
                print(f"   📁 Hesaplar: {acc_count} kayıt")
            
            if 'transactions' in tables:
                trans_count = db.session.query(Transaction).count()
                print(f"   📁 İşlemler: {trans_count} kayıt")
            
        except Exception as e:
            print(f"❌ Database bağlantı hatası: {e}")


def migrate_data():
    """Mevcut verileri yeni database'e taşı (opsiyonel)"""
    print("⚠️  Bu özellik henüz implemente edilmedi.")
    print("SQL dump/restore yöntemini kullanın.")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Yönetim Aracı')
    parser.add_argument('action', choices=['init', 'reset', 'check', 'migrate'], 
                       help='Yapılacak işlem')
    parser.add_argument('--sample-data', action='store_true',
                       help='Örnek veri ekle (init ile birlikte kullanın)')
    
    args = parser.parse_args()
    
    if args.sample_data:
        os.environ['ADD_SAMPLE_DATA'] = 'true'
    
    if args.action == 'init':
        init_database()
    elif args.action == 'reset':
        reset_database()
    elif args.action == 'check':
        check_database()
    elif args.action == 'migrate':
        migrate_data()