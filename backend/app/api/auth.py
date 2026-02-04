from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from ..models import db, User, Patient

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Logs in a user (Admin, Doctor, or Patient) and sets the session.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    if not user.is_active:
        return jsonify({'message': 'Account is inactive'}), 403

    # Set Session
    session['user_id'] = user.id
    session['role'] = user.role
    session['email'] = user.email

    response_data = {
        'message': 'Login successful',
        'role': user.role,
        'user_id': user.id
    }

    # Include profile ID for specific roles to simplify frontend calls
    if user.role == 'doctor' and user.doctor_profile:
        response_data['profile_id'] = user.doctor_profile.id
    elif user.role == 'patient' and user.patient_profile:
        response_data['profile_id'] = user.patient_profile.id

    return jsonify(response_data), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registers a new Patient. Admin and Doctor registration is blocked.
    """
    data = request.get_json()
    
    # Required fields for User and Patient
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    # Optional/Profile fields
    dob_str = data.get('dob') # Expected format YYYY-MM-DD
    contact_info = data.get('contact_info')
    address = data.get('address')

    if not email or not password or not name:
        return jsonify({'message': 'Email, password, and name are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 409

    try:
        # 1. Create User
        hashed_password = generate_password_hash(password)
        new_user = User(
            email=email,
            password=hashed_password,
            role='patient', # Enforce patient role
            is_active=True
        )
        db.session.add(new_user)
        db.session.flush() # Flush to get new_user.id

        # 2. Create Patient Profile
        dob_date = None
        if dob_str:
            dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date()

        new_patient = Patient(
            user_id=new_user.id,
            name=name,
            dob=dob_date,
            contact_info=contact_info,
            address=address,
            is_blocked=False
        )
        db.session.add(new_patient)
        
        db.session.commit()
        return jsonify({'message': 'Patient registered successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Clears the user session.
    """
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/me', methods=['GET'])
def current_user():
    """
    Helper endpoint to check current session status.
    """
    if 'user_id' not in session:
        return jsonify({'authenticated': False}), 200
        
    return jsonify({
        'authenticated': True,
        'user_id': session['user_id'],
        'role': session['role'],
        'email': session['email']
    }), 200