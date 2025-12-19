import sys
from app import create_app, db
from app.db import get_db
from werkzeug.security import generate_password_hash

def seed():
    app = create_app()
    with app.app_context():
        database = get_db()
        
        # Clear existing data (Optional, good for creating fresh state)
        # database.execute('DELETE FROM users')
        # database.execute('DELETE FROM courses')
        # database.execute('DELETE FROM lessons')
        # database.execute('DELETE FROM enrollments')
        # database.execute('DELETE FROM payments')
        
        print("Creating Users...")
        # Create Admin
        try:
            database.execute(
                'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                ('admin', 'admin@school.com', generate_password_hash('admin123'), 'admin')
            )
        except:
            print("Admin already exists")

        # Create Teacher
        teacher_id = None
        try:
            cursor = database.execute(
                'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                ('teacher', 'teacher@school.com', generate_password_hash('teacher123'), 'teacher')
            )
            teacher_id = cursor.lastrowid
        except:
            print("Teacher already exists")
            teacher = database.execute("SELECT id FROM users WHERE username='teacher'").fetchone()
            teacher_id = teacher['id']

        # Create Student
        try:
            database.execute(
                'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                ('student', 'student@school.com', generate_password_hash('student123'), 'student')
            )
        except:
            print("Student already exists")

        print("Creating Course...")
        course_id = None
        # Create Course
        if teacher_id:
            cursor = database.execute(
                'INSERT INTO courses (name, description, price, teacher_id) VALUES (?, ?, ?, ?)',
                ('Python Masterclass', 'Learn Python from scratch to advanced.', 99.99, teacher_id)
            )
            course_id = cursor.lastrowid
            
            # Create Lessons
            if course_id:
                print("Creating Lessons...")
                database.execute(
                    'INSERT INTO lessons (course_id, title, content, is_published) VALUES (?, ?, ?, ?)',
                    (course_id, '1. Introduction', 'Welcome to the course.', 1)
                )
                database.execute(
                    'INSERT INTO lessons (course_id, title, content, is_published) VALUES (?, ?, ?, ?)',
                    (course_id, '2. Setup Environment', 'Install Python and VS Code.', 1)
                )

        database.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed()
