#!/bin/bash
python3 -m celery -A ml_services.transfer_style worker --loglevel=INFO &

python3 main.py