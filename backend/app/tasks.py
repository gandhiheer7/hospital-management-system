import csv
import io
from datetime import datetime, timedelta
from celery import shared_task
from .models import db, Appointment, Doctor, Treatment, Patient, User

@shared_task
def send_daily_reminders():
    """
    Scheduled Job: Checks for appointments scheduled for today and logs a reminder.
    Intended to run every morning (configured in celery beat schedule).
    """
    today = datetime.today().date()
    
    # Query booked appointments for today
    appointments = Appointment.query.filter_by(
        date=today, 
        status='Booked'
    ).all()
    
    print(f"--- [Job] Starting Daily Reminders for {today} ---")
    
    if not appointments:
        print("No appointments scheduled for today.")
        return "No appointments"

    count = 0
    for apt in appointments:
        # Simulate sending email/SMS
        msg = (f"Reminder: Dear {apt.patient.name}, you have an appointment "
               f"with Dr. {apt.doctor.name} today at {apt.time_slot}.")
        print(f"Sending ALERT to {apt.patient.contact_info}: {msg}")
        count += 1
        
    print(f"--- [Job] Finished. Sent {count} reminders. ---")
    return f"Sent {count} reminders"

@shared_task
def generate_monthly_reports():
    """
    Scheduled Job: Generates activity report for the previous month for every doctor.
    Intended to run on the 1st of every month.
    """
    today = datetime.today()
    # Calculate first and last day of previous month
    first_day_current_month = today.replace(day=1)
    last_day_prev_month = first_day_current_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)
    
    print(f"--- [Job] Generating Monthly Reports ({first_day_prev_month.date()} to {last_day_prev_month.date()}) ---")
    
    doctors = Doctor.query.filter_by(is_approved=True).all()
    
    for doc in doctors:
        # Get appointments for this doctor in date range
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doc.id,
            Appointment.date >= first_day_prev_month.date(),
            Appointment.date <= last_day_prev_month.date()
        ).all()
        
        total_visits = len(appointments)
        completed_visits = sum(1 for a in appointments if a.status == 'Completed')
        cancelled_visits = sum(1 for a in appointments if a.status == 'Cancelled')
        
        # In a real app, this would generate an HTML file or PDF
        report_log = (
            f"REPORT FOR DR. {doc.name}\n"
            f"Period: {first_day_prev_month.strftime('%Y-%m')}\n"
            f"Total Appointments: {total_visits}\n"
            f"Completed: {completed_visits}\n"
            f"Cancelled: {cancelled_visits}\n"
        )
        
        # Simulate Emailing
        print(f"Emailing Report to {doc.user.email}...")
        print(report_log)
        print("------------------------------------------------")
        
    return "Monthly reports generated"

@shared_task
def export_patient_history(user_id):
    """
    Async Job: Exports patient treatment history to CSV.
    Triggered by Patient via UI.
    """
    print(f"--- [Job] Starting CSV Export for User ID {user_id} ---")
    
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        print("Error: Patient profile not found.")
        return "Failed: Patient not found"

    # Fetch history: Appointments that are completed and have treatment data
    history = Appointment.query.filter_by(
        patient_id=patient.id, 
        status='Completed'
    ).join(Treatment).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Date', 'Time', 'Doctor', 'Diagnosis', 'Prescription', 'Notes'])
    
    # Rows
    for apt in history:
        treatment = apt.treatment
        writer.writerow([
            apt.date,
            apt.time_slot,
            apt.doctor.name,
            treatment.diagnosis,
            treatment.prescription,
            treatment.notes
        ])
    
    csv_content = output.getvalue()
    output.close()
    
    # Simulate sending file via email
    # In production: save to file/S3 and send link, or attach to email
    print(f"CSV Generated for {patient.name} ({patient.user.email}).")
    print(f"Sending email with attachment 'history.csv'...")
    
    # Verification log
    print(f"Content Preview:\n{csv_content}")
    
    return "CSV Export Completed"