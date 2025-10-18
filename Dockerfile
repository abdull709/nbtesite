# nbtesite/Dockerfile
FROM python:3.11-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gfortran libopenblas-dev liblapack-dev \
    default-libmysqlclient-dev libjpeg-dev zlib1g-dev libmagic1 pkg-config curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Create entrypoint for Heroku
COPY heroku-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE $PORT
CMD ["/entrypoint.sh"]