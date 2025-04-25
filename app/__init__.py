import os
from dotenv import load_dotenv
from flask import Flask
from app.routes.project_routes import project_bp
from app.routes.task_routes import task_bp  
from app.routes.error_routes import error_bp
from app.routes.home_routes import home_bp
from app.routes.auth_routes import auth_bp
from app.routes.focus_session_route import focus_session_bp
from app.infra.db import db 
from .websocket import socketio

load_dotenv()

app = Flask(__name__)

def create_app():
    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    socketio.init_app(app)
    
    app.register_blueprint(project_bp)  
    app.register_blueprint(task_bp)  
    app.register_blueprint(error_bp)
    app.register_blueprint(home_bp)  
    app.register_blueprint(auth_bp)  
    app.register_blueprint(focus_session_bp)

    return app
