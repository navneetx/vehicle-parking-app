from extensions import db
import datetime

# User Model: Stores user data
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False) 
    role = db.Column(db.String(50), nullable=False, default='user') # Differentiates between 'user' and 'admin'

# ParkingLot Model: Stores details about each parking lot
class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)

# ParkingSpot Model: Represents an individual spot in a lot
class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='available') # e.g., 'available', 'occupied'

# ParkingRecord Model: Tracks each parking session
class ParkingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=True) # Nullable until the user leaves
    parking_cost = db.Column(db.Float, nullable=True) # Nullable until cost is calculated