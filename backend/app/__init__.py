import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask_socketio import SocketIO
from app.models import db

load_dotenv()

# Instantiate the SocketIO control matrix globally with production configurations
socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    CORS(app)

    secret_key = os.environ.get('FLASK_SECRET_KEY') or os.environ.get('SECRET_KEY') or 'dev-secret-change-me'
    app.config['SECRET_KEY'] = secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///storage.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    # Initialize socket context engine directly into our running environment
    socketio.init_app(app)

    from app.app.routes.auth import auth_bp
    from app.app.routes.ai_core import ai_bp
    from app.app.routes.telemetry_sockets import init_telemetry_sockets

    app.register_blueprint(auth_bp)
    app.register_blueprint(ai_bp)
    
    # Initialize socket routes
    init_telemetry_sockets(socketio)

    @app.route('/')
    def root_gateway():
        return redirect(url_for('auth.login_view'))

    with app.app_context():
        db.create_all()

    return app

app = create_app()