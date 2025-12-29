from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Account, Transaction
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy import func
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://finans_user:finans123@localhost/finans_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Flash mesajları için

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
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
    
    return render_template('dashboard.html',
                         accounts=accounts,
                         transactions=recent_transactions,
                         total_balance=total_balance,
                         monthly_income=monthly_income,
                         monthly_expense=monthly_expense,
                         monthly_net=monthly_net,
                         net_positive=net_positive,
                         top_category=top_category_name,
                         now=datetime.now().strftime('%Y-%m-%dT%H:%M'))

@app.route('/add_account', methods=['POST'])
def add_account():
    try:
        name = request.form.get('name')
        balance = Decimal(request.form.get('balance', 0))
        currency = request.form.get('currency', 'TRY')
        
        if not name:
            flash('Hesap adı gerekli!', 'danger')
            return redirect(url_for('dashboard'))
            
        new_acc = Account(name=name, balance=balance, currency=currency)
        db.session.add(new_acc)
        db.session.commit()
        
        flash(f'{name} hesabı başarıyla eklendi!', 'success')
    except Exception as e:
        flash(f'Hata: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
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
            return redirect(url_for('dashboard'))
        
        # Tarih formatını işle
        transaction_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M') if date_str else datetime.utcnow()
        
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
    
    return redirect(url_for('dashboard'))

@app.route('/delete_transaction/<int:id>', methods=['POST'])
def delete_transaction(id):
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
    
    return redirect(url_for('dashboard'))

@app.route('/delete_account/<int:id>', methods=['POST'])
def delete_account(id):
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
    
    return redirect(url_for('dashboard'))

# API ENDPOINTS
@app.route('/api/transactions')
def api_transactions():
    transactions = Transaction.query.order_by(Transaction.date.desc()).limit(50).all()
    return jsonify([{
        'id': t.id,
        'title': t.title,
        'amount': float(t.amount),
        'type': t.type,
        'category': t.category,
        'date': t.date.isoformat(),
        'account': t.account.name
    } for t in transactions])

@app.route('/api/stats')
def api_stats():
    today = datetime.now().date()
    start_of_month = datetime.now().replace(day=1)
    start_of_week = today - timedelta(days=today.weekday())
    
    # Bugünkü işlemler
    today_transactions = Transaction.query.filter(
        func.date(Transaction.date) == today
    ).all()
    
    # Aylık istatistikler
    monthly_stats = db.session.query(
        Transaction.type,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.date >= start_of_month
    ).group_by(Transaction.type).all()
    
    stats = {
        'today': {
            'income': sum([t.amount for t in today_transactions if t.type == 'income']),
            'expense': sum([t.amount for t in today_transactions if t.type == 'expense'])
        },
        'monthly': {t_type: float(total) for t_type, total in monthly_stats}
    }
    
    return jsonify(stats)

# KATEGORİ YÖNETİMİ
@app.route('/api/categories')
def api_categories():
    categories = db.session.query(
        Transaction.category,
        func.count(Transaction.id).label('count'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.type == 'expense',
        Transaction.date >= datetime.now().replace(day=1)
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()
    
    return jsonify([{
        'name': cat,
        'count': cnt,
        'total': float(total)
    } for cat, cnt, total in categories])

# Grafik verileri için
@app.route('/api/chart_data')
def chart_data():
    # Son 30 günlük veriler
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    daily_data = db.session.query(
        func.date(Transaction.date).label('date'),
        Transaction.type,
        func.sum(Transaction.amount).label('amount')
    ).filter(
        Transaction.date.between(start_date, end_date)
    ).group_by(func.date(Transaction.date), Transaction.type).all()
    
    return jsonify({
        'labels': [d.date.strftime('%d %b') for d in daily_data if d.type == 'expense'],
        'expenses': [float(d.amount) for d in daily_data if d.type == 'expense'],
        'incomes': [float(d.amount) for d in daily_data if d.type == 'income']
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)