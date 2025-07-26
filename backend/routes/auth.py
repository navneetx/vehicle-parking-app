from flask import request, jsonify, Blueprint
from models import User
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from decorators import admin_required
from flask_jwt_extended import decode_token


# Create a Blueprint to organize our routes
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 409

    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password, role='user')
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# --- NEW LOGIN ROUTE ---
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 1. Find the user by their username
    user = User.query.filter_by(username=username).first()

    # 2. Check if user exists and if the password is correct
    # `check_password_hash` compares the provided password with the stored hash
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401 # Unauthorized

    # 3. Create a JWT access token if credentials are valid
    access_token = create_access_token(identity=str(user.id))
    
    # 4. Return the token
    return jsonify(access_token=access_token)

# --- NEW ADMIN-ONLY TEST ROUTE ---
@auth_bp.route('/admin/test', methods=['GET'])
@jwt_required()
@admin_required()
def admin_test():
    return jsonify(message="Welcome, Admin!")

# --- NEW DEBUG ROUTE ---
@auth_bp.route('/crypto-test')
def crypto_test():
    try:
        # 1. Create a token for the admin user (id=1)
        test_token = create_access_token(identity=str(1))
        print(f"\nGenerated Token: {test_token}\n")

        # 2. Immediately try to decode it with the same configuration
        decoded = decode_token(test_token)
        print(f"Successfully Decoded: {decoded}\n")
        
        return jsonify(
            message="Crypto self-test PASSED!",
            token=test_token
        ), 200
    except Exception as e:
        # If this fails, there's a deep issue with the crypto library
        print(f"\nCrypto Test FAILED: {e}\n")
        return jsonify(message=f"Crypto self-test FAILED: {str(e)}"), 500