import json
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from ..models import db, Doctor, Appointment, Treatment, Patient
from .decorators import doctor_required

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/dashboard', methods=['GET'])
@doctor_required
def dashboard():
    """
    Fetches upcoming appointments and assigned patients for the logged-in doctor.
    """
    current_user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404

    # Fetch appointments (Booked)
    upcoming_appts = Appointment.query.filter_by(
        doctor_id=doctor.id, 
        status='Booked'
    ).order_by(Appointment.date, Appointment.time_slot).all()

    appointments_data = [{
        'id': apt.id,
        'patient_name': apt.patient.name,
        'date': apt.date.isoformat(),
        'time_slot': apt.time_slot,
        'status': apt.status
    } for apt in upcoming_appts]

    return jsonify({
        'doctor_name': doctor.name,
        'appointments': appointments_data
    }), 200

@doctor_bp.route('/availability', methods=['PUT'])
@doctor_required
def update_availability():
    """
    Updates the doctor's 7-day availability schedule.
    Expected Input: JSON string or object representing schedule.
    """
    current_user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=current_user_id).first()
    
    if not doctor:
        return jsonify({'message': 'Doctor profile not found'}), 404

    data = request.get_json()
    schedule = data.get('schedule') # Expecting a dictionary/list structure

    if not schedule:
        return jsonify({'message': 'Schedule data is required'}), 400

    try:
        # Store as JSON string in the Text column
        doctor.availability_schedule = json.dumps(schedule)
        db.session.commit()
        return jsonify({'message': 'Availability updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating availability: {str(e)}'}), 500

@doctor_bp.route('/appointment/<int:appt_id>/complete', methods=['POST'])
@doctor_required
def complete_visit(appt_id):
    """
    Marks an appointment as Completed and adds a Treatment record.
    """
    current_user_id = session.get('user_id')
    doctor = Doctor.query.filter_by(user_id=current_user_id).first()

    appointment = Appointment.query.filter_by(id=appt_id, doctor_id=doctor.id).first()

    if not appointment:
        return jsonify({'message': 'Appointment not found or unauthorized'}), 404

    if appointment.status != 'Booked':
        return jsonify({'message': 'Only booked appointments can be completed'}), 400

    data = request.get_json()
    diagnosis = data.get('diagnosis')
    prescription = data.get('prescription')
    notes = data.get('notes', '')

    if not diagnosis or not prescription:
        return jsonify({'message': 'Diagnosis and Prescription are required'}), 400

    try:
        # 1. Create Treatment
        treatment = Treatment(
            appointment_id=appointment.id,
            diagnosis=diagnosis,
            prescription=prescription,
            notes=notes
        )
        db.session.add(treatment)

        # 2. Update Status
        appointment.status = 'Completed'
        
        db.session.commit()
        return jsonify({'message': 'Visit marked as completed and treatment recorded'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error completing visit: {str(e)}'}), 500