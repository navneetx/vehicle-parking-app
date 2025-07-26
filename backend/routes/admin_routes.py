# In backend/routes/admin_routes.py

from flask import jsonify, Blueprint
from models import User
from flask_jwt_extended import jwt_required
from decorators import admin_required

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_users():
    # Query the database for all users
    users = User.query.all()
    output = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'role': user.role
            # IMPORTANT: We never include the user's password hash in an API response
        }
        output.append(user_data)

    return jsonify({'users': output})