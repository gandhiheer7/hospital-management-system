from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from ..models import db, User, Doctor, Patient, Appointment, Department
from .decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    """
    Returns system statistics for the Admin Dashboard.
    """
    doctor_count = Doctor.query.count()
    patient_count = Patient.query.count()
    appointment_count = Appointment.query.count()
    
    return jsonify({
        'stats': {
            'doctors': doctor_count,
            'patients': patient_count,
            'appointments': appointment_count
        }
    }), 200

@admin_bp.route('/doctors', methods=['GET'])
@admin_required
def get_all_doctors():
    """
    List all registered doctors.
    """
    doctors = Doctor.query.all()
    output = []
    for doc in doctors:
        output.append({
            'id': doc.id,
            'name': doc.name,
            'email': doc.user.email,
            'specialization': doc.department.name if doc.department else 'N/A',
            'is_approved': doc.is_approved,
            'active': doc.user.is_active
        })
    return jsonify(output), 200

@admin_bp.route('/doctors', methods=['POST'])
@admin_required
def add_doctor():
    """
    Creates a new Doctor.
    Steps:
    1. Create a User entity (Role='doctor')
    2. Create a Doctor entity linked to the User
    """
    data = request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    specialization_id = data.get('specialization_id')

    if not all([name, email, password, specialization_id]):
        return jsonify({'message': 'All fields are required'}), 400

    # Check if email exists
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 409

    # Verify department exists
    department = Department.query.get(specialization_id)
    if not department:
        return jsonify({'message': 'Invalid Specialization ID'}), 400

    try:
        # 1. Create User
        hashed_pw = generate_password_hash(password)
        new_user = User(
            email=email,
            password=hashed_pw,
            role='doctor',
            is_active=True
        )
        db.session.add(new_user)
        db.session.flush() # Flush to generate user.id

        # 2. Create Doctor Profile
        new_doctor = Doctor(
            user_id=new_user.id,
            name=name,
            specialization_id=specialization_id,
            is_approved=True # Auto-approve created doctors
        )
        db.session.add(new_doctor)
        db.session.commit()

        return jsonify({'message': 'Doctor added successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error adding doctor: {str(e)}'}), 500

@admin_bp.route('/doctors/<int:doctor_id>/status', methods=['PUT'])
@admin_required
def update_doctor_status(doctor_id):
    """
    Approve or Block a doctor.
    Input: {'is_approved': boolean}
    """
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'message': 'Doctor not found'}), 404

    data = request.get_json()
    is_approved = data.get('is_approved')

    if is_approved is None:
        return jsonify({'message': 'is_approved status required'}), 400

    try:
        doctor.is_approved = is_approved
        # Sync with User active status if needed, or keep separate
        doctor.user.is_active = is_approved 
        db.session.commit()
        status_msg = "approved" if is_approved else "blocked"
        return jsonify({'message': f'Doctor {status_msg} successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating status: {str(e)}'}), 500

@admin_bp.route('/patients/search', methods=['GET'])
@admin_required
def search_patients():
    """
    Search patients by name or contact info.
    Query Param: ?q=name_or_contact
    """
    query_str = request.args.get('q', '')
    if not query_str:
        return jsonify({'message': 'Query parameter q is required'}), 400

    # Search Case-Insensitive
    patients = Patient.query.filter(
        (Patient.name.ilike(f'%{query_str}%')) | 
        (Patient.contact_info.ilike(f'%{query_str}%'))
    ).all()

    output = [{
        'id': p.id,
        'name': p.name,
        'email': p.user.email,
        'contact': p.contact_info,
        'is_blocked': p.is_blocked
    } for p in patients]

    return jsonify(output), 200

@admin_bp.route('/patients/<int:patient_id>/block', methods=['PUT'])
@admin_required
def block_patient(patient_id):
    """
    Block or Unblock a patient.
    Input: {'is_blocked': boolean}
    """
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    data = request.get_json()
    is_blocked = data.get('is_blocked')

    if is_blocked is None:
        return jsonify({'message': 'is_blocked status required'}), 400

    try:
        patient.is_blocked = is_blocked
        # Optionally deactivate the user login
        patient.user.is_active = not is_blocked
        db.session.commit()
        status_msg = "blocked" if is_blocked else "unblocked"
        return jsonify({'message': f'Patient {status_msg} successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating patient: {str(e)}'}), 500

@admin_bp.route('/appointments', methods=['GET'])
@admin_required
def view_all_appointments():
    """
    View all appointments in the system.
    """
    appointments = Appointment.query.order_by(Appointment.date.desc()).all()
    
    output = [{
        'id': apt.id,
        'patient_name': apt.patient.name,
        'doctor_name': apt.doctor.name,
        'date': apt.date.isoformat(),
        'time_slot': apt.time_slot,
        'status': apt.status
    } for apt in appointments]

    return jsonify(output), 200