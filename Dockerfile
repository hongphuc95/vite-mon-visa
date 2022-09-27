FROM ubuntu:20.04

ENV EMAIL_NOTIFY_ENABLED false
ENV SMS_NOTIFY_ENABLED false
ENV LOG_PATH ./logs/
ENV REFRESH_TIME 300
ENV TZ Europe/Paris
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install --no-install-recommends -y python3.9 python3.9-dev python3.9-venv python3-pip python3-wheel build-essential firefox wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python3", "./app.py"]