from functools import wraps
from flask import session, jsonify

def login_required(f):
    """
    Decorator to ensure the user is logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to ensure the logged-in user is an Admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Authentication required'}), 401
        
        if session.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    """
    Decorator to ensure the logged-in user is a Doctor.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Authentication required'}), 401
            
        if session.get('role') != 'doctor':
            return jsonify({'message': 'Doctor access required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def patient_required(f):
    """
    Decorator to ensure the logged-in user is a Patient.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'message': 'Authentication required'}), 401
            
        if session.get('role') != 'patient':
            return jsonify({'message': 'Patient access required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function