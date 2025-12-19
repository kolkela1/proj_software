import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory, current_app, abort
)
from werkzeug.utils import secure_filename
from app.db import get_db
from app.blueprints.auth import login_required, teacher_required, admin_required

bp = Blueprint('lessons', __name__, url_prefix='/lessons')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf', 'mp4', 'png', 'jpg', 'jpeg', 'txt', 'docx'}

@bp.route('/create/<int:course_id>', methods=('GET', 'POST'))
@login_required
def create(course_id):
    # Check permission: Teacher or Admin
    if g.user['role'] == 'student':
        abort(403)
        
    db = get_db()
    course = db.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    if not course:
        abort(404)
        
    if g.user['role'] == 'teacher' and course['teacher_id'] != g.user['id']:
        abort(403, "You can only add lessons to your own courses.")

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        video_url = request.form['video_url']
        
        file = request.files['file']
        file_path = None
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # Save format: course_id_filename (to avoid collisions maybe? or subfolders)
            # Simple approach: default filename
            save_name = f"{course_id}_{filename}"
            file.save(os.path.join(upload_folder, save_name))
            file_path = save_name

        db.execute(
            'INSERT INTO lessons (course_id, title, content, file_path, video_url) VALUES (?, ?, ?, ?, ?)',
            (course_id, title, content, file_path, video_url)
        )
        db.commit()
        flash("Lesson added successfully!", "success")
        return redirect(url_for('courses.view', id=course_id))

    return render_template('lessons/create.html', course=course)

@bp.route('/download/<int:id>')
@login_required
def download(id):
    db = get_db()
    lesson = db.execute('SELECT * FROM lessons WHERE id = ?', (id,)).fetchone()
    if not lesson:
        abort(404)
        
    course_id = lesson['course_id']
    
    # Access Check
    can_access = False
    if g.user['role'] == 'admin':
        can_access = True
    elif g.user['role'] == 'teacher':
        course = db.execute('SELECT teacher_id FROM courses WHERE id = ?', (course_id,)).fetchone()
        if course and course['teacher_id'] == g.user['id']:
            can_access = True
    elif g.user['role'] == 'student':
        # Check enrollment & payment
        enrollment = db.execute('SELECT * FROM enrollments WHERE student_id = ? AND course_id = ?', 
                                (g.user['id'], course_id)).fetchone()
        payment = db.execute('SELECT status FROM payments WHERE student_id = ? AND course_id = ?', 
                             (g.user['id'], course_id)).fetchone()
                             
        if enrollment and payment and payment['status'] == 'completed':
            can_access = True
            
    if not can_access:
        abort(403, "Access Denied. Please enroll and pay for the course.")
        
    if not lesson['file_path']:
        abort(404, "No file attached to this lesson.")
        
    upload_folder = os.path.join(current_app.root_path, 'uploads')
    return send_from_directory(upload_folder, lesson['file_path'], as_attachment=True)

@bp.route('/delete/<int:id>', methods=('POST',))
@login_required
def delete(id):
    db = get_db()
    lesson = db.execute('SELECT * FROM lessons WHERE id = ?', (id,)).fetchone()
    if not lesson:
        abort(404)
        
    # Permission check (only owner teacher or admin)
    allow = False
    if g.user['role'] == 'admin':
        allow = True
    else:
        course = db.execute('SELECT teacher_id FROM courses WHERE id = ?', (lesson['course_id'],)).fetchone()
        if course and course['teacher_id'] == g.user['id']:
            allow = True
            
    if not allow:
        abort(403)
        
    # Delete file if exists
    if lesson['file_path']:
        try:
            os.remove(os.path.join(current_app.root_path, 'uploads', lesson['file_path']))
        except:
            pass # File might be missing
            
    db.execute('DELETE FROM lessons WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('courses.view', id=lesson['course_id']))
