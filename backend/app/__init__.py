from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from celery import Celery, Task
from celery.schedules import crontab
from werkzeug.security import generate_password_hash

# Initialize Extensions
db = SQLAlchemy()
cache = Cache()

def create_app():
    app = Flask(__name__)
    
    # Core Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-required'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Redis, Celery & Caching Configuration
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    app.config['CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP'] = True # Fixes the warning you saw
    
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/1'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    
    # Scheduled Jobs Configuration
    app.config['CELERY_BEAT_SCHEDULE'] = {
        'daily-reminders': {
            'task': 'app.tasks.send_daily_reminders',
            'schedule': crontab(hour=8, minute=0), # Runs daily at 8:00 AM
        },
        'monthly-reports': {
            'task': 'app.tasks.generate_monthly_reports',
            'schedule': crontab(day_of_month=1, hour=9, minute=0), # Runs 1st of month at 9:00 AM
        },
    }

    # Init Extensions
    db.init_app(app)
    cache.init_app(app)
    
    # Initialize Celery
    app.extensions['celery'] = celery_init_app(app)

    # Import models explicitly
    from .models import User, Doctor, Patient, Department, Appointment, Treatment
    
    # Register Blueprints
    from .api.auth import auth_bp
    from .api.admin import admin_bp
    from .api.doctor import doctor_bp
    from .api.patient import patient_bp

    app.register_blueprint(auth_bp, url_prefix='/auth') 
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(patient_bp, url_prefix='/patient')

    with app.app_context():
        db.create_all()

        # Admin Seeding
        if not User.query.filter_by(role='admin').first():
            hashed_password = generate_password_hash('admin123')
            new_admin = User(email='admin@hospital.com', password=hashed_password, role='admin', is_active=True)
            db.session.add(new_admin)
            db.session.commit()
            print("Admin user seeded.")

        # Department Seeding
        if not Department.query.first():
            departments = ['Cardiology', 'Dermatology', 'Neurology', 'Orthopedics', 'Pediatrics']
            for dep_name in departments:
                db.session.add(Department(name=dep_name, description=f'Department of {dep_name}'))
            db.session.commit()
            print("Departments seeded.")

    return app

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    
    # --- CRITICAL FIX: Explicitly load config values ---
    celery_app.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        beat_schedule=app.config['CELERY_BEAT_SCHEDULE'],
        broker_connection_retry_on_startup=True
    )
    # ---------------------------------------------------

    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app