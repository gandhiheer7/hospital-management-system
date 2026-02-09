import json
from flask import Blueprint, request, jsonify, session
from ..models import db, Doctor, Appointment, Treatment, Patient
from .decorators import doctor_required

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard', methods=['GET'])
@doctor_required
def dashboard():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    
    # 1. Upcoming Appointments (Status = 'Booked')
    upcoming_objs = Appointment.query.filter_by(doctor_id=doctor.id, status='Booked').all()
    upcoming_data = [{
        'id': a.id, 
        'patient_name': a.patient.name, 
        'date': a.date.isoformat(),
        'time_slot': a.time_slot, 
        'status': a.status
    } for a in upcoming_objs]

    # 2. Assigned Patients (Unique patients who have COMPLETED appointments with this doctor)
    completed_apts = Appointment.query.filter_by(doctor_id=doctor.id, status='Completed').all()
    
    # Use a dictionary to filter unique patients
    patients_map = {}
    for apt in completed_apts:
        if apt.patient_id not in patients_map:
            patients_map[apt.patient_id] = {
                'patient_id': apt.patient.id,
                'patient_name': apt.patient.name,
                'email': apt.patient.user.email,
                'contact': apt.patient.contact_info,
                'last_visit': apt.date.isoformat()
            }
    
    assigned_patients_data = list(patients_map.values())

    return jsonify({
        'doctor_name': doctor.name, 
        'upcoming_appointments': upcoming_data, 
        'assigned_patients': assigned_patients_data
    }), 200

@doctor_bp.route('/patient/<int:patient_id>/history', methods=['GET'])
@doctor_required
def get_patient_history(patient_id):
    """View past treatments of a specific patient"""
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    history = Appointment.query.filter_by(patient_id=patient_id, status='Completed').all()
    
    output = []
    for apt in history:
        if apt.treatment:
            output.append({
                'date': apt.date.isoformat(),
                'doctor_name': apt.doctor.name,
                'diagnosis': apt.treatment.diagnosis,
                'prescription': apt.treatment.prescription,
                'notes': apt.treatment.notes
            })
            
    return jsonify({'patient_name': patient.name, 'history': output}), 200

@doctor_bp.route('/availability', methods=['PUT'])
@doctor_required
def update_availability():
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    doctor.availability_schedule = json.dumps(request.json.get('schedule'))
    db.session.commit()
    return jsonify({'message': 'Availability updated'}), 200

@doctor_bp.route('/appointment/<int:id>/complete', methods=['POST'])
@doctor_required
def complete(id):
    user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=user_id).first()
    appt = Appointment.query.filter_by(id=id, doctor_id=doctor.id).first()
    
    if not appt: return jsonify({'message': 'Not found'}), 404
    
    data = request.get_json()
    treatment = Treatment(appointment_id=appt.id, diagnosis=data['diagnosis'], 
                          prescription=data['prescription'], notes=data.get('notes'))
    db.session.add(treatment)
    appt.status = 'Completed'
    db.session.commit()
    return jsonify({'message': 'Completed'}), 200