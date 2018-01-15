FROM ubuntu:17.10

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install package manager requirements which are less likely to change.
RUN apt-get update && \
    apt-get install -y build-essential \
                       curl \
                       libssl-dev \
                       libffi-dev \
                       python3-dev \
                       python3-pip \
                       python3-venv \
                       libpq-dev

WORKDIR /opt/armonaut

# Install requirements and dev-requirements before copying
# our code over to try to skip installing them every
# time code changes.
COPY requirements.txt dev-requirements.txt /opt/armonaut/
RUN python3 -m pip install --no-cache-dir -r requirements.txt -r dev-requirements.txt

# Finally add all our code to the image which will change often.
ADD . /opt/armonaut

# Remove all __pycache__ files as they mess with pytest
RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
