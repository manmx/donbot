FROM jrottenberg/ffmpeg as ffmpeg

FROM python:3.7-buster

COPY --from=ffmpeg /usr/local /usr/local

RUN echo "deb http://security.debian.org/debian-security jessie/updates main" >> /etc/apt/sources.list

RUN apt-get update -y

RUN apt-get install -y --no-install-recommends \
    libssl1.0.0

RUN apt-get install -y \ 
    libavdevice-dev \
    libavfilter-dev \
    libavresample-dev \
    libpostproc-dev \
    libssl-dev

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get -y update && apt-get install -y wget nano git build-essential yasm pkg-config

# Compile and install ffmpeg from source

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

COPY . .

COPY sounds/ ./

CMD [ "python", "-u", "./donbot.py" ]
