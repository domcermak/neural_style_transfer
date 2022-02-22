FROM ubuntu:20.04

LABEL version="0.1"

EXPOSE 8051

COPY ./Makefile /
COPY ./requirements/presentation_app/requirements.txt /
COPY ./setup.py /
COPY ./presentation_app /presentation_app
COPY ./data /data
COPY ./common /common
COPY ./qr-code.png /

RUN apt-get update -y
RUN apt-get install -y python3.9
RUN apt-get install -y python3-pip
RUN apt-get install -y libpq-dev
RUN apt-get install -y make
RUN python3 -m pip install pathlib
RUN make install

CMD [ "make", "run_presentation_app" ]