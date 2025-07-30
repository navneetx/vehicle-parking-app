from flask import request, jsonify, Blueprint
from models import ParkingLot, ParkingSpot
from extensions import db, redis_client
from flask_jwt_extended import jwt_required
from decorators import admin_required

# This Blueprint handles all CRUD operations for ParkingLots.
lot_bp = Blueprint('lot_bp', __name__)

# This route handles requests for the collection of all lots.
@lot_bp.route('/lots', methods=['GET', 'POST'])
@jwt_required()
@admin_required()
def handle_lots():
    # POST: Creates a new parking lot and its associated spots.
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

        # Automatically generate the number of spots specified by the admin.
        for i in range(1, new_lot.number_of_spots + 1):
            new_spot = ParkingSpot(lot_id=new_lot.id, spot_number=i)
            db.session.add(new_spot)

        db.session.commit()
        
        # --- Cache Invalidation ---
        # Deletes the cached list of lots because the data is now outdated.
        redis_client.delete("all_lots")

        return jsonify({"message": f"Parking lot '{new_lot.prime_location_name}' created successfully"}), 201

    # GET: Returns a list of all parking lots.
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

# This route handles requests for a single, specific lot by its ID.
@lot_bp.route('/lots/<int:lot_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
@admin_required()
def handle_specific_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({"message": "Parking lot not found"}), 404

    # GET: Returns detailed information for one lot, including the status of all its spots.
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
            'spots': spots_output
        }
        return jsonify(lot_data)

    # PUT: Updates the details of a specific lot.
    elif request.method == 'PUT':
        data = request.get_json()
        lot.prime_location_name = data.get('prime_location_name', lot.prime_location_name)
        lot.price = data.get('price', lot.price)
        lot.address = data.get('address', lot.address)
        lot.pin_code = data.get('pin_code', lot.pin_code)
        db.session.commit()
        
        # --- Cache Invalidation ---
        redis_client.delete("all_lots")
        
        return jsonify({"message": "Parking lot updated successfully"})

    # DELETE: Deletes a specific lot and all its spots.
    elif request.method == 'DELETE':
        # Rule: Cannot delete a lot if any of its spots are currently occupied.
        occupied_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='occupied').first()
        if occupied_spot:
            return jsonify({"message": "Cannot delete lot. At least one spot is currently occupied."}), 400

        # Delete all associated spots first, then the lot itself.
        ParkingSpot.query.filter_by(lot_id=lot_id).delete()
        db.session.delete(lot)
        db.session.commit()
        
        # --- Cache Invalidation ---
        redis_client.delete("all_lots")
        
        return jsonify({"message": f"Parking lot '{lot.prime_location_name}' and its spots have been deleted."})