from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from werkzeug.security import generate_password_hash
from app.db import get_db

bp = Blueprint('public', __name__)

@bp.route('/')
def home():
    return render_template('public/home.html')

@bp.route('/about')
def about():
    return render_template('public/about.html')

@bp.route('/courses')
def courses():
    db = get_db()
    # Fetch classes to show as courses
    courses = db.execute('SELECT * FROM classes').fetchall()
    return render_template('public/courses.html', courses=courses)

@bp.route('/contact')
def contact():
    return render_template('public/contact.html')


