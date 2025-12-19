from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from app.db import get_db
from app.blueprints.auth import login_required, student_required
import uuid

bp = Blueprint('payments', __name__, url_prefix='/payments')

@bp.route('/checkout/<int:course_id>', methods=('GET', 'POST'))
@login_required
def checkout(course_id):
    db = get_db()
    course = db.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    
    if not course:
        flash("Course not found.")
        return redirect(url_for('courses.index'))
        
    # Check if already paid
    existing_payment = db.execute(
        'SELECT status FROM payments WHERE student_id = ? AND course_id = ?',
        (g.user['id'], course_id)
    ).fetchone()
    
    if existing_payment and existing_payment['status'] == 'completed':
        flash("You have already paid for this course.")
        return redirect(url_for('courses.view', id=course_id))

    if request.method == 'POST':
        # Simulate payment processing
        card_number = request.form['card_number'] # Not storing this!
        
        # In a real app, we'd call Stripe/PayPal API here.
        # Simulation:
        
        payment_status = 'completed'
        transaction_id = str(uuid.uuid4())
        amount = course['price']
        
        # 1. Record Payment
        db.execute(
            'INSERT INTO payments (student_id, course_id, amount, status, transaction_id) VALUES (?, ?, ?, ?, ?)',
            (g.user['id'], course_id, amount, payment_status, transaction_id)
        )
        
        # 2. Create Enrollment (if not exists)
        try:
            db.execute(
                'INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)',
                (g.user['id'], course_id)
            )
        except db.IntegrityError:
            pass # Already enrolled, maybe pending payment before
            
        db.commit()
        
        flash("Payment successful! You are enrolled.", "success")
        return redirect(url_for('courses.view', id=course_id))

    return render_template('payments/checkout.html', course=course)
