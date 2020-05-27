#!/bin/bash
#
# This script will just deploy using gunicorn locally, without docker.
#
# This deployment script is not concerned with SSL encryption.
# It just gets the code running on multiple CPU processors.
#
gunicorn flask_api:app --config=gunicorn_config.py