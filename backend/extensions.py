from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from celery import Celery
from celery.schedules import crontab
import redis
from flask_mail import Mail

db = SQLAlchemy()
jwt = JWTManager()

celery = Celery(
    __name__,
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['tasks']
)

# Define the schedule directly on the celery object
celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'tasks.daily_reminder_task',
        'schedule': 30.0,  # Runs every 30 seconds for testing
    },
    # This is the new schedule for the monthly report
    'send-monthly-reports': {
        'task': 'tasks.monthly_report_task',
        'schedule': 60.0, # Runs every 60 seconds for testing
        # Real schedule would be: crontab(day_of_month=1, hour=5, minute=0)
    },
}

redis_client = redis.Redis(decode_responses=True)
mail = Mail()