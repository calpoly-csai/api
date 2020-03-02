#!/usr/bin/env python3
"""An API endpoint module.

Contains all the handlers for the API. Also the main code to run Flask.
"""
import json
import requests

from flask import Flask, jsonify, request
from flask_cors import CORS
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import gunicorn_config
from database_wrapper import (BadDictionaryKeyError, BadDictionaryValueError,
                              NimbusDatabaseError, NimbusMySQLAlchemy)
from modules.formatters import WakeWordFormatter
from modules.validators import WakeWordValidator, WakeWordValidatorError

from nimbus import Nimbus

BAD_REQUEST = 400
SUCCESS = 200

CONFIG_FILE_PATH = 'config.json'

app = Flask(__name__)
CORS(app)

# TODO: Initialize this somewhere else.
nimbus = Nimbus()

@app.route('/', methods=['GET', 'POST'])
def hello():
    if (request.method == 'POST'):
        request_body = request.get_json()
        return jsonify({'you sent': request_body})
    else:
        response_code = 42
        response_json = jsonify({'name': 'hello {}'.format(str(app))})
        return response_json, response_code


def generate_session_token() -> str:
    return "SOME_NEW_TOKEN"


@app.route('/ask', methods=['POST'])
def handle_question():
    """
    POST (not GET) request because the `question` is submitted
    and an `answer` is "created." Also, some side-effects on the
    server are:
        * storage of the logs of this question-answer-session.
    """

    if request.is_json is False:
        return "request must be JSON", BAD_REQUEST

    request_body = request.get_json()

    question = request_body.get('question', None)

    if "question" not in request_body:
        return "request body should include the question", BAD_REQUEST

    response = {
        "answer": nimbus.answer_question(question)
    }

    if "session" in request_body:
        response['session'] = request_body["session"]
    else:
        response['session'] = generate_session_token()

    return jsonify(response), SUCCESS


@app.route('/new_data/wakeword', methods=['POST'])
def save_a_recording():
    """Given the audio metadata & audio file, resamples it, saves to storage.
    """
    validator = WakeWordValidator()
    formatter = WakeWordFormatter()
    data = request.form
    issues = validator.validate(data)
    if issues:
        try:
            data = validator.fix(data, issues)
        except WakeWordValidatorError as err:
            return str(err), BAD_REQUEST
    formatted_data = formatter.format(data)
    filename = create_filename(formatted_data)

    # Save the audiofile first because if error then we stop here
    # We do not want to save any metadata to the NimbusDatabase
    #   if the audio fails to save.
    save_audiofile(filename, request.files["wav_file"])

    # Let's also save the filename to the database for quick reference
    formatted_data['filename'] = filename

    db = NimbusMySQLAlchemy(config_file=CONFIG_FILE_PATH)
    try:
        db.save_audio_sample_meta_data(formatted_data)
    except BadDictionaryKeyError as e:
        return str(e), BAD_REQUEST
    except BadDictionaryValueError as e:
        return str(e), BAD_REQUEST
    except NimbusDatabaseError as e:
        return str(e), BAD_REQUEST
    except Exception as e:
        # TODO: consider security tradeoff of displaying internal server errors
        #       versus development time (being able to see errors quickly)
        # HINT: security always wins
        raise e

    return filename


@app.route('/new_data/courses', methods=['POST'])
def save_courses():
    """
    Persists list of courses
    """
    data = request.get_json()
    db = NimbusMySQLAlchemy(config_file=CONFIG_FILE_PATH)
    for course in data['courses']:
        try:
            db.save_course(course)
        except BadDictionaryKeyError as e:
            return str(e), BAD_REQUEST
        except BadDictionaryValueError as e:
            return str(e), BAD_REQUEST
        except NimbusDatabaseError as e:
            return str(e), BAD_REQUEST
        except Exception as e:
            # TODO: consider security tradeoff of displaying internal server errors
            #       versus development time (being able to see errors quickly)
            # HINT: security always wins
            raise e

    return "SUCCESS"


@app.route('/new_data/clubs', methods=['POST'])
def save_clubs():
    """
    Persists list of clubs
    """
    data = request.get_json()
    db = NimbusMySQLAlchemy(config_file=CONFIG_FILE_PATH)
    for club in data['clubs']:
        try:
            db.save_club(club)
        except BadDictionaryKeyError as e:
            return str(e), BAD_REQUEST
        except BadDictionaryValueError as e:
            return str(e), BAD_REQUEST
        except NimbusDatabaseError as e:
            return str(e), BAD_REQUEST
        except Exception as e:
            # TODO: consider security tradeoff of displaying internal server errors
            #       versus development time (being able to see errors quickly)
            # HINT: security always wins
            raise e

    return "SUCCESS"


@app.route('/new_data/locations', methods=['POST'])
def save_locations():
    """
    Persists list of locations
    """
    data = request.get_json()
    db = NimbusMySQLAlchemy(config_file=CONFIG_FILE_PATH)
    for location in data['locations']:
        try:
            db.save_location(location)
        except BadDictionaryKeyError as e:
            return str(e), BAD_REQUEST
        except BadDictionaryValueError as e:
            return str(e), BAD_REQUEST
        except NimbusDatabaseError as e:
            return str(e), BAD_REQUEST
        except Exception as e:
            # TODO: consider security tradeoff of displaying internal server errors
            #       versus development time (being able to see errors quickly)
            # HINT: security always wins
            raise e

    return "SUCCESS"


@app.route('/new_data/calendars', methods=['POST'])
def save_calendars():
    """
    Persists list of calendars
    """
    data = request.get_json()
    db = NimbusMySQLAlchemy(config_file=CONFIG_FILE_PATH)
    for calendar in data['calendars']:
        try:
            db.save_calendar(calendar)
        except BadDictionaryKeyError as e:
            return str(e), BAD_REQUEST
        except BadDictionaryValueError as e:
            return str(e), BAD_REQUEST
        except NimbusDatabaseError as e:
            return str(e), BAD_REQUEST
        except Exception as e:
            # TODO: consider security tradeoff of displaying internal server errors
            #       versus development time (being able to see errors quickly)
            # HINT: security always wins
            raise e

    return "SUCCESS"


def create_filename(form):
    """
    Creates a string filename that adheres to the Nimbus foramtting standard.
    """
    order = [
        'isWakeWord', 'noiseLevel', 'tone', 'location', 'gender', 'lastName',
        'firstName', 'timestamp', 'username'
    ]
    values = list(
        map(lambda key: str(form[key]).lower().replace(" ", "-"), order))
    return '_'.join(values) + '.wav'


def resample_audio():
    """
    Resample the audio file to adhere to the Nimbus audio sampling standard.
    """
    pass


def save_audiofile(filename, content):
    """Actually save the file into Google Drive."""
    # Initialize our google drive authentication object using saved credentials,
    # or through the command line
    gauth = GoogleAuth()
    gauth.CommandLineAuth()
    # This is our pydrive object
    drive = GoogleDrive(gauth)
    # parent is our automatically uploaded file folder.  The ID should be read in from
    # folder_id.txt since we probably shouldn't have that ID floating around on GitHub"""
    folder_id = get_folder_id()
    file = drive.CreateFile({
        "parents": [{
            "kind": "drive#fileLink",
            "id": folder_id
        }],
        'title': filename,
        'mimeType': 'audio/wav'
    })
    # Set the content of the file to the POST request's wav_file parameter.
    file.content = content
    file.Upload()  # Upload file.


def get_folder_id():
    with open("folder_id.txt") as folder_id_file:
        return folder_id_file.readline()


def convert_to_mfcc():
    """Get this function from https://github.com/calpoly-csai/CSAI_Voice_Assistant"""
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            debug=gunicorn_config.DEBUG_MODE,
            port=gunicorn_config.PORT)

