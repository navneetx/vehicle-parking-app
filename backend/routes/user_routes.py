from flask import request, jsonify, Blueprint
from models import ParkingLot, ParkingSpot, ParkingRecord, User
from extensions import db, redis_client # Import redis_client
import json # Import json for handling data
from flask_jwt_extended import jwt_required, get_jwt_identity
import datetime

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/lots', methods=['GET'])
@jwt_required()
def get_available_lots():
    cache_key = "all_lots"
    # 1. First, try to get the data from the cache
    cached_lots = redis_client.get(cache_key)

    if cached_lots:
        # If the data exists in the cache, return it immediately
        print("Serving from cache") # For debugging
        return jsonify({'lots': json.loads(cached_lots)})
    
    # 2. If data is not in the cache, query the database
    print("Serving from database") # For debugging
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
    
    # 3. Store the fresh data in the cache for next time, with an expiry of 1 hour (3600 seconds)
    redis_client.setex(cache_key, 3600, json.dumps(output))

    return jsonify({'lots': output})


@user_bp.route('/reservations', methods=['GET', 'POST'])
@jwt_required()
def handle_reservations():
    user_id = get_jwt_identity()

    # Logic to create a new reservation
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

        return jsonify({
            "message": "Spot booked successfully!",
            "lot_id": available_spot.lot_id,
            "spot_number": available_spot.spot_number
        }), 201
    
    # Logic to get the user's entire parking history
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
    user_id = get_jwt_identity()

    # Find the user's active reservation (the one without a leaving time)
    active_reservation = ParkingRecord.query.filter_by(user_id=user_id, leaving_timestamp=None).first()

    if not active_reservation:
        return jsonify({"message": "No active reservation found."}), 404

    # Set the leaving time to now
    active_reservation.leaving_timestamp = datetime.datetime.utcnow()
    
    # Find the spot and lot to get the price and update status
    spot = ParkingSpot.query.get(active_reservation.spot_id)
    lot = ParkingLot.query.get(spot.lot_id)

    # Calculate cost (assuming the price is per hour)
    duration = active_reservation.leaving_timestamp - active_reservation.parking_timestamp
    hours = duration.total_seconds() / 3600
    cost = hours * lot.price
    active_reservation.parking_cost = round(cost, 2)

    # Update the spot's status back to 'available'
    spot.status = 'available'

    db.session.commit()

    return jsonify({
        "message": "Spot released successfully.",
        "parking_duration_hours": round(hours, 2),
        "total_cost": active_reservation.parking_cost
    })