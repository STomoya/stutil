FROM python:3.8

ENV DEBIAN_FRONTEND=noniteractive
RUN apt update -y && \
    apt install -y \
    libopencv-dev \
    git

ARG UID
RUN useradd -l -m -u ${UID} dockeruser
USER ${UID}
ENV PATH=$PATH:/home/dockeruser/.local/bin

RUN python -m pip install -U pip
COPY docker/python/requirements.txt requirements.txt
RUN pip --default-timeout=100 install --user -r requirements.txt
