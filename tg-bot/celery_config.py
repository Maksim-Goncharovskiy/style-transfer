from celery import Celery


app = Celery(
    'ml_services',
    broker='redis://localhost:6379/1',
    backend='redis://localhost:6379/1',
)