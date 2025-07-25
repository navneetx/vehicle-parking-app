from app import app, db
from models import User
from werkzeug.security import generate_password_hash

# This is the password we'll give our admin
ADMIN_PASSWORD = 'admin-password123'

# Create an application context
with app.app_context():
    # Create the database tables
    db.create_all()

    # Check if the admin user already exists
    if not User.query.filter_by(role='admin').first():
        print("Admin not found, creating one...")

        # Hash the password for security
        hashed_password = generate_password_hash(ADMIN_PASSWORD)

        # Create the admin user object
        admin = User(
            username='admin', 
            password=hashed_password, 
            role='admin'
        )

        # Add the new admin user to the session and commit it
        db.session.add(admin)
        db.session.commit()

        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")