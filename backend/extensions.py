# In backend/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import redis

db = SQLAlchemy()
jwt = JWTManager()
# Create a Redis client instance
# decode_responses=True ensures we get strings back from Redis, not bytes
redis_client = redis.Redis(decode_responses=True)