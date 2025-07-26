# In backend/routes/admin_routes.py

from flask import jsonify, Blueprint
from extensions import db
from models import User, ParkingRecord, ParkingSpot, ParkingLot
from flask_jwt_extended import jwt_required
from decorators import admin_required
from sqlalchemy import func

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

# This is the new route for getting all reservations
@admin_bp.route('/reservations', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_reservations():
    reservations = ParkingRecord.query.order_by(ParkingRecord.parking_timestamp.desc()).all()
    output = []
    for record in reservations:
        user = User.query.get(record.user_id)
        spot = ParkingSpot.query.get(record.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        record_data = {
            'reservation_id': record.id,
            'username': user.username,
            'lot_name': lot.prime_location_name,
            'spot_number': spot.spot_number,
            'parking_time': record.parking_timestamp.isoformat() if record.parking_timestamp else None,
            'leaving_time': record.leaving_timestamp.isoformat() if record.leaving_timestamp else None,
            'cost': record.parking_cost
        }
        output.append(record_data)
    
    return jsonify({'reservations': output})

@admin_bp.route('/revenue', methods=['GET'])
@jwt_required()
@admin_required()
def get_revenue_summary():
    """
    Calculates the total revenue for each parking lot by joining the
    ParkingLot, ParkingSpot, and ParkingRecord tables and summing the costs.
    """
    revenue_data = db.session.query(
        ParkingLot.prime_location_name,
        func.sum(ParkingRecord.parking_cost).label('total_revenue')
    ).join(ParkingSpot, ParkingLot.id == ParkingSpot.lot_id)\
     .join(ParkingRecord, ParkingSpot.id == ParkingRecord.spot_id)\
     .filter(ParkingRecord.parking_cost.isnot(None))\
     .group_by(ParkingLot.prime_location_name)\
     .all()

    output = []
    for lot_name, total_revenue in revenue_data:
        output.append({
            'lot_name': lot_name,
            'total_revenue': round(total_revenue, 2) if total_revenue else 0
        })

    return jsonify({'revenue_summary': output})