from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import os
from types import SimpleNamespace
import bank_database as db

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# -------------------- Login Auth -------------------- #
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.validate_user(username, password):

            session['username'] = username
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# -------------------- Account Operations -------------------- #
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        accNo = int(request.form['accNo'])
        name = request.form['name']
        acc_type = request.form['type'].upper()
        deposit = int(request.form['deposit'])
        try:
            db.create_account(accNo, name, acc_type, deposit)
            flash('Account created successfully')
        except Exception as e:
            flash(str(e))
        return redirect(url_for('create'))
    return render_template('create.html')

@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    if request.method == 'POST':
        accNo = int(request.form['accNo'])
        db.delete_account(accNo)
        flash('Account deleted')
        return redirect(url_for('delete'))
    return render_template('delete.html')

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        accNo = int(request.form['accNo'])
        amount = int(request.form['amount'])
        try:
            db.update_balance(accNo, amount, mode=1)
            flash('Deposited successfully')
        except Exception as e:
            flash(str(e))
        return redirect(url_for('deposit'))
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'POST':
        accNo = int(request.form['accNo'])
        amount = int(request.form['amount'])
        try:
            db.update_balance(accNo, amount, mode=2)
            flash('Withdrawn successfully')
        except Exception as e:
            flash(str(e))
        return redirect(url_for('withdraw'))
    return render_template('withdraw.html')

@app.route('/balance', methods=['GET', 'POST'])
@login_required
def balance():
    result = None
    if request.method == 'POST':
        accNo = int(request.form['accNo'])
        result = db.get_balance(accNo)
        if result is None:
            flash('Account not found')
    return render_template('balance.html', result=result)

@app.route('/modify', methods=['GET', 'POST'])
@login_required
def modify():
    account = None
    if request.method == 'POST':
        # update flow (form includes hidden 'update' flag)
        if request.form.get('update'):
            accNo = int(request.form['accNo'])
            name = request.form['name']
            acc_type = request.form['type'].upper()
            deposit = int(request.form['deposit'])
            db.modify_account(accNo, name, acc_type, deposit)
            flash('Account modified')
            return redirect(url_for('modify'))
        # lookup flow: fetch account and show form
        else:
            accNo = int(request.form['accNo'])
            row = db.get_account(accNo)
            if row:
                account = SimpleNamespace(accNo=row[0], name=row[1], type=row[2], deposit=row[3])
            else:
                flash('Account not found')
    return render_template('modify.html', account=account)


@app.route('/accounts')
@login_required
def accounts():
    rows = db.get_all_accounts()
    accounts = []
    for r in rows:
        accounts.append(SimpleNamespace(accNo=r[0], name=r[1], type=r[2], deposit=r[3]))
    return render_template('accounts.html', accounts=accounts)

# -------------------- Dashboard -------------------- #
@app.route('/dashboard')
@login_required
def dashboard():
    total_accounts, total_balance, saving_count, current_count = db.get_dashboard_stats()
    return render_template('dashboard.html',
                           total_accounts=total_accounts,
                           total_balance=total_balance,
                           saving_count=saving_count,
                           current_count=current_count)

# -------------------- Forgot Password -------------------- #
@app.route('/forgot_password')
def forgot_password():
    flash('This is a placeholder. Implement password reset logic.')
    return redirect(url_for('login'))

# -------------------- Signup -------------------- #
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if db.register_user(username, password):
            flash('Account created successfully. Please log in.')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Choose another.')
    return render_template('signup.html')


if __name__ == '__main__':
    # Read production configuration from environment variables
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    # Allow overriding the secret key via env var in production
    app.secret_key = os.environ.get('SECRET_KEY', app.secret_key)
    app.run(host=host, port=port, debug=debug)
