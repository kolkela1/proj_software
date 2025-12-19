from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import generate_password_hash
from app.blueprints.auth import login_required
from app.db import get_db

bp = Blueprint('teachers', __name__, url_prefix='/teachers')

@bp.route('/')
@login_required
def index():
    db = get_db()
    teachers = db.execute(
        'SELECT t.id, t.name, t.phone, t.subject, t.salary, u.username'
        ' FROM teachers t JOIN users u ON t.user_id = u.id'
    ).fetchall()
    return render_template('teachers/index.html', teachers=teachers)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        subject = request.form['subject']
        salary = request.form['salary']
        error = None

        if not name:
            error = 'Name is required.'
        elif not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            db = get_db()
            try:
                # Create User first
                cursor = db.execute(
                    'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                    (username, generate_password_hash(password), 'teacher')
                )
                user_id = cursor.lastrowid

                # Create Teacher
                db.execute(
                    'INSERT INTO teachers (user_id, name, phone, subject, salary) VALUES (?, ?, ?, ?, ?)',
                    (user_id, name, phone, subject, salary)
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for('teachers.index'))

        flash(error)

    return render_template('teachers/create.html')
