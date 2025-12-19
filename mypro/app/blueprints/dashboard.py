from flask import (
    Blueprint, render_template, g
)
from app.blueprints.auth import login_required

bp = Blueprint('dashboard', __name__)

from app.db import get_db

@bp.route('/')
@login_required
def index():
    db = get_db()
    
    # Statistics
    student_count = db.execute("SELECT COUNT(*) FROM users WHERE role = 'student'").fetchone()[0]
    teacher_count = db.execute("SELECT COUNT(*) FROM users WHERE role = 'teacher'").fetchone()[0]
    course_count = db.execute('SELECT COUNT(*) FROM courses').fetchone()[0]
    
    # Total Revenue (Completed payments)
    total_revenue = db.execute(
        "SELECT SUM(amount) FROM payments WHERE status = 'completed'"
    ).fetchone()[0] or 0.0
    
    # Monthly Revenue
    monthly_revenue = db.execute(
        "SELECT SUM(amount) FROM payments WHERE status = 'completed' AND strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')"
    ).fetchone()[0] or 0.0

    # Pending Payments count
    pending_payments = db.execute(
        "SELECT COUNT(*) FROM payments WHERE status = 'pending'"
    ).fetchone()[0]

    # Context specific data
    my_courses = []
    if g.user['role'] == 'student':
        my_courses = db.execute(
            '''SELECT c.id, c.name, e.enrolled_at 
               FROM courses c 
               JOIN enrollments e ON c.id = e.course_id 
               WHERE e.student_id = ?''', (g.user['id'],)
        ).fetchall()
    elif g.user['role'] == 'teacher':
        my_courses = db.execute(
            'SELECT id, name, price FROM courses WHERE teacher_id = ?', (g.user['id'],)
        ).fetchall()

    return render_template('dashboard/index.html',
                           student_count=student_count,
                           teacher_count=teacher_count,
                           course_count=course_count,
                           total_revenue=total_revenue,
                           monthly_revenue=monthly_revenue,
                           pending_payments=pending_payments,
                           my_courses=my_courses
                           )
