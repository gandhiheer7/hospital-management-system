import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from app import create_app

load_dotenv()  # Load variables from .env

app = create_app()

# Expose celery for the worker: `celery -A run.celery_app worker`
celery_app = app.extensions["celery"]

# Enable CORS — origin now configurable via environment variable
CORS(app, resources={r"/*": {"origins": os.environ.get("FRONTEND_URL", "http://localhost:5173")}}, supports_credentials=True)

if __name__ == "__main__":
    app.run(debug=True)