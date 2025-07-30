from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from celery import Celery
from celery.schedules import crontab
import redis
from flask_mail import Mail

db = SQLAlchemy()

jwt = JWTManager()

mail = Mail()

# Redis client for caching API responses
redis_client = redis.Redis(decode_responses=True)

# Celery object for handling background tasks
celery = Celery(
    __name__,
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['tasks']  # Automatically discover tasks in the tasks.py file
)

# --- Celery Beat Schedule ---
celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'tasks.daily_reminder_task', # The path to the task function
        'schedule': 30.0,  # For testing: runs every 30 seconds.
    },
    # A task named 'send-monthly-reports'
    'send-monthly-reports': {
        'task': 'tasks.monthly_report_task',
        'schedule': 60.0, # For testing: runs every 60 seconds.
        
        # 'schedule': crontab(day_of_month=1, hour=5, minute=0)
    },
}