FROM ubuntu:20.04

ENV EMAIL_NOTIFY_ENABLED false
ENV SMS_NOTIFY_ENABLED false
ENV LOG_PATH ./logs/

RUN apt-get update \
    && apt-get install --no-install-recommends -y python3.9 python3.9-dev python3.9-venv python3-pip python3-wheel build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt update \                                                                                                                                                          
    && echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && apt update \
    && apt install -y google-chrome-stable firefox

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python", "./app.py"]