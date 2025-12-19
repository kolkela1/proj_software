from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from app.blueprints.auth import login_required
from app.db import get_db

bp = Blueprint('accounts', __name__, url_prefix='/accounts')

@bp.route('/')
@login_required
def index():
    return render_template('accounts/index.html')

@bp.route('/payments')
@login_required
def payments_index():
    db = get_db()
    payments = db.execute(
        'SELECT p.id, s.name as student_name, p.amount, p.payment_date, m.month_number, m.year'
        ' FROM payments p'
        ' JOIN students s ON p.student_id = s.id'
        ' LEFT JOIN months m ON p.month_id = m.id'
        ' ORDER BY p.payment_date DESC'
    ).fetchall()
    return render_template('accounts/payments.html', payments=payments)

@bp.route('/payments/create', methods=('GET', 'POST'))
@login_required
def create_payment():
    db = get_db()
    if request.method == 'POST':
        student_id = request.form['student_id']
        month_id = request.form['month_id']
        amount = request.form['amount']
        
        db.execute(
            'INSERT INTO payments (student_id, month_id, amount) VALUES (?, ?, ?)',
            (student_id, month_id, amount)
        )
        db.commit()
        return redirect(url_for('accounts.payments_index'))
        
    students = db.execute('SELECT id, name FROM students WHERE active = 1').fetchall()
    months = db.execute('SELECT id, month_number, year FROM months ORDER BY year DESC, month_number DESC').fetchall()
    return render_template('accounts/create_payment.html', students=students, months=months)

@bp.route('/expenses')
@login_required
def expenses_index():
    db = get_db()
    expenses = db.execute('SELECT * FROM expenses ORDER BY expense_date DESC').fetchall()
    return render_template('accounts/expenses.html', expenses=expenses)

@bp.route('/expenses/create', methods=('GET', 'POST'))
@login_required
def create_expense():
    if request.method == 'POST':
        title = request.form['title']
        amount = request.form['amount']
        notes = request.form['notes']
        
        db = get_db()
        db.execute(
            'INSERT INTO expenses (title, amount, notes) VALUES (?, ?, ?)',
            (title, amount, notes)
        )
        db.commit()
        return redirect(url_for('accounts.expenses_index'))
        
    return render_template('accounts/create_expense.html')
