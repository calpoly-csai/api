#
# This Dockerfile will configure the environment for Google Compute Engine
#
FROM ubuntu:latest

# the chmod will
# resolve PermissionError on heroku
# more context in issue #100
# TODO: make chmod less insecure by only setting needed permissions
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
  && apt-get install -y python3-pip python3-dev certbot cron git \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip \
  && chmod 777 /usr/lib/python3/dist-packages/*

# verify permissions set
RUN ls -lah /usr/lib/python3/dist-packages/

# put the requirements file into the container
ADD requirements.txt /nimbus/requirements.txt

# install the requirements in the container
RUN pip3 install -r /nimbus/requirements.txt \
  && chmod 777 /usr/lib/python3/dist-packages/*

# verify permissions set
RUN ls -lah /usr/lib/python3/dist-packages/

# put all the code into nimbus folder
ADD . /nimbus

EXPOSE 443:443

# need to declare the --build-arg that gets passed in
# for ENV to work properly
ARG DATABASE_HOSTNAME
ARG DATABASE_PASSWORD
ARG DATABASE_USERNAME
ARG DATABASE_NAME
ARG PYDRIVE_CLIENT_ID
ARG PYDRIVE_CLIENT_SECRET
ARG GOOGLE_DRIVE_CREDENTIALS
ARG GOOGLE_DRIVE_FOLDER_ID
ARG GOOGLE_CLOUD_NLP_CREDENTIALS
ARG GOOGLE_CLOUD_NLP_MODEL_NAME
ARG GIT_SSH_CERT
# this lets you say `ENV PORT ${PORT}` below (the one within the ${...})
ARG PORT


# env variables needed for the setup_special_files_from_env.py
ENV DATABASE_HOSTNAME ${DATABASE_HOSTNAME}
ENV DATABASE_PASSWORD ${DATABASE_PASSWORD}
ENV DATABASE_USERNAME ${DATABASE_USERNAME}
ENV DATABASE_NAME ${DATABASE_NAME}
ENV PYDRIVE_CLIENT_ID ${PYDRIVE_CLIENT_ID}
ENV PYDRIVE_CLIENT_SECRET ${PYDRIVE_CLIENT_SECRET}
ENV GOOGLE_DRIVE_CREDENTIALS ${GOOGLE_DRIVE_CREDENTIALS}
ENV GOOGLE_DRIVE_FOLDER_ID ${GOOGLE_DRIVE_FOLDER_ID}
ENV GOOGLE_CLOUD_NLP_CREDENTIALS ${GOOGLE_CLOUD_NLP_CREDENTIALS}
ENV GOOGLE_CLOUD_NLP_MODEL_NAME ${GOOGLE_CLOUD_NLP_MODEL_NAME}
ENV GIT_SSH_CERT ${GIT_SSH_CERT}
# gunicorn will look for PORT.
# --build-arg PORT="$SSL_PORT" will choose `443` for production
ENV PORT ${PORT}


# need set WORKDIR for setup_special_files_from_env.py to save config.json to right place
WORKDIR /nimbus

# generate all the special configuration files
RUN ./setup_special_files_from_env.py

RUN python -m pip install --upgrade urllib3

# get en_core_web_sm
RUN python3 -m spacy download en_core_web_sm
# RUN python3 -m spacy download en_core_web_lg

# just make sure the file is there
RUN ls | grep config

# need set WORKDIR for gunicorn
WORKDIR /nimbus

# verify permissions set
RUN ls -lah /usr/lib/python3/dist-packages/

# setup SSH keys correctly
RUN /nimbus/scripts/setup_letsencrypt.sh

# the gunicorn_config.py will check the env vars for PORT
# else it will do port=8080
CMD ["gunicorn", \
  "flask_api:app", \
  "--config=gunicorn_config.py", \
  "--keyfile=/etc/letsencrypt/live/nimbus.api.calpolycsai.com/privkey.pem", \
  "--certfile=/etc/letsencrypt/live/nimbus.api.calpolycsai.com/cert.pem", \
  "--ca-certs=/etc/letsencrypt/live/nimbus.api.calpolycsai.com/chain.pem" \
  ]
