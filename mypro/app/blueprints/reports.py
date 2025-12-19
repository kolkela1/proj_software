from flask import (
    Blueprint, render_template
)
from app.blueprints.auth import login_required
from app.db import get_db

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/')
@login_required
def index():
    db = get_db()
    # Basic aggregates
    total_students = db.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    total_teachers = db.execute('SELECT COUNT(*) FROM teachers').fetchone()[0]
    # Simple income
    total_income = db.execute('SELECT SUM(amount) FROM payments').fetchone()[0] or 0
    total_expenses = db.execute('SELECT SUM(amount) FROM expenses').fetchone()[0] or 0
    net_profit = total_income - total_expenses
    
    return render_template('reports/index.html', 
                            total_students=total_students, 
                            total_teachers=total_teachers,
                            total_income=total_income,
                            total_expenses=total_expenses,
                            net_profit=net_profit)
