FROM python:3.12-slim AS builder

WORKDIR /app

# Копируем файлы для установки зависимостей
COPY requirements.txt requirements.txt
COPY entrypoint.sh entrypoint.sh

# Устанавливаем Python-зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip && \
    apt-get purge -y --auto-remove gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu


# Этап 2: Создание финального образа
FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости и исходный код из первого этапа
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

COPY . .

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
