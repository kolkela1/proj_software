from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from app.blueprints.auth import login_required
from app.db import get_db

bp = Blueprint('grades', __name__, url_prefix='/grades')

@bp.route('/')
@login_required
def index():
    db = get_db()
    exams = db.execute(
        'SELECT e.id, s.name as student_name, e.score, m.month_number, m.year'
        ' FROM exams e'
        ' JOIN students s ON e.student_id = s.id'
        ' LEFT JOIN months m ON e.month_id = m.id'
        ' ORDER BY e.id DESC'
    ).fetchall()
    return render_template('grades/index.html', exams=exams)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    db = get_db()
    if request.method == 'POST':
        student_id = request.form['student_id']
        month_id = request.form['month_id'] # User selects month
        score = request.form['score']
        
        # If month is not selected or we need to manage it, assuming it exists for now based on previous lesson logic
        # OR we can let user pick "Month X, Year Y" from a dropdown of months in DB?
        # Let's assume we list months.
        
        db.execute(
            'INSERT INTO exams (student_id, month_id, score) VALUES (?, ?, ?)',
            (student_id, month_id, score)
        )
        db.commit()
        return redirect(url_for('grades.index'))

    students = db.execute('SELECT id, name FROM students WHERE active = 1').fetchall()
    months = db.execute('SELECT id, month_number, year FROM months ORDER BY year DESC, month_number DESC').fetchall()
    
    return render_template('grades/create.html', students=students, months=months)
