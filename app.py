from flask import Flask, render_template, request, redirect, url_for
from models import db, Account, Transaction
from decimal import Decimal # Para hesapları için gerekli

app = Flask(__name__)

# Veritabanı ayarlarını kendi bilgilerine göre güncelle
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://finans_user:finans123@localhost/finans_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Tabloları oluştur (Sadece ilk çalıştırmada veya değişimde gerekir)
with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    accounts = Account.query.all()
    # Son 10 işlemi çekelim
    recent_transactions = Transaction.query.order_by(Transaction.date.desc()).limit(10).all()
    return render_template('dashboard.html', accounts=accounts, transactions=recent_transactions)


@app.route('/add_account', methods=['POST'])
def add_account():
    name = request.form.get('name')
    balance = request.form.get('balance')
    currency = request.form.get('currency')
    if name and balance:
        new_acc = Account(name=name, balance=Decimal(balance), currency=currency)
        db.session.add(new_acc)
        db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    amount = request.form.get('amount')
    acc_id = request.form.get('account_id')
    cat = request.form.get('category')
    t_type = request.form.get('type') # 'income' veya 'expense'
    
    if amount and acc_id:
        # İşlemi kaydet
        new_t = Transaction(
            amount=Decimal(amount),
            account_id=int(acc_id),
            category=cat,
            type=t_type
        )
        # Hesap bakiyesini güncelle
        account = Account.query.get(acc_id)
        if t_type == 'income':
            account.balance += Decimal(amount)
        else:
            account.balance -= Decimal(amount)
            
        db.session.add(new_t)
        db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/delete_transaction/<int:id>', methods=['POST'])
def delete_transaction(id):
    t = Transaction.query.get_or_404(id)
    # Silinen işlemin miktarını hesaba iade edelim
    account = Account.query.get(t.account_id)
    if t.type == 'income':
        account.balance -= t.amount
    else:
        account.balance += t.amount
    
    db.session.delete(t)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete_account/<int:id>', methods=['POST'])
def delete_account(id):
    acc = Account.query.get_or_404(id)
    # Önce bu hesaba ait tüm işlemleri silmemiz gerekir (Postgres kısıtlaması)
    Transaction.query.filter_by(account_id=id).delete()
    db.session.delete(acc)
    db.session.commit()
    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    app.run(debug=True)