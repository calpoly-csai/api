"""An API endpoint module.

Contains all the handlers for the API. Also the main code to run Flask.
"""
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from modules.validators import WakeWordValidator
from modules.formatters import WakeWordFormatter
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

BAD_REQUEST = 400
SUCCESS = 200
DEBUG = True

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET', 'POST'])
def hello():
    if (request.method == 'POST'):
        request_body = request.get_json()
        return jsonify({'you sent': request_body})
    else:
        response_code = 42
        response_json = jsonify({'name': 'hello {}'.format(str(app))})
        return response_json, response_code


@app.route('/examples/wakeword', methods=['POST'])
def save_a_recording():
    """Given the audio metadata & audio file, resamples it, saves to storage.

    Resamples for the AI model. Saves to Google Drive. The audio is a
    binary BLOB with a (wrapper?). The request JSON should include a
    field representing WakeWord or NotWakeWord. Audio file size expected
    to be around 76 KB.

    Example:
    {
        'isWakeWord': True,
        'firstName': "john",
        'lastName': "doe",
        'gender': "m", // enum('m', 'f') // male, female
        'noiseLevel': "m", // enum('q','m','l') // quiet, medium, loud
        'location': "here",
        'tone': "serious",
        // TODO: consider an optional description
        'timestamp': '1577077883' //integer seconds since epoch
        'username' : 'ewenike'

    }

    Returns:
        HTTP status code
    """
    validator = WakeWordValidator()
    formatter = WakeWordFormatter()
    data = request.form
    issues = validator.validate(data)
    if issues:
        try:
            data = validator.fix(data, issues)
        except ValueError as err:
            return str(err), BAD_REQUEST
    formatted_data = formatter.format(data)
    filename = create_filename(formatted_data)
    save_audiofile(filename, request.files["wav_file"])
    return filename


def create_filename(form):
    """Creates a string filename that adheres to the Nimbus foramtting standard."""

    order = [
        'isWakeWord',
        'noiseLevel',
        'tone',
        'location',
        'gender',
        'lastName',
        'firstName',
        'timestamp',
        'username'
    ]
    values = list(map(lambda key: str(form[key]), order))
    return '_'.join(values) + '.wav'


def resample_audio():
    """Resample the audio file to adhere to the Nimbus audio sampling standard."""
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
    # constants.json since we probably shouldn't have that ID floating around on GitHub"""
    folder_id = get_folder_id()
    file = drive.CreateFile({"parents": [{"kind": "drive#fileLink",
    "id": folder_id}], 'title':filename, 'mimeType':'audio/wav'})
    # Set the content of the file to the POST request's wav_file parameter.
    file.content = content
    file.Upload() # Upload file.

def get_folder_id():
    with open("folder_id.txt") as folder_id_file:
        return folder_id_file.readline()

def convert_to_mfcc():
    """Get this function from https://github.com/calpoly-csai/CSAI_Voice_Assistant"""
    pass


@app.route('/times10/<int:num>', methods=['GET'])
def get_times10(num):
    return jsonify({'result': num*10})


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=DEBUG)
