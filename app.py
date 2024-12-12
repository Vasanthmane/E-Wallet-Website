from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    conn = sqlite3.connect('db.sqlite')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        ssn = request.form['ssn']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash("Passwords do not match. Please try again.")
            return redirect(url_for('signup'))

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (name, email, phone, ssn, password) VALUES (?, ?, ?, ?, ?)',
                         (f"{first_name} {last_name}", email, phone, ssn, password))
            conn.commit()
            flash("Account created successfully. Please log in.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("An account with this email, phone, or SSN already exists.")
            return redirect(url_for('signup'))
        finally:
            conn.close()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/account_info')
def account_info():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    bank_account = conn.execute('SELECT * FROM bank_accounts WHERE user_id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('account_info.html', user=user, bank_account=bank_account)

@app.route('/modify_details', methods=['GET', 'POST'])
def modify_details():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        conn = get_db_connection()
        conn.execute('UPDATE users SET name = ?, email = ?, phone = ? WHERE id = ?',
                     (name, email, phone, session['user_id']))
        conn.commit()
        flash("Details updated successfully.")
        conn.close()
        return redirect(url_for('account_info'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('modify_details.html', user=user)

@app.route('/modify_bank_account', methods=['GET', 'POST'])
def modify_bank_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        account_number = request.form['account_number']
        routing_number = request.form['routing_number']
        phone = request.form['phone']

        existing_account = conn.execute('SELECT * FROM bank_accounts WHERE user_id = ?', (session['user_id'],)).fetchone()
        if existing_account:
            conn.execute('UPDATE bank_accounts SET account_number = ?, routing_number = ?, phone = ? WHERE user_id = ?',
                         (account_number, routing_number, phone, session['user_id']))
            flash("Bank account updated successfully.")
        else:
            conn.execute('INSERT INTO bank_accounts (user_id, account_number, routing_number, phone) VALUES (?, ?, ?, ?)',
                         (session['user_id'], account_number, routing_number, phone))
            flash("Bank account added successfully.")
        
        conn.commit()
        conn.close()
        return redirect(url_for('account_info'))

    bank_account = conn.execute('SELECT * FROM bank_accounts WHERE user_id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('modify_bank_account.html', bank_account=bank_account)

@app.route('/send_money', methods=['GET', 'POST'])
def send_money():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    success = False  # Track success state for dynamic rendering
    if request.method == 'POST':
        recipient = request.form['recipient']
        amount = float(request.form['amount'])
        conn = get_db_connection()
        receiver = conn.execute('SELECT * FROM users WHERE email = ? OR phone = ?', (recipient, recipient)).fetchone()
        
        if receiver:
            conn.execute('INSERT INTO transactions (sender_id, receiver_id, amount, date, transaction_type) VALUES (?, ?, ?, ?, ?)',
                         (session['user_id'], receiver['id'], amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'send'))
            conn.commit()
            success = True  # Flag success for displaying the message
        else:
            flash("Recipient not found. Please check the email or phone number.")
        conn.close()
        return render_template('send_money.html', success=success)
    return render_template('send_money.html', success=success)

@app.route('/request_money', methods=['GET', 'POST'])
def request_money():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        sender = request.form['sender']
        amount = float(request.form['amount'])
        conn = get_db_connection()
        sender_user = conn.execute('SELECT * FROM users WHERE email = ? OR phone = ?', (sender, sender)).fetchone()

        if sender_user:
            conn.execute('INSERT INTO transactions (sender_id, receiver_id, amount, date, transaction_type) VALUES (?, ?, ?, ?, ?)',
                         (sender_user['id'], session['user_id'], amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'request'))
            conn.commit()
            flash("Request sent successfully.")
        else:
            flash("Sender not found. Please check the email or phone number.")
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('request_money.html')

@app.route('/statements', methods=['GET', 'POST'])
def statements():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    transactions = []

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        transactions = conn.execute('''
            SELECT * FROM transactions
            WHERE (sender_id = ? OR receiver_id = ?)
            AND date BETWEEN ? AND ?
        ''', (session['user_id'], session['user_id'], start_date, end_date)).fetchall()
    else:
        transactions = conn.execute('SELECT * FROM transactions WHERE sender_id = ? OR receiver_id = ?', 
                                    (session['user_id'], session['user_id'])).fetchall()

    conn.close()
    return render_template('statements.html', transactions=transactions)

@app.route('/search_transactions', methods=['GET', 'POST'])
def search_transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    transactions = []
    if request.method == 'POST':
        search_term = request.form['search']
        conn = get_db_connection()
        transactions = conn.execute('''
            SELECT * FROM transactions
            WHERE (sender_id = (SELECT id FROM users WHERE email = ? OR phone = ? OR ssn = ?)
            OR receiver_id = (SELECT id FROM users WHERE email = ? OR phone = ? OR ssn = ?))
            AND (sender_id = ? OR receiver_id = ?)
        ''', (search_term, search_term, search_term, search_term, search_term, search_term, session['user_id'], session['user_id'])).fetchall()
        conn.close()
    return render_template('search_transactions.html', transactions=transactions)

@app.route('/transaction_statistics')
def transaction_statistics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()

    # Total amount sent and received
    total_sent = conn.execute(
        'SELECT SUM(amount) FROM transactions WHERE sender_id = ?',
        (session['user_id'],)
    ).fetchone()[0] or 0
    total_received = conn.execute(
        'SELECT SUM(amount) FROM transactions WHERE receiver_id = ?',
        (session['user_id'],)
    ).fetchone()[0] or 0

    # Monthly statistics (totals and averages)
    monthly_stats = conn.execute('''
        SELECT strftime('%Y-%m', date) AS month,
               SUM(CASE WHEN sender_id = ? THEN amount ELSE 0 END) AS total_sent,
               SUM(CASE WHEN receiver_id = ? THEN amount ELSE 0 END) AS total_received
        FROM transactions
        GROUP BY month
        ORDER BY month
    ''', (session['user_id'], session['user_id'])).fetchall()

    # Parse monthly stats for rendering
    parsed_stats = []
    for row in monthly_stats:
        parsed_stats.append({
            'month': row['month'],
            'total_sent': row['total_sent'],
            'total_received': row['total_received']
        })

    # Identify largest transaction
    largest_transaction = conn.execute('''
        SELECT amount, transaction_type
        FROM transactions
        WHERE sender_id = ? OR receiver_id = ?
        ORDER BY amount DESC
        LIMIT 1
    ''', (session['user_id'], session['user_id'])).fetchone()

    conn.close()

    return render_template(
        'transaction_statistics.html',
        total_sent=total_sent,
        total_received=total_received,
        monthly_stats=parsed_stats,
        largest_transaction=largest_transaction
    )

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
