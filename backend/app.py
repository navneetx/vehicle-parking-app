from flask import Flask
from flask_cors import CORS
from extensions import db, jwt, mail, celery

# -----------------
# Application Factory
# -----------------
# This function creates and configures the main Flask application.
# Using a factory helps avoid circular import errors and keeps the setup organized.
def create_app():
    app = Flask(__name__)
    CORS(app) # Enables Cross-Origin Resource Sharing for the frontend

    # --- CONFIGURATIONS ---
    # Loads all application settings from a single mapping.
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='sqlite:///database.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY='super-secret',
        
        # Mailhog Configuration (for local email testing)
        MAIL_SERVER='localhost',
        MAIL_PORT=1025,
        MAIL_USE_TLS=False,
        MAIL_DEFAULT_SENDER='no-reply@parkingapp.com',
        
        # Celery Configuration (uses Redis as a broker and backend)
        broker_url='redis://localhost:6379/0',
        result_backend='redis://localhost:6379/0'
    )

    # --- INITIALIZE EXTENSIONS ---
    # Connects the extension objects (like db, jwt) to the Flask app.
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    celery.conf.update(app.config)

    # --- CELERY CONTEXT ---
    # This ensures that Celery tasks run with access to the Flask app's
    # context, allowing them to use the database and other extensions.
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    
    # --- BLUEPRINT REGISTRATION ---
    # Organizes the application's routes into logical groups.
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from routes.lot_routes import lot_bp
    app.register_blueprint(lot_bp, url_prefix='/api')
    
    from routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    from routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)