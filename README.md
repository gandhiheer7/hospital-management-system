# Hospital Management System

A role-based hospital management platform for Admins, Doctors, and Patients — built as a 
full-stack application handling appointment scheduling, treatment records, and automated 
patient communication.

## Tech Stack
**Frontend:** Vue.js 3, Bootstrap  
**Backend:** Flask, SQLAlchemy, Flask-Session  
**Async/Scheduled Jobs:** Celery + Redis  
**Database:** SQLite

## Features

### Admin
- Dashboard showing total doctors, patients, and appointments
- Add, update, and blacklist doctor/patient profiles
- Search patients or doctors by name/specialization
- View and manage all appointments

### Doctor
- View upcoming appointments (daily/weekly)
- Mark appointments as completed and log diagnosis, prescriptions, and notes
- Provide 7-day availability windows
- View and update patient treatment history

### Patient
- Register, log in, and manage their profile
- Search doctors by specialization and availability
- Book, reschedule, or cancel appointments
- View appointment and treatment history
- Export their full treatment history as a CSV (triggered asynchronously via Celery)

### Background Jobs (Celery + Redis)
- **Daily reminders** — checks for scheduled visits each morning and sends a reminder to the 
  patient
- **Monthly activity reports** — generated on the 1st of each month per doctor, summarizing 
  that month's appointments, diagnoses, and treatments, sent via email
- **CSV export** — user-triggered async job that compiles a patient's full treatment history 
  and notifies them once ready

## Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Redis + Celery (required for reminders, reports, and CSV export)
```bash
# Start Redis (must be running separately — e.g. via redis-server or a local Redis install)
redis-server

# Start the Celery worker
celery -A run.celery_app worker

# Start Celery Beat (for scheduled jobs — daily reminders, monthly reports)
celery -A run.celery_app beat
```

## Roles
Only one Admin exists, created programmatically at database setup — there is no public admin 
registration. Doctors are added by the Admin. Patients self-register.