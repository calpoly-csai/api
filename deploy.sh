#!/bin/bash
python3 setup_special_files_from_env.py
./download_nlp_stuff.sh
python3 download_nltk_stuff.py
gunicorn flask_api:app --config=gunicorn_config.py
