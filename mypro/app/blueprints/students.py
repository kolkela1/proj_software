from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from app.blueprints.auth import login_required
from app.db import get_db

bp = Blueprint('students', __name__, url_prefix='/students')

@bp.route('/')
@login_required
def index():
    db = get_db()
    students = db.execute(
        'SELECT s.id, s.name, s.gender, s.phone, c.class_name, p.name as parent_name, s.active'
        ' FROM students s'
        ' LEFT JOIN classes c ON s.class_id = c.id'
        ' LEFT JOIN parents p ON s.parent_id = p.id'
    ).fetchall()
    return render_template('students/index.html', students=students)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    db = get_db()
    
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        phone = request.form['phone']
        parent_id = request.form['parent_id']
        class_id = request.form['class_id']
        error = None

        if not name:
            error = 'Name is required.'
        
        if error is None:
            db.execute(
                'INSERT INTO students (name, gender, phone, parent_id, class_id) VALUES (?, ?, ?, ?, ?)',
                (name, gender, phone, parent_id, class_id)
            )
            db.commit()
            return redirect(url_for('students.index'))

        flash(error)

    parents = db.execute('SELECT id, name FROM parents').fetchall()
    classes = db.execute('SELECT id, class_name FROM classes').fetchall()
    
    return render_template('students/create.html', parents=parents, classes=classes)
