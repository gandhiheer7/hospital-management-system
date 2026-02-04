from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

# Initialize SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'dev-secret-key-required'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Import models explicitly to ensure they are registered with SQLAlchemy
    from .models import User, Doctor, Patient, Department, Appointment, Treatment

    with app.app_context():
        # [cite_start]Programmatic Database Creation [cite: 17]
        db.create_all()

        # [cite_start]Admin Seeding Logic [cite: 77]
        # Check if an admin already exists to prevent duplicates
        admin_user = User.query.filter_by(role='admin').first()
        
        if not admin_user:
            hashed_password = generate_password_hash('admin123')
            new_admin = User(
                email='admin@hospital.com',
                password=hashed_password,
                role='admin',
                is_active=True
            )
            db.session.add(new_admin)
            db.session.commit()
            print("Admin user seeded successfully.")

    return app