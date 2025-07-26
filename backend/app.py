# In backend/app.py

from flask import Flask
from extensions import db, jwt  # <-- Import from extensions

def create_app():
    app = Flask(__name__)

    # --- CONFIGURATIONS ---
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Use a very simple key for debugging
    app.config['JWT_SECRET_KEY'] = 'super' # <-- CHANGE THIS LINE

    # Add a print statement to be sure
    print(f"Using Secret Key: {app.config['JWT_SECRET_KEY']}")

    # --- INITIALIZE EXTENSIONS WITH THE APP ---
    db.init_app(app)
    jwt.init_app(app)

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