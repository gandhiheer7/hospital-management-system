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
    
    # Updated: Include patient_id in response
    upcoming = Appointment.query.filter_by(doctor_id=doctor.id, status='Booked').all()
    output = [{
        'id': a.id, 
        'patient_id': a.patient_id,  # <--- Added
        'patient_name': a.patient.name, 
        'date': a.date.isoformat(),
        'time_slot': a.time_slot, 
        'status': a.status
    } for a in upcoming]
    
    return jsonify({'doctor_name': doctor.name, 'appointments': output}), 200

# --- NEW FEATURE: View Patient History ---
@doctor_bp.route('/patient/<int:patient_id>/history', methods=['GET'])
@doctor_required
def get_patient_history(patient_id):
    """View past treatments of a specific patient"""
    # Verify patient exists
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'message': 'Patient not found'}), 404

    # Fetch all completed appointments for this patient (from ANY doctor)
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
# -----------------------------------------

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