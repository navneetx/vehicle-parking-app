from flask import request, jsonify, Blueprint
from models import User
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# This Blueprint handles all authentication-related routes.
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registers a new user."""
    data = request.get_json()

    # Prevent duplicate usernames.
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 409

    # Hash the password for security before storing it.
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password, role='user')
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Logs in a user or admin and returns a JWT access token."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    # Verify the user exists and the password is correct.
    if not user or not check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Create and return an access token for the authenticated user.
    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token)

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Returns the profile information (role) for the currently logged-in user."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if user:
        return jsonify(username=user.username, role=user.role)
    
    return jsonify({"message": "User not found"}), 404