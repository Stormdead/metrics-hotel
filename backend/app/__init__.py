from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from config import config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"],
                                     "methods": ["GET", "POST", "PUT", "DELETE"],
                                     "allow_headers": ["Content-Type", "Authorization"]}})
    
    # Registrar blueprints (por ahora comentados hasta que los creemos)
    from app.routes import auth, users, rooms, bookings, metrics
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(rooms.bp)
    app.register_blueprint(bookings.bp)
    app.register_blueprint(metrics.bp)
    
    return app