from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from celery import Celery
import redis

db = SQLAlchemy()
jwt = JWTManager()
celery = Celery(__name__, broker='redis://localhost:6379/0', backend='redis://localhost:6379/0', include=['tasks'])
redis_client = redis.Redis(decode_responses=True)