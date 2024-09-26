FROM python:3.11-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy just the requirements.txt initially to leverage Docker cache
COPY requirements.txt /app/

# Install necessary packages, Python libraries, and clean up in one command to keep the image slim
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libc-dev linux-headers g++ geos-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

COPY . /app/

CMD ["gunicorn", "mishwari_server.wsgi:application", "--bind", "0.0.0.0:8000"]
