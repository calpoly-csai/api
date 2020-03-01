from os import environ
import multiprocessing

PORT = int(environ.get("PORT", 8080))
DEBUG_MODE = int(environ.get("DEBUG_MODE", 1))

# Gunicorn config
bind = ":" + str(PORT)
workers = 3
