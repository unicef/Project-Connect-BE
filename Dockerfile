FROM python:3.8-buster

# Install dependencies
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    build-essential \
    libcurl4-openssl-dev \
    libjpeg-dev \
    vim \
    ntp \
    libpq-dev
RUN apt-get install -y --no-install-recommends \
    git-core
RUN apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq-dev \
    python-psycopg2
RUN apt-get install -y --no-install-recommends \
    python-gdal \
    gdal-bin \
    libgdal-dev \
    libgdal20 \
    libxml2-dev \
    libxslt-dev \
    xmlsec1

RUN pip install --upgrade \
    setuptools \
    pip \
    wheel \
    pipenv

# ssh
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
        && apt-get install -y --no-install-recommends dialog \
        && apt-get update \
	&& apt-get install -y --no-install-recommends openssh-server \
	&& echo "$SSH_PASSWD" | chpasswd

COPY sshd_config /etc/ssh/

# python app
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /code

RUN mkdir /code

ADD Pipfile /code/Pipfile
ADD Pipfile.lock /code/Pipfile.lock

WORKDIR /code/

 # todo: try to figure out how we can test using dev packages and exclude them from prod build at the same time...
RUN pipenv install --ignore-pipfile --dev

ADD . /code/
# cleanup env files if any
RUN find . -type f -name '.env' -delete

EXPOSE 8000 2222
