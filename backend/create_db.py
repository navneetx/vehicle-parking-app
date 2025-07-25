# In backend/create_db.py

from app import create_app, db
from models import User
from werkzeug.security import generate_password_hash

# Create an app instance using the factory
app = create_app()

# Use the app context to perform database operations
with app.app_context():
    # Create the database tables
    db.create_all()

    # The rest of the script is the same...
    if not User.query.filter_by(role='admin').first():
        print("Admin user not found, creating one...")
        hashed_password = generate_password_hash('admin-password123')
        admin = User(username='admin', password=hashed_password, role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")