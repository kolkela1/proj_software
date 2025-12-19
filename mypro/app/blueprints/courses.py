from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, abort
)
from app.db import get_db
from app.blueprints.auth import login_required, admin_required

bp = Blueprint('courses', __name__, url_prefix='/courses')

@bp.route('/')
@login_required
def index():
    db = get_db()
    courses = db.execute(
        'SELECT c.id, c.name, c.description, c.price, u.username as teacher_name '
        'FROM courses c LEFT JOIN users u ON c.teacher_id = u.id'
    ).fetchall()
    
    # Check if student is enrolled in each course
    # For now, just listing all courses. Enrollment check can be done in template or here.
    # If we want to show "Enroll" vs "View" button.
    enrolled_course_ids = []
    if g.user['role'] == 'student':
        enrollments = db.execute(
            'SELECT course_id FROM enrollments WHERE student_id = ?', (g.user['id'],)
        ).fetchall()
        enrolled_course_ids = [e['course_id'] for e in enrollments]

    return render_template('courses/index.html', courses=courses, enrolled_ids=enrolled_course_ids)

@bp.route('/create', methods=('GET', 'POST'))
@admin_required
def create():
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        teacher_id = request.form.get('teacher_id') # Optional or Required?
        error = None

        if not name:
            error = 'Course Name is required.'

        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO courses (name, description, price, teacher_id) VALUES (?, ?, ?, ?)',
                (name, description, price, teacher_id)
            )
            db.commit()
            return redirect(url_for('courses.index'))
    
    # Get teachers for dropdown
    teachers = db.execute('SELECT id, username FROM users WHERE role = "teacher"').fetchall()
    return render_template('courses/create.html', teachers=teachers)

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@admin_required
def update(id):
    db = get_db()
    course = db.execute('SELECT * FROM courses WHERE id = ?', (id,)).fetchone()
    
    if course is None:
        abort(404, f"Course id {id} doesn't exist.")

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        teacher_id = request.form.get('teacher_id')
        error = None

        if not name:
            error = 'Course Name is required.'

        if error is not None:
            flash(error)
        else:
            db.execute(
                'UPDATE courses SET name = ?, description = ?, price = ?, teacher_id = ? WHERE id = ?',
                (name, description, price, teacher_id, id)
            )
            db.commit()
            return redirect(url_for('courses.index'))

    teachers = db.execute('SELECT id, username FROM users WHERE role = "teacher"').fetchall()
    return render_template('courses/update.html', course=course, teachers=teachers)

@bp.route('/<int:id>/delete', methods=('POST',))
@admin_required
def delete(id):
    db = get_db()
    db.execute('DELETE FROM courses WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('courses.index'))

@bp.route('/<int:id>')
@login_required
def view(id):
    db = get_db()
    course = db.execute(
        'SELECT c.id, c.name, c.description, c.price, u.username as teacher_name '
        'FROM courses c LEFT JOIN users u ON c.teacher_id = u.id WHERE c.id = ?', (id,)
    ).fetchone()

    if course is None:
        abort(404, f"Course {id} does not exist.")

    # Check enrollment
    is_enrolled = False
    payment_status = 'unpaid'
    
    if g.user['role'] == 'student':
        enrollment = db.execute(
            'SELECT * FROM enrollments WHERE student_id = ? AND course_id = ?', 
            (g.user['id'], id)
        ).fetchone()
        if enrollment:
            is_enrolled = True
            
        # Check payment
        payment = db.execute(
            'SELECT status FROM payments WHERE student_id = ? AND course_id = ?',
            (g.user['id'], id)
        ).fetchone()
        if payment:
            payment_status = payment['status']
            
    # Teachers can view their own course content always? 
    # Or Admin.
    can_access_content = False
    if g.user['role'] == 'admin':
        can_access_content = True
    elif g.user['role'] == 'teacher':
        # Check if assigned teacher
        c = db.execute('SELECT teacher_id FROM courses WHERE id = ?', (id,)).fetchone()
        if c and c['teacher_id'] == g.user['id']:
             can_access_content = True
    elif is_enrolled and payment_status == 'completed':
        can_access_content = True
    
    # Get lessons if access allowed
    lessons = []
    if can_access_content:
        lessons = db.execute('SELECT * FROM lessons WHERE course_id = ?', (id,)).fetchall()

    return render_template('courses/view.html', course=course, is_enrolled=is_enrolled, payment_status=payment_status, can_access_content=can_access_content, lessons=lessons)
