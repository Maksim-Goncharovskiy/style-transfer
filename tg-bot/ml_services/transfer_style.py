from celery_config import app
import time



@app.task()
def transfer_style(content, style, degree) -> bytes:
    time.sleep(20) # имитация бурной деятельности
    return bytes()