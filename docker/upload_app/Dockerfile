FROM ubuntu:20.04

LABEL version="0.1"

EXPOSE 8080

COPY ./Makefile /
COPY ./requirements.txt /
COPY ./setup.py /
COPY ./upload_app /upload_app
COPY ./data /data
COPY ./common /common
COPY ./components/RadioButtonImages /components/RadioButtonImages

RUN apt-get update -y
RUN apt-get install -y python3.9
RUN apt-get install -y python3-pip
RUN apt-get install -y libpq-dev
RUN apt-get install -y make
RUN apt-get install -y nodejs
RUN apt-get install -y npm
RUN python3 -m pip install pathlib

WORKDIR /components/RadioButtonImages
RUN make build

WORKDIR /
RUN make install

CMD [ "make", "run_upload_app" ]