from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from app.blueprints.auth import login_required
from app.db import get_db

bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@bp.route('/lesson/<int:lesson_id>', methods=('GET', 'POST'))
@login_required
def lesson_attendance(lesson_id):
    db = get_db()
    lesson = db.execute(
        'SELECT l.*, c.class_name, c.id as class_id'
        ' FROM lessons l JOIN classes c ON l.class_id = c.id'
        ' WHERE l.id = ?', (lesson_id,)
    ).fetchone()
    
    if lesson is None:
        flash('Lesson not found.')
        return redirect(url_for('lessons.index'))

    if request.method == 'POST':
        # Save attendance
        # The form will submit student_id and status (present/absent)
        # We assume checkboxes or radios named 'status_<student_id>'
        
        # Get all students in this class to know who to check
        students = db.execute(
            'SELECT id FROM students WHERE class_id = ? AND active = 1', (lesson['class_id'],)
        ).fetchall()
        
        for student in students:
            sid = student['id']
            status = request.form.get(f'status_{sid}', 'absent') # Default absent if unchecked/missing
            score = request.form.get(f'score_{sid}', 0) # participation score
            
            # Check if exists
            exists = db.execute(
                'SELECT id FROM student_attendance WHERE lesson_id = ? AND student_id = ?',
                (lesson_id, sid)
            ).fetchone()
            
            if exists:
                db.execute(
                    'UPDATE student_attendance SET status = ?, score = ? WHERE lesson_id = ? AND student_id = ?',
                    (status, score, lesson_id, sid)
                )
            else:
                db.execute(
                    'INSERT INTO student_attendance (lesson_id, student_id, status, score) VALUES (?, ?, ?, ?)',
                    (lesson_id, sid, status, score)
                )
        db.commit()
        flash('Attendance saved.')
        return redirect(url_for('lessons.index'))

    # Get students and their current attendance status if any
    students = db.execute(
        'SELECT s.id, s.name, sa.status, sa.score'
        ' FROM students s'
        ' LEFT JOIN student_attendance sa ON s.id = sa.student_id AND sa.lesson_id = ?'
        ' WHERE s.class_id = ? AND s.active = 1',
        (lesson_id, lesson['class_id'])
    ).fetchall()

    return render_template('attendance/lesson.html', lesson=lesson, students=students)
