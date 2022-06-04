# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt update
RUN apt install wget
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install
RUN pip3 install -r requirements.txt

#pip3 install --upgrade pip
#python3 -m pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python","./src/main.py"]

