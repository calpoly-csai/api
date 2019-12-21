"""An API endpoint module.

Contains all the handlers for the API. Also the main code to run Flask.
"""
from flask import Flask, jsonify, request

DEBUG = True

app = Flask(__name__)

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
    }

    Returns:
        200 success
        TODO: figure out the non-success http status code
    """
    return jsonify({'implemented': False}), 400


def create_filename():
    """Creates a string filename that adheres to the Nimbus foramtting standard."""
    pass


def resample_audio():
    """Resample the audio file to adhere to the Nimbus audio sampling standard."""
    pass


def save_audiofile():
    """Actually save the file into Google Drive or whereever we may do it."""
    pass


def convert_to_mfcc():
    """Get this function from https://github.com/calpoly-csai/CSAI_Voice_Assistant"""
    pass


@app.route('/times10/<int:num>', methods=['GET'])
def get_times10(num):
    return jsonify({'result': num*10})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=DEBUG)
