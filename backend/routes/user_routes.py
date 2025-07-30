from flask import request, jsonify, Blueprint
from models import ParkingLot, ParkingSpot, ParkingRecord, User
from extensions import db, redis_client, celery
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import datetime

# This Blueprint handles all routes for a regular, logged-in user.
user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/lots', methods=['GET'])
@jwt_required()
def get_available_lots():
    """Returns a list of all available parking lots, using a cache for performance."""
    cache_key = "all_lots"
    # First, attempt to retrieve the list of lots from the Redis cache.
    cached_lots = redis_client.get(cache_key)

    if cached_lots:
        # If found in cache, return the cached data immediately.
        return jsonify({'lots': json.loads(cached_lots)})

    # If not in cache, query the main database.
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

    # Store the fresh data in the cache for 1 hour (3600 seconds).
    redis_client.setex(cache_key, 3600, json.dumps(output))

    return jsonify({'lots': output})


@user_bp.route('/reservations', methods=['GET', 'POST'])
@jwt_required()
def handle_reservations():
    """Handles creating a new reservation and fetching the user's history."""
    user_id = get_jwt_identity()

    # POST: Creates a new parking reservation for the user.
    if request.method == 'POST':
        data = request.get_json()
        lot_id = data.get('lot_id')

        # Rule: A user cannot have more than one active reservation at a time.
        active_reservation = ParkingRecord.query.filter_by(user_id=user_id, leaving_timestamp=None).first()
        if active_reservation:
            return jsonify({"message": "You already have an active parking reservation."}), 409

        # Find the first available spot in the selected lot.
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='available').first()
        if not available_spot:
            return jsonify({"message": "No available spots in this parking lot."}), 404

        # Update the spot's status and create the reservation record.
        available_spot.status = 'occupied'
        new_reservation = ParkingRecord(user_id=user_id, spot_id=available_spot.id)
        db.session.add(new_reservation)
        db.session.commit()

        # --- Cache Invalidation ---
        # A spot has been taken, so the lot details are now outdated.
        # We must delete the cache to force the next request to get fresh data.
        redis_client.delete("all_lots")

        return jsonify({
            "message": "Spot booked successfully!",
            "lot_id": available_spot.lot_id,
            "spot_number": available_spot.spot_number
        }), 201

    # GET: Returns the current user's entire parking history.
    elif request.method == 'GET':
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
    """Releases a user's active spot, calculates the cost, and ends the session."""
    user_id = get_jwt_identity()

    # Find the user's current active reservation.
    active_reservation = ParkingRecord.query.filter_by(user_id=user_id, leaving_timestamp=None).first()
    if not active_reservation:
        return jsonify({"message": "No active reservation found."}), 404

    # Record the leaving time.
    active_reservation.leaving_timestamp = datetime.datetime.utcnow()
    
    spot = ParkingSpot.query.get(active_reservation.spot_id)
    lot = ParkingLot.query.get(spot.lot_id)

    # --- Cost Calculation Logic ---
    duration = active_reservation.leaving_timestamp - active_reservation.parking_timestamp
    hours = duration.total_seconds() / 3600
    cost = hours * lot.price
    active_reservation.parking_cost = round(cost, 2)

    # Update the spot's status back to 'available'.
    spot.status = 'available'
    db.session.commit()

    # --- Cache Invalidation ---
    # A spot has been freed, so the lot details are now outdated.
    redis_client.delete("all_lots")

    return jsonify({
        "message": "Spot released successfully.",
        "parking_duration_hours": round(hours, 2),
        "total_cost": active_reservation.parking_cost
    })

@user_bp.route('/export-csv', methods=['POST'])
@jwt_required()
def export_csv():
    """Triggers a background job to export the user's history to a CSV file."""
    user_id = get_jwt_identity()
    # Send the task to the Celery worker to run in the background.
    task = celery.send_task('tasks.export_history_task', args=[user_id])
    return jsonify({"message": "CSV export has started. The file will be available shortly."}), 202