from flask import Blueprint, jsonify
from models import Transaction, Account
from datetime import datetime, timedelta
from sqlalchemy import func
import pytz

api_bp = Blueprint('api', __name__)
NYC_TZ = pytz.timezone('America/New_York')


@api_bp.route('/transactions')
def api_transactions():
    """API: İşlemler - MEVCUT KODUNUZ BURAYA"""
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


@api_bp.route('/stats')
def api_stats():
    """API: İstatistikler - MEVCUT KODUNUZ BURAYA"""
    nyc_now = datetime.now(NYC_TZ)
    today = nyc_now.date()
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
@api_bp.route('/categories')
def api_categories():
    """API: Kategoriler - MEVCUT KODUNUZ BURAYA"""
    nyc_now = datetime.now(NYC_TZ)
    start_of_month = nyc_now.replace(day=1)

    categories = db.session.query(
        Transaction.category,
        func.count(Transaction.id).label('count'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.type == 'expense',
        Transaction.date >= start_of_month
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()
    
    return jsonify([{
        'name': cat,
        'count': cnt,
        'total': float(total)
    } for cat, cnt, total in categories])


# Grafik verileri için
@api_bp.route('/chart_data')
def chart_data():
    """API: Grafik verileri - MEVCUT KODUNUZ BURAYA"""
    # Son 30 günlük veriler
    nyc_now = datetime.now(NYC_TZ)
    end_date = nyc_now
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
