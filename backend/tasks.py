import csv
import os
import datetime
from dateutil.relativedelta import relativedelta
from flask import render_template
from extensions import celery, mail
from models import ParkingRecord, ParkingSpot, ParkingLot, User
from flask_mail import Message

@celery.task
def export_history_task(user_id):
    """Generate a CSV of a user's parking history."""
    user = User.query.get(user_id)
    if not user:
        return "User not found."

    export_dir = 'exports'
    os.makedirs(export_dir, exist_ok=True)
    
    filename = os.path.join(export_dir, f'history_{user.username}.csv')
    print(f"Generating CSV for {user.username} at {filename}...")

    records = ParkingRecord.query.filter_by(user_id=user_id).order_by(ParkingRecord.parking_timestamp.desc()).all()

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
    return f"CSV generated at {filename}"


@celery.task
def daily_reminder_task():
    """Send promotional reminder emails to all users."""
    print("\n--- Running Daily Reminder Task ---")
    users = User.query.filter_by(role='user').all()
    for user in users:
        msg = Message(
            subject="Parking App Daily Reminder",
            recipients=[f"{user.username}@example.com"],  # Fake email for Mailhog
            body=f"Hi {user.username}, don't forget to book a parking spot today!"
        )
        mail.send(msg)
        print(f"Sending daily reminder email to: {user.username}")
    
    print("--- Daily Reminder Task Complete ---\n")
    return f"Sent email reminders to {len(users)} users."


@celery.task
def monthly_report_task():
    """Generate and email monthly parking reports to all users."""
    print("\n--- Running Monthly Report Task ---")

    today = datetime.date.today()

    # --- THIS LOGIC IS CHANGED FOR TESTING ---
    # It now looks for records in the CURRENT month instead of the PREVIOUS month.
    first_day_of_month = today.replace(day=1)
    first_day_next_month = (today.replace(day=1) + relativedelta(months=1))
    
    users = User.query.filter_by(role='user').all()

    reports_sent = 0
    for user in users:
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

        html_body = render_template(
            'report.html',
            username=user.username,
            reporting_period=today.strftime('%B %Y'),
            total_spent=total_spent,
            total_parkings=len(records),
            records=report_data
        )

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