from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from ..models import db, User, Doctor, Patient, Appointment, Department
from .decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    doctor_count = Doctor.query.count()
    patient_count = Patient.query.count()
    appointment_count = Appointment.query.count()
    return jsonify({'stats': {'doctors': doctor_count, 'patients': patient_count, 'appointments': appointment_count}}), 200

@admin_bp.route('/departments', methods=['GET'])
@admin_required
def get_departments():
    departments = Department.query.all()
    output = [{'id': d.id, 'name': d.name} for d in departments]
    return jsonify(output), 200

@admin_bp.route('/doctors', methods=['GET'])
@admin_required
def get_all_doctors():
    doctors = Doctor.query.all()
    output = []
    for doc in doctors:
        output.append({
            'id': doc.id,
            'name': doc.name,
            'email': doc.user.email,
            'specialization_id': doc.specialization_id,
            'specialization': doc.department.name if doc.department else 'N/A',
            'is_approved': doc.is_approved,
            'active': doc.user.is_active
        })
    return jsonify(output), 200

@admin_bp.route('/doctors', methods=['POST'])
@admin_required
def add_doctor():
    data = request.get_json()
    if not all([data.get('name'), data.get('email'), data.get('password'), data.get('specialization_id')]):
        return jsonify({'message': 'All fields required'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 409

    try:
        hashed_pw = generate_password_hash(data['password'])
        new_user = User(email=data['email'], password=hashed_pw, role='doctor', is_active=True)
        db.session.add(new_user)
        db.session.flush()

        new_doctor = Doctor(user_id=new_user.id, name=data['name'], specialization_id=data['specialization_id'], is_approved=True)
        db.session.add(new_doctor)
        db.session.commit()
        return jsonify({'message': 'Doctor added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@admin_required
def update_doctor(doctor_id):
    """Update Doctor Details (Name, Specialization)"""
    doctor = Doctor.query.get(doctor_id)
    if not doctor: return jsonify({'message': 'Doctor not found'}), 404
    
    data = request.get_json()
    if 'name' in data: doctor.name = data['name']
    if 'specialization_id' in data: doctor.specialization_id = data['specialization_id']
    
    db.session.commit()
    return jsonify({'message': 'Doctor updated successfully'}), 200

@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@admin_required
def delete_doctor(doctor_id):
    """Hard Delete Doctor"""
    doctor = Doctor.query.get(doctor_id)
    if not doctor: return jsonify({'message': 'Doctor not found'}), 404
    
    # Note: Cascading delete handles the User record if configured, 
    # but manually deleting User is safer for clarity.
    user = doctor.user
    db.session.delete(doctor)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Doctor deleted'}), 200

@admin_bp.route('/doctors/<int:doctor_id>/status', methods=['PUT'])
@admin_required
def update_doctor_status(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor: return jsonify({'message': 'Doctor not found'}), 404
    
    is_approved = request.json.get('is_approved')
    if is_approved is None: return jsonify({'message': 'Status required'}), 400

    doctor.is_approved = is_approved
    doctor.user.is_active = is_approved
    db.session.commit()
    return jsonify({'message': 'Status updated'}), 200

@admin_bp.route('/patients', methods=['GET'])
@admin_required
def get_all_patients():
    patients = Patient.query.all()
    output = [{
        'id': p.id,
        'name': p.name,
        'email': p.user.email,
        'contact_info': p.contact_info,
        'is_blocked': p.is_blocked,
        'appointment_count': len(p.appointments)
    } for p in patients]
    return jsonify(output), 200

@admin_bp.route('/patients/<int:patient_id>/block', methods=['PUT'])
@admin_required
def block_patient(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient: return jsonify({'message': 'Patient not found'}), 404
    
    is_blocked = request.json.get('is_blocked')
    patient.is_blocked = is_blocked
    db.session.commit()
    return jsonify({'message': 'Status updated'}), 200

@admin_bp.route('/appointments', methods=['GET'])
@admin_required
def view_all_appointments():
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