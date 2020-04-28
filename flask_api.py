#!/usr/bin/env python3
"""An API endpoint module.

Contains all the handlers for the API. Also the main code to run Flask.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import gunicorn_config
from Entity.Calendars import Calendars
from Entity.Clubs import Clubs
from Entity.Courses import Courses
from Entity.Locations import Locations
from Entity.QuestionLog import QuestionLog
from database_wrapper import (
    BadDictionaryKeyError,
    BadDictionaryValueError,
    NimbusDatabaseError,
    NimbusMySQLAlchemy,
)
from modules.formatters import WakeWordFormatter
from modules.validators import (
    WakeWordValidator,
    WakeWordValidatorError,
    PhrasesValidator,
    PhrasesValidatorError,
    FeedbackValidator,
    FeedbackValidatorError,
)

from Entity.AudioSampleMetaData import AudioSampleMetaData
from Entity.QuestionAnswerPair import QuestionAnswerPair
from Entity.QueryFeedback import QueryFeedback

from nimbus import Nimbus

BAD_REQUEST = 400
SUCCESS = 200
SERVER_ERROR = 500

CONFIG_FILE_PATH = "config.json"

app = Flask(__name__)
CORS(app)

# NOTE:
#   1. Flask "@app.route" decorated functions below commonly use a db or nimbus object
#   2. Because the decorated functions can't take parameters (because they're called by
#      the flask web server) the database and nimbus objects must be global
#   3. Instantiating objects at the global level (especially ones that are resource-intensive
#      to create like db and nimbus objects) is obviously bad practice
#
# Due to these points, the very un-Pythonic solution chosen is to initialize these objects as
# None at the top level, associate them with actual objects in the `initialize*()` functions,
# and do None checks in the functions below.

db = None
nimbus = None


def initializeDB():
    global db
    if db is None:
        db = NimbusMySQLAlchemy(config_file=CONFIG_FILE_PATH)


def initializeNimbus():
    global nimbus
    if nimbus is None:
        initializeDB()
        nimbus = Nimbus(db)


@app.route("/", methods=["GET", "POST"])
def hello():
    if request.method == "POST":
        request_body = request.get_json()
        return jsonify({"you sent": request_body})
    else:
        response_code = 42
        response_json = jsonify({"name": "hello {}".format(str(app))})
        return response_json, response_code


def generate_session_token() -> str:
    return "SOME_NEW_TOKEN"


@app.route("/ask", methods=["POST"])
def handle_question():
    """
    POST (not GET) request because the `question` is submitted
    and an `answer` is "created." Also, some side-effects on the
    server are:
        * storage of the logs of this question-answer-session.
    """
    initializeNimbus()

    if request.is_json is False:
        return "request must be JSON", BAD_REQUEST

    request_body = request.get_json()

    question = request_body.get("question", None)

    if "question" not in request_body:
        return "request body should include the question", BAD_REQUEST

    # Store
    db = NimbusMySQLAlchemy(config_file=CONFIG_FILE_PATH)
    try:
        feedback_saved = db.insert_entity(QuestionLog, {"question": question})
    except (Exception) as e:
        print("Could not store question upon user ask: ", str(e))

    response = {"answer": nimbus.answer_question(question)}
    if "session" in request_body:
        response["session"] = request_body["session"]
    else:
        response["session"] = generate_session_token()

    return jsonify(response), SUCCESS


@app.route("/new_data/wakeword", methods=["POST"])
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
    formatted_data["filename"] = filename

    initializeDB()

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


@app.route("/new_data/office_hours", methods=["POST"])
def save_office_hours():
    """
    Persists list of office hours
    """
    initializeDB()

    data = request.get_json()
    for professor in data:
        try:
            process_office_hours(data[professor], db)
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


@app.route("/new_data/phrase", methods=["POST"])
def save_query_phrase():
    validator = PhrasesValidator()
    data = request.get_json()
    try:
        issues = validator.validate(data)
    except:
        return (
            "Please format the query data: {question: {text: string, variables: list}, answer: {text: string, variables: list}}",
            BAD_REQUEST,
        )
    if issues:
        try:
            data = validator.fix(data, issues)
        except PhrasesValidatorError as err:
            print("error", err)
            return str(err), BAD_REQUEST

    initializeDB()

    try:
        phrase_saved = db.insert_entity(QuestionAnswerPair, data)
    except (BadDictionaryKeyError, BadDictionaryValueError) as e:
        return str(e), BAD_REQUEST
    except NimbusDatabaseError as e:
        return str(e), SERVER_ERROR
    except Exception as e:
        raise e

    if phrase_saved:
        return "Phrase has been saved", SUCCESS
    else:
        return "An error was encountered while saving to database", SERVER_ERROR


@app.route("/new_data/feedback", methods=["POST"])
def save_feedback():
    validator = FeedbackValidator()
    data = request.get_json()
    try:
        issues = validator.validate(data)
    except:
        return (
            "Please format the query data: {question: String, answer: String, type: String, timestamp: int}",
            BAD_REQUEST,
        )
    if issues:
        try:
            data = validator.fix(data, issues)
        except FeedbackValidatorError as err:
            print("error:", err)
            return str(err), BAD_REQUEST

    initializeDB()

    try:
        feedback_saved = db.insert_entity(QueryFeedback, data)
    except (BadDictionaryKeyError, BadDictionaryValueError) as e:
        return str(e), BAD_REQUEST
    except NimbusDatabaseError as e:
        return str(e), SERVER_ERROR
    except Exception as e:
        raise e

    if feedback_saved:
        return "Feedback has been saved", SUCCESS
    else:
        return "An error was encountered while saving to database", SERVER_ERROR


@app.route("/new_data/courses", methods=["POST"])
def save_courses():
    """
    Persists list of courses
    """
    data = request.get_json()
    initializeDB()

    for course in data["courses"]:
        try:
            db.update_entity(Courses, course, ["dept", "courseNum"])
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


@app.route("/new_data/clubs", methods=["POST"])
def save_clubs():
    """
    Persists list of clubs
    """
    data = request.get_json()
    initializeDB()

    for club in data["clubs"]:
        try:
            db.update_entity(Clubs, club, ["club_name"])
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


@app.route("/new_data/locations", methods=["POST"])
def save_locations():
    """
    Persists list of locations
    """
    data = request.get_json()
    initializeDB()

    for location in data["locations"]:
        try:
            db.update_entity(Locations, location, ["longitude", "latitude"])
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


@app.route("/new_data/calendars", methods=["POST"])
def save_calendars():
    """
    Persists list of calendars
    """
    data = request.get_json()
    initializeDB()

    for calendar in data["calendars"]:
        try:
            db.update_entity(Calendars, calendar, ["date", "raw_events_text"])
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
        "isWakeWord",
        "noiseLevel",
        "tone",
        "location",
        "gender",
        "lastName",
        "firstName",
        "timestamp",
        "username",
    ]
    values = list(
        map(lambda key: str(form[key]).lower().replace(" ", "-"), order))
    return "_".join(values) + ".wav"


def process_office_hours(current_prof: dict, db: NimbusMySQLAlchemy):
    """
    Takes the path to a CSV, reads the data row-by-row,
    and stores the data to the database

    Ex: def process_office_hours(
                        current_prof: dict,
                        db: NimbusMySQLAlchemy
                        )

    """
    # Set the entity type as the OfficeHours entity class
    entity_type = db.OfficeHours

    # Check if the current entity is already within the database
    if (
            db.get_property_from_entity(
                prop="Name", entity=entity_type, identifier=current_prof["Name"]
            )
            != None
    ):

        update_office_hours = True

    else:
        update_office_hours = False

    # String for adding each day of office hours
    office_hours = ""

    # Split name for first and last name
    split_name = current_prof["Name"].split(",")

    # Extract each property for the entity
    last_name = split_name[0].replace('"', "")
    first_name = split_name[1].replace('"', "")

    # Check that each extracted property is not empty then add it to
    # the office hours string
    if current_prof["Monday"] != "":

        # Check that the current property does not contain digits which
        # implies that it is alternative information about availability
        if any(char.isdigit() for char in current_prof["Monday"]) == False:
            office_hours = current_prof["Monday"]

        # Otherwise it is a time
        else:
            office_hours += "Monday " + current_prof["Monday"] + ", "

    if current_prof["Tuesday"] != "":
        office_hours += "Tuesday " + current_prof["Tuesday"] + ", "

    if current_prof["Wednesday"] != "":
        office_hours += "Wednesday " + current_prof["Wednesday"] + ", "

    if current_prof["Thursday"] != "":
        office_hours += "Thursday " + current_prof["Thursday"] + ", "

    if current_prof["Friday"] != "" and current_prof["Friday"] != "\n":
        office_hours += "Friday " + current_prof["Friday"] + ", "

    # Generate the data structure for the database entry
    sql_data = {
        "Name": last_name + ", " + first_name,
        "LastName": last_name,
        "FirstName": first_name,
        "Office": current_prof["Office"],
        "Phone": current_prof["Phone"],
        "Email": current_prof["Email"],
        "Monday": current_prof["Monday"],
        "Tuesday": current_prof["Tuesday"],
        "Wednesday": current_prof["Wednesday"],
        "Thursday": current_prof["Thursday"],
        "Friday": current_prof["Friday"],
        "OfficeHours": office_hours,
    }

    # Update the entity properties if the entity already exists
    if update_office_hours == True:
        db.update_entity(
            entity_type=entity_type, data_dict=sql_data, filter_fields=[
                "Email"]
        )

    # Otherwise, add the entity to the database
    else:
        db.insert_entity(entity_type=entity_type, data_dict=sql_data)


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
    file = drive.CreateFile(
        {
            "parents": [{"kind": "drive#fileLink", "id": folder_id}],
            "title": filename,
            "mimeType": "audio/wav",
        }
    )
    # Set the content of the file to the POST request's wav_file parameter.
    file.content = content
    file.Upload()  # Upload file.


def get_folder_id():
    with open("folder_id.txt") as folder_id_file:
        return folder_id_file.readline()


def convert_to_mfcc():
    """Get this function from https://github.com/calpoly-csai/CSAI_Voice_Assistant"""
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=gunicorn_config.DEBUG_MODE,
            port=gunicorn_config.PORT)