import json
import pytest

import flask_api
from database_wrapper import (NimbusMySQLAlchemy, BadDictionaryKeyError, BadDictionaryValueError,
                              NimbusDatabaseError, UnsupportedDatabaseError, BadConfigFileError)
from mock import patch, Mock
from .MockEntity import MockEntity


BAD_REQUEST = 400
SUCCESS = 200
SERVER_ERROR = 500
TOKEN = "test_token"

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


def test_ask_request_not_json(client):
    resp = client.post('/ask', data="dummy data")
    assert resp.status_code == BAD_REQUEST
    assert resp.data == b'request must be JSON'


def test_ask_no_question(client):
    resp = client.post('/ask', json={})
    assert resp.status_code == BAD_REQUEST
    assert resp.data == b'request body should include the question'


@patch("flask_api.generate_session_token", return_value=TOKEN)
@patch("flask_api.Nimbus")
def test_ask_question(mock_nimbus, mock_generate_session_token, client):
    mock_nimbus_client = Mock()
    mock_nimbus.return_value = mock_nimbus_client
    mock_nimbus_client.answer_question.return_value = "test_answer"

    # Verify that calling ask without a token will return a response with a new token
    resp = client.post('/ask', json={"question": "test_question"})
    assert resp.status_code == SUCCESS
    assert resp.json == {"answer": "test_answer", "session": TOKEN}

    # Verify that calling ask with a token will return a response with the same token
    dummy_token = "dummy_token"
    resp = client.post('/ask', json={"question": "test_question", "session": dummy_token})
    assert resp.status_code == SUCCESS
    assert resp.json == {"answer": "test_answer", "session": dummy_token}