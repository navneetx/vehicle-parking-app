# In backend/routes/lot_routes.py

from flask import request, jsonify, Blueprint
from models import ParkingLot, ParkingSpot
from extensions import db
from flask_jwt_extended import jwt_required
from decorators import admin_required

lot_bp = Blueprint('lot_bp', __name__)

@lot_bp.route('/lots', methods=['GET', 'POST'])
@jwt_required()
@admin_required()
def handle_lots():
    # Logic for creating a new lot
    if request.method == 'POST':
        data = request.get_json()

        new_lot = ParkingLot(
            prime_location_name=data['prime_location_name'],
            price=data['price'],
            address=data['address'],
            pin_code=data['pin_code'],
            number_of_spots=data['number_of_spots']
        )
        db.session.add(new_lot)
        db.session.commit()

        for i in range(1, new_lot.number_of_spots + 1):
            new_spot = ParkingSpot(lot_id=new_lot.id, spot_number=i)
            db.session.add(new_spot)

        db.session.commit()

        return jsonify({"message": f"Parking lot '{new_lot.prime_location_name}' and its {new_lot.number_of_spots} spots created successfully"}), 201

    # Logic for retrieving all lots
    elif request.method == 'GET':
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

        return jsonify({'lots': output})

@lot_bp.route('/lots/<int:lot_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@admin_required()
def handle_specific_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({"message": "Parking lot not found"}), 404

    # Logic for getting a single lot's details
    if request.method == 'GET':
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        spots_output = []
        for spot in spots:
            spots_output.append({
                'id': spot.id,
                'spot_number': spot.spot_number,
                'status': spot.status
            })

        lot_data = {
            'id': lot.id,
            'prime_location_name': lot.prime_location_name,
            'price': lot.price,
            'address': lot.address,
            'pin_code': lot.pin_code,
            'number_of_spots': lot.number_of_spots,
            'spots': spots_output  # Nest the list of spots in the response
        }
        return jsonify(lot_data)

    # Logic for updating a lot
    elif request.method == 'PUT':
        data = request.get_json()
        lot.prime_location_name = data.get('prime_location_name', lot.prime_location_name)
        lot.price = data.get('price', lot.price)
        lot.address = data.get('address', lot.address)
        lot.pin_code = data.get('pin_code', lot.pin_code)
        db.session.commit()
        return jsonify({"message": "Parking lot updated successfully"})

    # Logic for deleting a lot
    elif request.method == 'DELETE':
        occupied_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='occupied').first()
        if occupied_spot:
            return jsonify({"message": "Cannot delete lot. At least one spot is currently occupied."}), 400

        ParkingSpot.query.filter_by(lot_id=lot_id).delete()
        db.session.delete(lot)
        db.session.commit()
        return jsonify({"message": f"Parking lot '{lot.prime_location_name}' and its spots have been deleted successfully."})