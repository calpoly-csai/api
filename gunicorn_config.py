#!/usr/bin/env python3

"""
This python script will initialize variables
to configure Gunicorn workers that support the Flask API server.
"""

from os import environ
import multiprocessing

PORT = int(environ.get("PORT", 8080))
DEBUG_MODE = int(environ.get("DEBUG_MODE", 1))

# Gunicorn config
bind = ":" + str(PORT)
#workers = multiprocessing.cpu_count() * 2 + 1
# The above is considered bad practice - cpu_count() can be unreliable.
# We have 1 core, so 1 * 2 + 1 = 3
workers = 3
timeout = 90
keyfile = "/etc/letsencrypt/live/nimbus.api.calpolycsai.com/privkey.pem"
certfile = "/etc/letsencrypt/live/nimbus.api.calpolycsai.com/cert.pem"
ca_certs = "/etc/letsencrypt/live/nimbus.api.calpolycsai.com/chain.pem"
