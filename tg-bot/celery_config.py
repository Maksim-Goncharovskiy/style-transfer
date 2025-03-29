from celery import Celery
from config import load_config

app_config = load_config()

app = Celery(
    'ml_services',
    broker=f'redis://{app_config.redis.HOST}:{app_config.redis.PORT}/1',
    backend=f'redis://{app_config.redis.HOST}:{app_config.redis.PORT}/1',
)