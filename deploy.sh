#!/bin/bash
gunicorn flask_api:app --config=gunicorn_config.py
