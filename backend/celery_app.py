from app import create_app
from extensions import celery

# Create the Flask app using the factory.
# This ensures the celery object (imported from extensions) is fully configured
# with the app context before the worker starts.
app = create_app()

# The celery command `celery -A celery_app.celery` needs to find this exact
# `celery` object in this file.