from flask import request, jsonify, Blueprint
from models import User
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token
from decorators import admin_required

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

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # --- START DEBUGGING ---
    print(f"\n--- LOGIN ATTEMPT ---")
    print(f"Attempting login for username: '{username}'")

    user = User.query.filter_by(username=username).first()

    if not user:
        print("Result: User NOT FOUND in database.")
        print("-----------------------\n")
        return jsonify({"message": "Invalid credentials"}), 401

    print(f"Result: User FOUND. User ID: {user.id}, Stored Hash: {user.password[:30]}...")
    
    password_is_correct = check_password_hash(user.password, password)
    
    if not password_is_correct:
        print(f"Password Check Result: FAILED.")
        print("-----------------------\n")
        return jsonify({"message": "Invalid credentials"}), 401

    print("Password Check Result: PASSED.")
    access_token = create_access_token(identity=str(user.id))
    print("Token created successfully.")
    print("-----------------------\n")
    
    return jsonify(access_token=access_token)

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if user:
        return jsonify(username=user.username, role=user.role)
    return jsonify({"message": "User not found"}), 404

@auth_bp.route('/admin/test', methods=['GET'])
@jwt_required()
@admin_required()
def admin_test():
    return jsonify(message="Welcome, Admin!")

@auth_bp.route('/crypto-test')
def crypto_test():
    try:
        test_token = create_access_token(identity=str(1))
        print(f"\nGenerated Token: {test_token}\n")
        decoded = decode_token(test_token)
        print(f"Successfully Decoded: {decoded}\n")
        
        return jsonify(
            message="Crypto self-test PASSED!",
            token=test_token
        ), 200
    except Exception as e:
        print(f"\nCrypto Test FAILED: {e}\n")
        return jsonify(message=f"Crypto self-test FAILED: {str(e)}"), 500