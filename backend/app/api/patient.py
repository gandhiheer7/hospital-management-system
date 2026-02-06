import json
from flask import Blueprint, request, jsonify, session
from datetime import datetime, date
from ..models import db, Patient, Doctor, Appointment, Department
from .decorators import patient_required
from ..tasks import export_patient_history
from .. import cache

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/departments', methods=['GET'])
@patient_required
def get_departments():
    departments = Department.query.all()
    output = [{'id': d.id, 'name': d.name} for d in departments]
    return jsonify(output), 200

@patient_bp.route('/doctors', methods=['GET'])
@patient_required
@cache.cached(timeout=60, query_string=True)
def get_doctors():
    spec_id = request.args.get('specialization_id')
    query = Doctor.query.filter_by(is_approved=True)
    if spec_id:
        query = query.filter_by(specialization_id=spec_id)
    
    doctors = query.all()
    doctor_list = []
    for doc in doctors:
        availability = []
        if doc.availability_schedule:
            try:
                availability = json.loads(doc.availability_schedule)
            except:
                availability = []
        doctor_list.append({
            'id': doc.id,
            'name': doc.name,
            'specialization': doc.department.name if doc.department else 'General',
            'availability': availability
        })
    return jsonify(doctor_list), 200

@patient_bp.route('/book', methods=['POST'])
@patient_required
def book_appointment():
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    
    data = request.get_json()
    doctor_id, date_str, time_slot = data.get('doctor_id'), data.get('date'), data.get('time_slot')

    if not all([doctor_id, date_str, time_slot]):
        return jsonify({'message': 'Missing fields'}), 400

    try:
        appt_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format'}), 400

    existing_appt = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == appt_date,
        Appointment.time_slot == time_slot,
        Appointment.status != 'Cancelled'
    ).first()

    if existing_appt:
        return jsonify({'message': 'Slot already booked'}), 409

    new_appt = Appointment(patient_id=patient.id, doctor_id=doctor_id, date=appt_date, time_slot=time_slot)
    db.session.add(new_appt)
    db.session.commit()
    return jsonify({'message': 'Booked successfully'}), 201

# --- NEW FEATURE: Cancel Appointment ---
@patient_bp.route('/appointments/<int:id>/cancel', methods=['PUT'])
@patient_required
def cancel_appointment(id):
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    
    appt = Appointment.query.filter_by(id=id, patient_id=patient.id).first()
    
    if not appt:
        return jsonify({'message': 'Appointment not found'}), 404
        
    if appt.status == 'Completed':
        return jsonify({'message': 'Cannot cancel completed appointments'}), 400
        
    appt.status = 'Cancelled'
    db.session.commit()
    return jsonify({'message': 'Appointment cancelled'}), 200
# ---------------------------------------

@patient_bp.route('/dashboard', methods=['GET'])
@patient_required
def dashboard():
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    
    upcoming = Appointment.query.filter_by(patient_id=patient.id).filter(Appointment.status != 'Cancelled').all()
    output = [{
        'id': a.id, 'doctor_name': a.doctor.name, 'date': a.date.isoformat(), 
        'time_slot': a.time_slot, 'status': a.status
    } for a in upcoming]
    
    return jsonify({'patient_name': patient.name, 'upcoming_appointments': output}), 200

@patient_bp.route('/history', methods=['GET'])
@patient_required
def history():
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    
    history = Appointment.query.filter_by(patient_id=patient.id, status='Completed').all()
    output = []
    for apt in history:
        if apt.treatment:
            output.append({
                'id': apt.id,
                'date': apt.date.isoformat(),
                'doctor_name': apt.doctor.name,
                'diagnosis': apt.treatment.diagnosis,
                'prescription': apt.treatment.prescription,
                'notes': apt.treatment.notes
            })
    return jsonify(output), 200

@patient_bp.route('/export', methods=['POST'])
@patient_required
def export_data():
    user_id = session.get('user_id')
    export_patient_history.delay(user_id)
    return jsonify({'message': 'Export started'}), 202

@patient_bp.route('/profile', methods=['PUT'])
@patient_required
def update_profile():
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    
    data = request.get_json()
    if 'name' in data: patient.name = data['name']
    if 'contact_info' in data: patient.contact_info = data['contact_info']
    if 'address' in data: patient.address = data['address']
    
    db.session.commit()
    return jsonify({'message': 'Profile updated'}), 200