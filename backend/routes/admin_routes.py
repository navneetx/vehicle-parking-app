from flask import jsonify, Blueprint
from models import User, ParkingRecord, ParkingSpot, ParkingLot
from extensions import db, celery
from flask_jwt_extended import jwt_required
from decorators import admin_required
from sqlalchemy import func

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'role': user.role
        }
        output.append(user_data)
    
    return jsonify({'users': output})

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

# Temporary test route for Celery
@admin_bp.route('/test-task', methods=['GET'])
def test_task():
    # Send the task by its string name
    task = celery.send_task('tasks.add_together', args=[5, 10])
    return jsonify({"message": "Task sent!", "task_id": task.id})