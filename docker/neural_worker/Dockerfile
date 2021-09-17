FROM ubuntu:20.04

LABEL version="0.1"

COPY ./Makefile /
COPY ./requirements.txt /
COPY ./setup.py /
COPY ./neural_worker /neural_worker
COPY ./data /data
COPY ./common /common

RUN apt-get update -y
RUN apt-get install -y python3.9
RUN apt-get install -y python3-pip
RUN apt-get install -y make
RUN python3 -m pip install pathlib
RUN make install

CMD [ "make", "run_neural_worker" ]