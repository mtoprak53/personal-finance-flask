import pytz
from flask import Blueprint, flash, render_template, request, redirect, url_for
from models import db, Account, Transaction
from decimal import Decimal
from datetime import datetime
from sqlalchemy import func

main_bp = Blueprint('main', __name__)


# Timezone (config'ten alınacak ama şimdilik sabit)
NYC_TZ = pytz.timezone('America/New_York')


def get_nyc_time():
    """Get current time in NYC timezone"""
    return datetime.now(NYC_TZ)


@main_bp.route('/')
def dashboard():
    """Ana dashboard sayfası - MEVCUT KODUNUZ BURAYA"""
    # Hesapları getir
    accounts = Account.query.all()
    
    # Toplam bakiye hesapla
    total_balance = sum([acc.balance for acc in accounts]) if accounts else Decimal('0')
    
    # Aylık istatistikler
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_income = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.type == 'income',
        Transaction.date >= start_of_month
    ).scalar() or Decimal('0')
    
    monthly_expense = db.session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.type == 'expense',
        Transaction.date >= start_of_month
    ).scalar() or Decimal('0')
    
    monthly_net = monthly_income - monthly_expense
    net_positive = monthly_net >= 0
    
    # En çok harcanan kategori
    top_category = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.type == 'expense',
        Transaction.date >= start_of_month
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).first()
    
    top_category_name = top_category[0] if top_category else None
    
    # Son işlemler (20 tane)
    recent_transactions = Transaction.query.order_by(Transaction.date.desc()).limit(20).all()
    
    # Template'e NYC zamanını da geçir
    nyc_now_str = get_nyc_time().strftime('%Y-%m-%dT%H:%M')
    
    return render_template('dashboard.html',
                         accounts=accounts,
                         transactions=recent_transactions,
                         total_balance=total_balance,
                         monthly_income=monthly_income,
                         monthly_expense=monthly_expense,
                         monthly_net=monthly_net,
                         net_positive=net_positive,
                         top_category=top_category_name,
                         now=nyc_now_str)


@main_bp.route('/add_account', methods=['POST'])
def add_account():
    """Hesap ekleme - MEVCUT KODUNUZ BURAYA"""
    try:
        name = request.form.get('name')
        balance = Decimal(request.form.get('balance', 0))
        currency = request.form.get('currency', 'USD')
        
        if not name:
            flash('Hesap adı gerekli!', 'danger')
            return redirect(url_for('main.dashboard'))
            
        new_acc = Account(name=name, balance=balance, currency=currency)
        db.session.add(new_acc)
        db.session.commit()
        
        flash(f'{name} hesabı başarıyla eklendi!', 'success')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
    
    return redirect(url_for('main.dashboard'))


@main_bp.route('/add_transaction', methods=['POST'])
def add_transaction():
    """İşlem ekleme - MEVCUT KODUNUZ BURAYA"""
    try:
        amount = Decimal(request.form.get('amount', 0))
        account_id = request.form.get('account_id')
        title = request.form.get('title', 'İşlem')
        category = request.form.get('category', 'Diğer')
        t_type = request.form.get('type', 'expense')
        date_str = request.form.get('date')
        description = request.form.get('description', '')
        
        if not amount or not account_id:
            flash('Tutar ve hesap seçimi zorunludur!', 'danger')
            return redirect(url_for('main.dashboard'))
        
        
        # Tarih formatını işle (NYC timezone'ında)
        if date_str:
            # Input'tan gelen datetime'ı NYC timezone'ına çevir
            naive_dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            transaction_date = NYC_TZ.localize(naive_dt)
        else:
            transaction_date = get_nyc_time()
        
        # Yeni işlem oluştur
        new_t = Transaction(
            title=title,
            account_id=int(account_id),
            amount=amount,
            type=t_type,
            category=category,
            date=transaction_date,
            description=description
        )
        
        # Hesap bakiyesini güncelle
        account = Account.query.get(account_id)
        if t_type == 'income':
            account.balance += amount
        else:
            account.balance -= amount
        
        db.session.add(new_t)
        db.session.commit()
        
        flash(f'İşlem başarıyla eklendi!', 'success')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
    
    return redirect(url_for('main.dashboard'))


@main_bp.route('/delete_transaction/<int:id>', methods=['POST'])
def delete_transaction(id):
    """İşlem silme - MEVCUT KODUNUZ BURAYA"""
    try:
        transaction = Transaction.query.get_or_404(id)
        account = Account.query.get(transaction.account_id)
        
        # Bakiyeyi düzelt
        if transaction.type == 'income':
            account.balance -= transaction.amount
        else:
            account.balance += transaction.amount
        
        db.session.delete(transaction)
        db.session.commit()
        
        flash('İşlem silindi!', 'warning')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
    
    return redirect(url_for('main.dashboard'))


@main_bp.route('/delete_account/<int:id>', methods=['POST'])
def delete_account(id):
    """Hesap silme - MEVCUT KODUNUZ BURAYA"""
    try:
        account = Account.query.get_or_404(id)
        
        # Hesaba ait işlemleri sil
        Transaction.query.filter_by(account_id=id).delete()
        
        # Hesabı sil
        db.session.delete(account)
        db.session.commit()
        
        flash(f'{account.name} hesabı silindi!', 'warning')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
    
    return redirect(url_for('main.dashboard'))
