# In backend/tasks.py

from extensions import celery

@celery.task
def add_together(a, b):
    result = a + b
    print(f"Task result: {a} + {b} = {result}")
    return result