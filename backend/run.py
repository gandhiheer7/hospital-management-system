from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'dev-secret-key'

    # ✅ Enable CORS for Vite frontend
    CORS(
        app,
        resources={r"/*": {"origins": "http://localhost:5173"}},
        supports_credentials=True
    )

    # 🔗 REGISTER BLUEPRINTS
    from app.api.auth import auth_bp
    app.register_blueprint(auth_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
