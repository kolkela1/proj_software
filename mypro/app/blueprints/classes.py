from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from app.blueprints.auth import login_required
from app.db import get_db

bp = Blueprint('classes', __name__, url_prefix='/classes')

@bp.route('/')
@login_required
def index():
    db = get_db()
    classes = db.execute('SELECT * FROM classes').fetchall()
    return render_template('classes/index.html', classes=classes)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        class_name = request.form['class_name']
        level = request.form['level']
        monthly_price = request.form['monthly_price']
        error = None

        if not class_name:
            error = 'Class Name is required.'

        if error is None:
            db = get_db()
            db.execute(
                'INSERT INTO classes (class_name, level, monthly_price) VALUES (?, ?, ?)',
                (class_name, level, monthly_price)
            )
            db.commit()
            return redirect(url_for('classes.index'))

        flash(error)

    return render_template('classes/create.html')
