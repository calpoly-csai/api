import json
import pytest

import flask_api
from database_wrapper import (NimbusMySQLAlchemy, BadDictionaryKeyError, BadDictionaryValueError,
                              NimbusDatabaseError, UnsupportedDatabaseError, BadConfigFileError)
from io import BytesIO
from mock import patch, Mock
from modules.validators import WakeWordValidatorError
from .MockEntity import MockEntity


BAD_REQUEST = 400
SUCCESS = 200
SERVER_ERROR = 500
TOKEN = "test_token"
TEST_ERROR = "test error string"


@pytest.fixture
def client():
    flask_api.app.config['TESTING'] = True

    with flask_api.app.test_client() as client:
        yield client


def test_hello(client):
    resp = client.get('/')
    assert resp.json == {"name": "hello {}".format(flask_api.app)}

    test_data_dict = {"hello": "world"}
    resp = client.post('/', json=test_data_dict)
    assert resp.json == {"you sent": test_data_dict}


@patch("flask_api.nimbus")
@patch("flask_api.db")
def test_ask_request_not_json(mock_db, mock_nimbus, client):
    resp = client.post('/ask', data="dummy data")
    assert resp.status_code == BAD_REQUEST
    assert resp.data == b'request must be JSON'


@patch("flask_api.nimbus")
@patch("flask_api.db")
def test_ask_no_question(mock_db, mock_nimbus, client):
    resp = client.post('/ask', json={})
    assert resp.status_code == BAD_REQUEST
    assert resp.data == b'request body should include the question'


@patch("flask_api.generate_session_token", return_value=TOKEN)
@patch("flask_api.nimbus")
@patch("flask_api.db")
def test_ask_question(mock_db, mock_nimbus, mock_generate_session_token, client):
    test_answer = "test_answer"
    dummy_token = "dummy_token"

    mock_nimbus.answer_question.return_value = test_answer

    # Verify that calling ask without a token will return a response with a new token
    resp = client.post('/ask', json={"question": "test_question"})
    assert resp.status_code == SUCCESS
    assert resp.json == {"answer": test_answer, "session": TOKEN}

    # Verify that calling ask with a token will return a response with the same token
    resp = client.post('/ask', json={"question": "test_question", "session": dummy_token})
    assert resp.status_code == SUCCESS
    assert resp.json == {"answer": test_answer, "session": dummy_token}


@patch("flask_api.save_audiofile")
@patch("flask_api.create_filename", return_value="test_filename")
@patch("flask_api.WakeWordValidator")
@patch("flask_api.WakeWordFormatter")
@patch("flask_api.db")
def test_new_data_wakeword(mock_db, mock_formatter, mock_validator, mock_create_filename, mock_save_audiofile, client):
    mock_formatter_instance = Mock()
    mock_formatter_instance.format.return_value = {"filename": "dummy"}
    mock_formatter.return_value = mock_formatter_instance

    resp = client.post(
        '/new_data/wakeword',
        data={"test": "foo", 'wav_file': (BytesIO(b'dummyText'), 'dummyfile.txt')})

    # Verify that db client was told to save data, and that the newly generated filename was returned
    mock_db.save_audio_sample_meta_data.assert_called_once()
    assert resp.data == b"test_filename"


@patch("flask_api.WakeWordValidator")
def test_new_data_wakeword_validator_issues(mock_validator, client):
    mock_validator_instance = Mock()
    mock_validator_instance.fix.side_effect = WakeWordValidatorError(TEST_ERROR)
    mock_validator.return_value = mock_validator_instance

    # Verify that the client will catch and throw an error if the validator fails
    resp = client.post('/new_data/wakeword', data={"dummy1": "dummy2"})
    assert resp.status_code == BAD_REQUEST
    assert resp.data == TEST_ERROR.encode()


@patch("flask_api.save_audiofile")
@patch("flask_api.create_filename", return_value="test_filename")
@patch("flask_api.WakeWordValidator")
@patch("flask_api.WakeWordFormatter")
@patch("flask_api.db")
def test_new_data_wakeword_db_error(mock_db, mock_formatter, mock_validator, mock_create_filename,
                                    mock_save_audiofile, client):
    mock_formatter_instance = Mock()
    mock_formatter_instance.format.return_value = {"filename": "dummy"}
    mock_formatter.return_value = mock_formatter_instance

    # Verify that the client will catch and throw an error for specific exceptions
    mock_db.save_audio_sample_meta_data.side_effect = BadDictionaryKeyError(TEST_ERROR)
    resp = client.post(
        '/new_data/wakeword',
        data={"test": "foo", 'wav_file': (BytesIO(b'dummyText'), 'dummyfile.txt')})
    assert resp.status_code == BAD_REQUEST
    assert resp.data == TEST_ERROR.encode()

    mock_db.save_audio_sample_meta_data.side_effect = BadDictionaryValueError(TEST_ERROR)
    resp = client.post(
        '/new_data/wakeword',
        data={"test": "foo", 'wav_file': (BytesIO(b'dummyText'), 'dummyfile.txt')})
    assert resp.status_code == BAD_REQUEST
    assert resp.data == TEST_ERROR.encode()

    mock_db.save_audio_sample_meta_data.side_effect = NimbusDatabaseError(TEST_ERROR)
    resp = client.post(
        '/new_data/wakeword',
        data={"test": "foo", 'wav_file': (BytesIO(b'dummyText'), 'dummyfile.txt')})
    assert resp.status_code == BAD_REQUEST
    assert resp.data == TEST_ERROR.encode()
