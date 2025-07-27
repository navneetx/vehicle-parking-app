from flask import Flask
from extensions import db, jwt, celery, mail

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
    app.config['MAIL_USERNAME'] = None
    app.config['MAIL_PASSWORD'] = None
    app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@parkingapp.com'

    # --- INITIALIZE EXTENSIONS ---
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    # --- CELERY CONFIGURATION ---
    # The schedule is now defined in extensions.py, so we only update the context here
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

    @app.route('/hello')
    def hello():
        return "Hello, World!"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)