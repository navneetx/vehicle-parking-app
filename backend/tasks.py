import csv
import os
import datetime
from dateutil.relativedelta import relativedelta
from flask import render_template
from extensions import celery, mail
from models import ParkingRecord, ParkingSpot, ParkingLot, User
from flask_mail import Message
from app import create_app

# This file defines all the background tasks that are run by the Celery worker.

# Create a Flask app instance so our tasks can access the database and other extensions.
app = create_app()

# -----------------
# User-Triggered Task
# -----------------
@celery.task
def export_history_task(user_id):
    """Generates a CSV file of a user's parking history."""
    # Tasks run in the background, so they need their own app context
    # to access the database.
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return f"User with ID {user_id} not found."

        # Ensure the 'exports' directory exists.
        export_dir = 'exports'
        os.makedirs(export_dir, exist_ok=True)
        filename = os.path.join(export_dir, f'history_{user.username}.csv')
        
        # Fetch all parking records for the user.
        records = ParkingRecord.query.filter_by(user_id=user_id).order_by(ParkingRecord.parking_timestamp.desc()).all()

        # Write the data to a CSV file.
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Reservation ID', 'Lot Name', 'Spot Number', 'Parking Time', 'Leaving Time', 'Cost (INR)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in records:
                spot = ParkingSpot.query.get(record.spot_id)
                lot = ParkingLot.query.get(spot.lot_id)
                writer.writerow({
                    'Reservation ID': record.id,
                    'Lot Name': lot.prime_location_name,
                    'Spot Number': spot.spot_number,
                    'Parking Time': record.parking_timestamp.isoformat() if record.parking_timestamp else '',
                    'Leaving Time': record.leaving_timestamp.isoformat() if record.leaving_timestamp else '',
                    'Cost (INR)': record.parking_cost if record.parking_cost is not None else ''
                })
        
        print(f"Successfully generated CSV for {user.username}.")
        return f"CSV generated for {user.username}."

# -----------------
# Scheduled Tasks
# -----------------
@celery.task
def daily_reminder_task():
    """Sends a simple promotional reminder email to all users."""
    with app.app_context():
        print("\n--- Running Daily Reminder Task ---")
        users = User.query.filter_by(role='user').all()
        for user in users:
            msg = Message(
                subject="Parking App Daily Reminder",
                recipients=[f"{user.username}@example.com"], # Using a placeholder email for the demo
                body=f"Hi {user.username}, don't forget to book a parking spot today!"
            )
            mail.send(msg)
            print(f"Sending daily reminder email to: {user.username}")
        
        print("--- Daily Reminder Task Complete ---\n")
        return f"Sent email reminders to {len(users)} users."

@celery.task
def monthly_report_task():
    """Generates and emails a monthly activity report to each user."""
    with app.app_context():
        print("\n--- Running Monthly Report Task ---")
        today = datetime.date.today()

        # --- Date Calculation Logic (For Testing) ---
        # This logic is set to find records from the CURRENT month for the demo.
        # In a real application, this would be changed to look at the previous month.
        first_day_of_month = today.replace(day=1)
        first_day_next_month = (today.replace(day=1) + relativedelta(months=1))
        
        users = User.query.filter_by(role='user').all()
        reports_sent = 0

        for user in users:
            # Query for all completed parking sessions within the date range.
            records = ParkingRecord.query.filter(
                ParkingRecord.user_id == user.id,
                ParkingRecord.leaving_timestamp != None,
                ParkingRecord.parking_timestamp >= first_day_of_month,
                ParkingRecord.parking_timestamp < first_day_next_month
            ).all()

            if not records:
                print(f"No completed parkings this month for {user.username}. Skipping report.")
                continue

            total_spent = sum(r.parking_cost or 0 for r in records)
            
            # Prepare data for the email template.
            report_data = []
            for r in records:
                spot = ParkingSpot.query.get(r.spot_id)
                lot = ParkingLot.query.get(spot.lot_id)
                duration = r.leaving_timestamp - r.parking_timestamp
                report_data.append({
                    "lot_name": lot.prime_location_name,
                    "parking_time": r.parking_timestamp.strftime('%d-%b-%Y'),
                    "duration_hours": round(duration.total_seconds() / 3600, 2),
                    "cost": r.parking_cost
                })
            
            # Render the HTML for the email using a Jinja2 template.
            html_body = render_template(
                'report.html',
                username=user.username,
                reporting_period=today.strftime('%B %Y'),
                total_spent=total_spent,
                total_parkings=len(records),
                records=report_data
            )
            
            # Create and send the email.
            msg = Message(
                subject=f"Your Parking Report for {today.strftime('%B %Y')}",
                recipients=[f"{user.username}@example.com"],
                html=html_body
            )
            mail.send(msg)
            reports_sent += 1
            print(f"Sent monthly report to {user.username}")

        print(f"--- Monthly Report Task Complete ({reports_sent} reports sent) ---\n")
        return f"Monthly reports sent to {reports_sent} users."