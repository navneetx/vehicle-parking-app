from flask import request, jsonify, Blueprint
from models import User
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

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
    access_token = create_access_token(identity=user.id)
    
    # 4. Return the token
    return jsonify(access_token=access_token)