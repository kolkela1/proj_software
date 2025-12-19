from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from app.blueprints.auth import login_required
from app.db import get_db

bp = Blueprint('rooms', __name__, url_prefix='/rooms')

@bp.route('/')
@login_required
def index():
    db = get_db()
    rooms = db.execute('SELECT * FROM rooms').fetchall()
    return render_template('rooms/index.html', rooms=rooms)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        room_name = request.form['room_name']
        capacity = request.form['capacity']
        error = None

        if not room_name:
            error = 'Room Name is required.'

        if error is None:
            db = get_db()
            db.execute(
                'INSERT INTO rooms (room_name, capacity) VALUES (?, ?)',
                (room_name, capacity)
            )
            db.commit()
            return redirect(url_for('rooms.index'))

        flash(error)

    return render_template('rooms/create.html')
