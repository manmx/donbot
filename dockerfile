FROM jrottenberg/ffmpeg:4.1-ubuntu as ffmpeg

FROM python:3.7-buster

COPY --from=ffmpeg /usr/local /usr/local

RUN apt-get update -y

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get -y update && apt-get install -y wget nano git build-essential yasm pkg-config

RUN apt-get install libopus0

# Compile and install ffmpeg from source

RUN pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY sounds/ ./

CMD [ "python", "-u", "./donbot.py" ]
