from flask import request, jsonify, Blueprint
from models import ParkingLot, ParkingSpot, ParkingRecord, User
from extensions import db, redis_client
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import datetime

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/lots', methods=['GET'])
@jwt_required()
def get_available_lots():
    cache_key = "all_lots"
    cached_lots = redis_client.get(cache_key)

    if cached_lots:
        print("Serving from cache")
        return jsonify({'lots': json.loads(cached_lots)})

    print("Serving from database")
    lots = ParkingLot.query.all()
    output = []
    for lot in lots:
        lot_data = {
            'id': lot.id,
            'prime_location_name': lot.prime_location_name,
            'price': lot.price,
            'address': lot.address,
            'pin_code': lot.pin_code,
            'number_of_spots': lot.number_of_spots
        }
        output.append(lot_data)

    redis_client.setex(cache_key, 3600, json.dumps(output))

    return jsonify({'lots': output})


@user_bp.route('/reservations', methods=['GET', 'POST'])
@jwt_required()
def handle_reservations():
    user_id = get_jwt_identity()

    if request.method == 'POST':
        data = request.get_json()
        lot_id = data.get('lot_id')

        active_reservation = ParkingRecord.query.filter_by(user_id=user_id, leaving_timestamp=None).first()
        if active_reservation:
            return jsonify({"message": "You already have an active parking reservation."}), 409

        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='available').first()
        if not available_spot:
            return jsonify({"message": "No available spots in this parking lot."}), 404

        available_spot.status = 'occupied'
        new_reservation = ParkingRecord(user_id=user_id, spot_id=available_spot.id)
        db.session.add(new_reservation)
        db.session.commit()

        # --- FIX: Clear the cache after a booking ---
        redis_client.delete("all_lots")

        return jsonify({
            "message": "Spot booked successfully!",
            "lot_id": available_spot.lot_id,
            "spot_number": available_spot.spot_number
        }), 201

    elif request.method == 'GET':
        # ... (this part is unchanged)
        reservations = ParkingRecord.query.filter_by(user_id=user_id).order_by(ParkingRecord.parking_timestamp.desc()).all()
        output = []
        for record in reservations:
            spot = ParkingSpot.query.get(record.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            record_data = {
                'reservation_id': record.id,
                'lot_name': lot.prime_location_name,
                'spot_number': spot.spot_number,
                'parking_time': record.parking_timestamp.isoformat() if record.parking_timestamp else None,
                'leaving_time': record.leaving_timestamp.isoformat() if record.leaving_timestamp else None,
                'cost': record.parking_cost
            }
            output.append(record_data)
        return jsonify({'history': output})


@user_bp.route('/reservations/active', methods=['PUT'])
@jwt_required()
def release_spot():
    user_id = get_jwt_identity()

    active_reservation = ParkingRecord.query.filter_by(user_id=user_id, leaving_timestamp=None).first()
    if not active_reservation:
        return jsonify({"message": "No active reservation found."}), 404

    active_reservation.leaving_timestamp = datetime.datetime.utcnow()
    spot = ParkingSpot.query.get(active_reservation.spot_id)
    lot = ParkingLot.query.get(spot.lot_id)

    duration = active_reservation.leaving_timestamp - active_reservation.parking_timestamp
    hours = duration.total_seconds() / 3600
    cost = hours * lot.price
    active_reservation.parking_cost = round(cost, 2)

    spot.status = 'available'

    db.session.commit()

    # --- FIX: Clear the cache after releasing a spot ---
    redis_client.delete("all_lots")

    return jsonify({
        "message": "Spot released successfully.",
        "parking_duration_hours": round(hours, 2),
        "total_cost": active_reservation.parking_cost
    })

@user_bp.route('/export-csv', methods=['POST'])
@jwt_required()
def export_csv():
    user_id = get_jwt_identity()
    # Send the task to our Celery worker
    task = celery.send_task('tasks.export_history_task', args=[user_id])
    return jsonify({"message": "CSV export has started.", "task_id": task.id}), 202    