from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Get the user's ID from the access token
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            # Check if the user exists and their role is 'admin'
            if user and user.role == 'admin':
                return fn(*args, **kwargs)
            else:
                return jsonify(message="Admins only! Access forbidden."), 403
        return decorator
    return wrapper