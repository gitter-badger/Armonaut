FROM ubuntu:17.10

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install package manager requirements which are less likely to change.
RUN apt-get update && \
    apt-get install -y build-essential \
                       libssl-dev \
                       libffi-dev \
                       python3-dev \
                       python3-pip \
                       python3-venv

# Install pipenv and copy in our Pipfile which is less likely
# to change compared to our code to try to skip reinstalling
# requirements whenever we change our code.
WORKDIR /opt/armonaut
COPY requirements.txt dev-requirements.txt /opt/armonaut/
RUN python3 -m pip install --no-cache-dir -r requirements.txt -r dev-requirements.txt

# Finally add all our code to the image which will change often.
ADD . /opt/armonaut
