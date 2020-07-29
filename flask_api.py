#!/usr/bin/env python3
"""An API endpoint module.

Contains all the handlers for the API. Also the main code to run Flask.
"""
from sqlalchemy.exc import OperationalError

from flask import Flask, jsonify, request
from flask_cors import CORS
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import json

import gunicorn_config
from Entity.Calendars import Calendars
from Entity.Clubs import Clubs
from Entity.Courses import Courses
from Entity.Locations import Locations
from Entity.Sections import Sections
from Entity.Professors import Professors
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
from Entity.QuestionLog import QuestionLog

from Entity.EntityToken import EntityToken

from nimbus import Nimbus

import json

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


def init_nimbus_db():
    global db
    global nimbus

    # If not connected to db, initialize db connection and Nimbus client
    if db is None:
        db = NimbusMySQLAlchemy(config_file=CONFIG_FILE_PATH)
        nimbus = Nimbus(db)
    # If not connected, reset db and Nimbus client
    else:
        try:
            db.engine.connect()
        except OperationalError:
            db = NimbusMySQLAlchemy(config_file=CONFIG_FILE_PATH)
            nimbus = Nimbus(db)


@app.errorhandler(OperationalError)
def handle_database_error(error):
    global db
    if db is None:
        # reinit the database
        init_nimbus_db()
    else:
        # we *probably* have a bad session - try and roll it back,
        # then create a new database connection.
        db.session.rollback()
        db.session.close()
        db = None
        init_nimbus_db()


@app.route("/", methods=["GET", "POST"])
def hello():
    """
    always return SUCCESS (200) code on this route, to serve as a health check.
    """
    if request.method == "POST":
        request_body = request.get_json()
        return jsonify({"you sent": request_body}), SUCCESS
    else:
        response_json = jsonify({"name": "hello {}".format(str(app))})
        return response_json, SUCCESS


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
    init_nimbus_db()

    if request.is_json is False:
        return "request must be JSON", BAD_REQUEST

    request_body = request.get_json()

    question = request_body.get("question", None)

    if "question" not in request_body:
        return "request body should include the question", BAD_REQUEST

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
    if "wav_file" not in request.files:
        return (
            "Please provide an audio file under the key 'wav_file' in your FormData",
            BAD_REQUEST,
        )
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
    try:
        file_id = save_audiofile(filename, request.files["wav_file"])
    except Exception as err:
        return f"Failed to save audio file because... {err}", BAD_REQUEST

    formatted_data["audio_file_id"] = file_id

    init_nimbus_db()

    try:
        db.insert_entity(AudioSampleMetaData, formatted_data)
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

    return f"Successfully stored audiofile as '{filename}'", SUCCESS


@app.route("/new_data/office_hours", methods=["POST"])
def save_office_hours():
    """
    Persists list of office hours
    """
    init_nimbus_db()

    data = json.loads(request.get_json())
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
    data = json.loads(request.get_json())
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

    init_nimbus_db()

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


@app.route("/data/get_phrase/<numQueries>", methods=["GET"])
def get_phrase(numQueries):
    init_nimbus_db()
    try:
        # if no phrases are unvalidated, will return an empty list
        return {"data": db.get_unvalidated_qa_data(numQueries)}, SUCCESS
    except NimbusDatabaseError as e:
        return str(e), SERVER_ERROR
    except Exception as e:
        raise e


@app.route("/new_data/update_phrase", methods=["POST"])
def update_query_phrase():
    init_nimbus_db()
    data = request.get_json()
    try:
        updated = db.update_entity(QuestionAnswerPair, data, [])
    except (BadDictionaryKeyError, BadDictionaryValueError) as e:
        return str(e), BAD_REQUEST
    except NimbusDatabaseError as e:
        return str(e), SERVER_ERROR
    except Exception as e:
        raise e

    return (
        ("Phrase updated!", SUCCESS)
        if updated
        else ("Failed to update phrase", SERVER_ERROR)
    )


@app.route("/new_data/delete_phrase", methods=["POST"])
def delete_query_phrase():
    init_nimbus_db()
    data = request.get_json()
    if "id" not in data or type(data["id"]) != int:
        return "Please provide 'id' as an integer"
    identifier = data["id"]
    try:
        deleted = db.delete_entity(QuestionAnswerPair, identifier)
    except (BadDictionaryKeyError, BadDictionaryValueError) as e:
        return str(e), BAD_REQUEST
    except NimbusDatabaseError as e:
        return str(e), SERVER_ERROR
    except Exception as e:
        raise e

    return (
        ("Phrase deleted!", SUCCESS)
        if deleted
        else ("Failed to delete phrase", SERVER_ERROR)
    )

@app.route("/entity_structure", methods=["GET"])
def get_entity_structure():
    
    def get_class_info(entity):
        keys = list(filter(lambda key: not key[0] == '_', entity.__dict__.keys()))
        return {
            "props": keys,
            "synonyms": entity.synonyms
            }

    props = {
        "COURSE": get_class_info(Courses),
        "CLUB": get_class_info(Clubs)
        }
    return jsonify(props)


@app.route("/new_data/feedback", methods=["POST"])
def save_feedback():
    validator = FeedbackValidator()
    data = json.loads(request.get_json())
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

    init_nimbus_db()

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

    data = json.loads(request.get_json())
    init_nimbus_db()

    for course in data["courses"]:
        try:
            db.update_entity(Courses, course, ["dept", "course_num"])
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


@app.route("/new_data/sections", methods=["POST"])
def save_sections():
    """
    Persists list of sections
    """
    data = json.loads(request.get_json())
    init_nimbus_db()

    for section in data["sections"]:
        try:
            db.update_entity(Sections, section, ["section_name"])
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

    data = json.loads(request.get_json())
    init_nimbus_db()

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

    data = json.loads(request.get_json())
    init_nimbus_db()

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


@app.route("/new_data/professors", methods=["POST"])
def save_professors():
    """
    Persists a list of professors
    """
    data = json.loads(request.get_json())
    init_nimbus_db()

    for prof in data["professors"]:
        try:
            print("PROF:", prof)
            db.update_entity(Professors, prof, ["email"])
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

    data = json.loads(request.get_json())
    init_nimbus_db()

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


@app.route("/schema/entity_tokens", methods=["GET"])
def get_entity_tokens():
    init_nimbus_db()
    try:
        identifiers = db.session.query(EntityToken).all()
    except:
        return "Could not fetch at this time", BAD_REQUEST
    data = list(map(lambda token: token.get_data(), identifiers))
    return jsonify(data)


@app.route("/schema/entity_tokens", methods=["POST"])
def add_entity_token():
    init_nimbus_db()
    data = request.get_json()
    try:
        new_token = EntityToken(data)
    except Exception as ex:
        return ex.args[0], BAD_REQUEST
    token_added = db.add_entity(new_token)
    if not token_added:
        return "Could not add token", BAD_REQUEST
    return "Added Token", SUCCESS


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
        "name": last_name + ", " + first_name,
        "last_name": last_name,
        "first_name": first_name,
        "office": current_prof["Office"],
        "phone": current_prof["Phone"],
        "email": current_prof["Email"],
        "monday": current_prof["Monday"],
        "tuesday": current_prof["Tuesday"],
        "wednesday": current_prof["Wednesday"],
        "thursday": current_prof["Thursday"],
        "friday": current_prof["Friday"],
        "office_hours": office_hours,
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
    """
     Saves audio to the club Google Drive folder.

     Parameters
     ----------
     - `filename:str` the name of the file, formatted by `create_filename()`
     - `content: file` audio file to store

     Returns
     -------
     The Google Drive file id that can be used to retrieve the file
     """
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
    return file["id"]


def get_folder_id():
    with open("folder_id.txt") as folder_id_file:
        return folder_id_file.readline()


def convert_to_mfcc():
    """Get this function from https://github.com/calpoly-csai/CSAI_Voice_Assistant"""
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=gunicorn_config.DEBUG_MODE,
            port=gunicorn_config.PORT)
