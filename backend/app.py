# In backend/app.py

from flask import Flask
from extensions import db, jwt  # <-- Import from extensions

def create_app():
    app = Flask(__name__)

    # --- CONFIGURATIONS ---
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your-super-secret-key-change-this'

    # --- INITIALIZE EXTENSIONS WITH THE APP ---
    db.init_app(app)
    jwt.init_app(app)

    # --- BLUEPRINT REGISTRATION ---
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.route('/hello')
    def hello():
        return "Hello, World!"

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)