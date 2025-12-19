import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or g.user['role'] != 'admin':
            abort(403)
        return view(**kwargs)
    return wrapped_view

def teacher_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or g.user['role'] not in ['admin', 'teacher']:
             abort(403)
        return view(**kwargs)
    return wrapped_view

def student_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
             abort(403)
        # Students can access student routes. Admins/Teachers typically don't enroll?
        # For simplicity, if role is student.
        # But maybe we allow everyone to view courses?
        # Strict validation:
        # if g.user['role'] != 'student': abort(403)
        return view(**kwargs)
    return wrapped_view

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            return redirect(url_for('dashboard.index'))
        

        flash(error)

    return render_template('auth/login.html')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'student') # Default to student
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif role not in ['student', 'teacher']: # Admin should not be self-registered ideally
            error = 'Invalid role selected.'

        if error is None:
            try:
                db.execute(
                    'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                    (username, email, generate_password_hash(password), role)
                )
                db.commit()
                flash(f'Registration successful! Please login.', 'success')
                return redirect(url_for('auth.login'))
            except db.IntegrityError:
                error = f"User {username} or Email {email} is already registered."

        flash(error)

    return render_template('auth/register.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
