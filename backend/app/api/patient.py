import json
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from ..models import db, Patient, Doctor, Department, Appointment
from .decorators import patient_required

patient_bp = Blueprint('patient', __name__)

@patient_bp.route('/doctors', methods=['GET'])
@patient_required
def get_doctors():
    """
    List doctors with their specialization and availability.
    Optional query param: ?specialization_id=X
    """
    spec_id = request.args.get('specialization_id')
    
    query = Doctor.query.filter_by(is_approved=True)
    if spec_id:
        query = query.filter_by(specialization_id=spec_id)
    
    doctors = query.all()
    
    doctor_list = []
    for doc in doctors:
        # Parse availability JSON string back to object for frontend
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
    """
    Books an appointment. 
    CRITICAL: Prevents double booking for the same Doctor + Date + Time.
    """
    current_user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=current_user_id).first()

    if not patient:
        return jsonify({'message': 'Patient profile not found'}), 404

    data = request.get_json()
    doctor_id = data.get('doctor_id')
    date_str = data.get('date') # YYYY-MM-DD
    time_slot = data.get('time_slot')

    if not all([doctor_id, date_str, time_slot]):
        return jsonify({'message': 'Doctor, Date, and Time Slot are required'}), 400

    try:
        appt_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # DOUBLE BOOKING CHECK
    # Check if ANY appointment exists for this doctor at this time that is NOT Cancelled
    existing_appt = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == appt_date,
        Appointment.time_slot == time_slot,
        Appointment.status != 'Cancelled'
    ).first()

    if existing_appt:
        return jsonify({'message': 'This time slot is already booked'}), 409

    try:
        new_appt = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            date=appt_date,
            time_slot=time_slot,
            status='Booked'
        )
        db.session.add(new_appt)
        db.session.commit()
        return jsonify({'message': 'Appointment booked successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Booking failed: {str(e)}'}), 500

@patient_bp.route('/appointment/<int:appt_id>/cancel', methods=['POST'])
@patient_required
def cancel_appointment(appt_id):
    """
    Cancels a specific appointment.
    """
    current_user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=current_user_id).first()

    appointment = Appointment.query.filter_by(id=appt_id, patient_id=patient.id).first()

    if not appointment:
        return jsonify({'message': 'Appointment not found or unauthorized'}), 404

    if appointment.status == 'Completed':
        return jsonify({'message': 'Cannot cancel a completed appointment'}), 400
    
    if appointment.status == 'Cancelled':
        return jsonify({'message': 'Appointment is already cancelled'}), 400

    try:
        appointment.status = 'Cancelled'
        db.session.commit()
        return jsonify({'message': 'Appointment cancelled successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Cancellation failed: {str(e)}'}), 500