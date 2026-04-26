FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install \
        git python3 python3-dev pip -y \
    && rm -rf /var/lib/apt/lists/*

RUN pip install python-telegram-bot[job-queue] --break-system-packages

RUN git clone https://github.com/george-kurshakov/poll-webpage-bot.git

WORKDIR /poll-webpage-bot

CMD ["python3", "main.py"]