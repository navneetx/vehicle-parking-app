from flask import Flask
from flask_cors import CORS
from extensions import db, jwt, mail, celery

def create_app():
    app = Flask(__name__)
    CORS(app)

    # --- CONFIGURATIONS ---
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'super-secret'

    # --- MAILHOG CONFIGURATION ---
    app.config['MAIL_SERVER'] = 'localhost'
    app.config['MAIL_PORT'] = 1025
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@parkingapp.com'

    # --- INITIALIZE EXTENSIONS ---
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Update celery with the app config and set the context-aware task class
    celery.conf.update(app.config)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    
    # --- BLUEPRINT REGISTRATION ---
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from routes.lot_routes import lot_bp
    app.register_blueprint(lot_bp, url_prefix='/api')
    from routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    from routes.user_routes import user_bp
    app.register_blueprint(user_bp, url_prefix='/api/user')

    return app

# This block was missing. It's the "start button" for the server.
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)