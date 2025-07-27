from app import create_app
from extensions import celery

app = create_app()

# Make sure Celery sees the Flask app
app.app_context().push()
