from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.security import generate_password_hash
from app.blueprints.auth import login_required
from app.db import get_db

bp = Blueprint('parents', __name__, url_prefix='/parents')

@bp.route('/')
@login_required
def index():
    db = get_db()
    parents = db.execute(
        'SELECT p.id, p.name, p.phone, p.email, u.username'
        ' FROM parents p JOIN users u ON p.user_id = u.id'
    ).fetchall()
    return render_template('parents/index.html', parents=parents)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        email = request.form['email']
        error = None

        if not name:
            error = 'Name is required.'
        elif not username:
            error = 'Username is required.'

        if error is None:
            db = get_db()
            try:
                # Create User
                cursor = db.execute(
                    'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                    (username, generate_password_hash(password), 'parent')
                )
                user_id = cursor.lastrowid

                # Create Parent
                db.execute(
                    'INSERT INTO parents (user_id, name, phone, email) VALUES (?, ?, ?, ?)',
                    (user_id, name, phone, email)
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for('parents.index'))

        flash(error)

    return render_template('parents/create.html')
