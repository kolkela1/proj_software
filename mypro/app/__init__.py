import os
from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'database_v2.db'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Database setup
    from . import db
    db.init_app(app)

    # Register Blueprints
    from .blueprints import auth, dashboard, courses, payments, lessons
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(courses.bp)
    app.register_blueprint(payments.bp)
    app.register_blueprint(lessons.bp)
    
    # Old blueprints are likely broken due to schema change, disabling them for now
    # from .blueprints import teachers, parents, classes, students, rooms, lessons, attendance, grades, accounts, reports
    # app.register_blueprint(teachers.bp)
    # ...
    
    from .blueprints import public
    app.register_blueprint(public.bp)

    # Root is now handled by public.home

    return app
