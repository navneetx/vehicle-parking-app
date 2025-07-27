from app import create_app
from models import User, db
from werkzeug.security import generate_password_hash

# The password we want to set
NEW_PASSWORD = 'admin-password123'

app = create_app()

with app.app_context():
    # Find the admin user
    admin = User.query.filter_by(role='admin').first()

    if admin:
        print("Found admin user. Resetting password...")
        # Set the password to a new, correct hash
        admin.password = generate_password_hash(NEW_PASSWORD)
        db.session.commit()
        print(f"Admin password has been successfully reset to: {NEW_PASSWORD}")
    else:
        print("Admin user not found.")