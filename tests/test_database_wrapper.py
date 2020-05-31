import json
import os
import pytest

from database_wrapper import (
    NimbusMySQLAlchemy,
    BadDictionaryKeyError,
    BadDictionaryValueError,
    InvalidOperationOnView,
    NimbusDatabaseError,
    UnsupportedDatabaseError,
    BadConfigFileError,
)
from mock import patch, Mock
from .MockEntity import MockEntity
from .MockViewEntity import MockViewEntity


ENTITY_TYPES = [
    "AudioSampleMetaData",
    "Calendars",
    "Courses",
    "Locations",
    "QuestionAnswerPair",
    "Professors",
    "Clubs",
    "Sections",
]

MOCK_ENTITY_DATA_DICT = {
    "value_one": "test1",
    "value_two": "test2",
    "value_three": "test3",
}

TEST_AUDIO_SAMPLE_META_DATA_DATA_DICT = {
    "isWakeWord": True,
    "firstName": "jj",
    "lastName": "doe",
    "gender": "f",
    "noiseLevel": "q",
    "location": "here",
    "tone": "serious-but-not-really",
    "timestamp": 1577077883,
    "username": "guest",
    "audio_file_id": "OZ234FSDWER5GDF234F4G5",
    "script": "Nimbus",
    "emphasis": "us"
}

TEST_CONFIG_FILENAME = "testConfig.json"
TEST_CONFIG_DICT = {
    "mysql": {
        "host": "testHost",
        "port": "testPort",
        "user": "testUser",
        "password": "testPassword",
        "database": "testDatabase",
    },
}

RDBMS = "mysql"
PIP_PACKAGE = "mysqlconnector"
SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}".format(
    RDBMS,
    PIP_PACKAGE,
    TEST_CONFIG_DICT["mysql"]["user"],
    TEST_CONFIG_DICT["mysql"]["password"],
    TEST_CONFIG_DICT["mysql"]["host"],
    TEST_CONFIG_DICT["mysql"]["port"],
    TEST_CONFIG_DICT["mysql"]["database"],
)


@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_validate_input_keys(mock_create_engine):
    test_db = NimbusMySQLAlchemy()
    test_db.validate_input_keys(MOCK_ENTITY_DATA_DICT, MOCK_ENTITY_DATA_DICT.keys())


@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_validate_input_keys_no_input(mock_create_engine):
    test_db = NimbusMySQLAlchemy
    with pytest.raises(BadDictionaryKeyError):
        test_db.validate_input_keys({}, [])


@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_validate_input_keys_extra_keys(mock_create_engine):
    test_db = NimbusMySQLAlchemy
    extra_key_dict = dict(MOCK_ENTITY_DATA_DICT)
    extra_key_dict["value_extra"] = "test4"
    with pytest.raises(BadDictionaryKeyError):
        test_db.validate_input_keys(extra_key_dict, MOCK_ENTITY_DATA_DICT.keys())


@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_validate_input_keys_missing_keys(mock_create_engine):
    test_db = NimbusMySQLAlchemy
    missing_key_dict = {"value_one": "test1"}
    with pytest.raises(BadDictionaryKeyError):
        test_db.validate_input_keys(missing_key_dict, MOCK_ENTITY_DATA_DICT.keys())


@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_create_all_tables(mock_create_engine):
    test_db = NimbusMySQLAlchemy()

    for entity_type in ENTITY_TYPES:
        mock_entity = Mock()
        mock_entity.__tablename__ = entity_type
        mock_entity.__table__ = Mock()
        mock_entity.__table__.create.return_value = None
        setattr(test_db, entity_type, mock_entity)

    test_db._create_all_tables()

    # Verify that each Entity had .create() called on it once.
    for entity_type in ENTITY_TYPES:
        getattr(test_db, entity_type).__table__.create.assert_called_once()


@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_create_all_tables_already_exists(mock_create_engine):
    mock_inspector = Mock()
    mock_inspector.get_table_names.return_value = ENTITY_TYPES

    test_db = NimbusMySQLAlchemy()
    test_db.inspector = mock_inspector

    for entity_type in ENTITY_TYPES:
        mock_entity = Mock()
        mock_entity.__tablename__ = entity_type
        mock_entity.__table__ = Mock()
        setattr(test_db, entity_type, mock_entity)

    test_db._create_all_tables()

    # Verify that each Entity did not have .create() called on it
    for entity_type in ENTITY_TYPES:
        assert not getattr(test_db, entity_type).__table__.create.called


@patch.object(
    NimbusMySQLAlchemy,
    "validate_and_format_entity_data",
    return_value=MOCK_ENTITY_DATA_DICT,
)
@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_insert_entity(mock_create_engine, mock_validate):
    # Setup mocks and test_db instance
    test_db = NimbusMySQLAlchemy()
    test_db.session = Mock()

    # Insert entity and assert that add/commit were called
    test_db.insert_entity(MockEntity, MOCK_ENTITY_DATA_DICT)
    test_db.session.add.assert_called_once()
    test_db.session.commit.assert_called_once()

    # Assert that the entity inserted was populated with the right fields
    entity = test_db.session.add.call_args.args[0]
    for field in list(MOCK_ENTITY_DATA_DICT.keys()):
        assert getattr(entity, field) is MOCK_ENTITY_DATA_DICT[field]


@patch.object(
    NimbusMySQLAlchemy,
    "validate_and_format_entity_data",
    return_value=MOCK_ENTITY_DATA_DICT,
)
@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_update_entity_no_match(mock_create_engine, mock_validate):
    # Setup mocks and test_db instance
    mock_session = Mock()
    mock_query = Mock()

    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    test_db = NimbusMySQLAlchemy()
    test_db.session = mock_session

    # Insert entity and assert that add/commit were called
    test_db.update_entity(MockEntity, MOCK_ENTITY_DATA_DICT, ["value_one"])
    test_db.session.add.assert_called_once()
    test_db.session.commit.assert_called_once()

    # Assert that the entity inserted was populated with the right fields
    entity = test_db.session.add.call_args.args[0]
    for field in list(MOCK_ENTITY_DATA_DICT.keys()):
        assert getattr(entity, field) is MOCK_ENTITY_DATA_DICT[field]


@patch.object(
    NimbusMySQLAlchemy,
    "validate_and_format_entity_data",
    return_value=MOCK_ENTITY_DATA_DICT,
)
@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_update_entity_match(mock_create_engine, mock_validate):
    # Setup mocks and test_db instance
    mock_session = Mock()
    mock_query = Mock()

    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = MockEntity

    test_db = NimbusMySQLAlchemy()
    test_db.session = mock_session

    # Insert entity and assert that add/commit were called
    test_db.update_entity(MockEntity, MOCK_ENTITY_DATA_DICT, ["value_one"])
    test_db.session.add.assert_called_once()
    test_db.session.commit.assert_called_once()

    # Assert that the entity inserted was populated with the right fields
    entity = test_db.session.add.call_args.args[0]
    for field in list(MOCK_ENTITY_DATA_DICT.keys()):
        assert getattr(entity, field) is MOCK_ENTITY_DATA_DICT[field]


@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_update_entity_no_filter_fields_error(mock_create_engine):
    test_db = NimbusMySQLAlchemy()
    with pytest.raises(RuntimeError, match="filter"):
        test_db.update_entity(MockEntity, MOCK_ENTITY_DATA_DICT, [])


@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_invalid_entity_type(mock_create_engine):
    test_db = NimbusMySQLAlchemy()
    with pytest.raises(KeyError):
        test_db.insert_entity(MockEntity, MOCK_ENTITY_DATA_DICT)
    with pytest.raises(KeyError):
        test_db.update_entity(MockEntity, MOCK_ENTITY_DATA_DICT, ["test"])


@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_format_audio_sample_meta_data_dict(mock_create_engine):
    test_db = NimbusMySQLAlchemy()
    test_db.format_audio_sample_meta_data_dict(
        dict(TEST_AUDIO_SAMPLE_META_DATA_DATA_DICT)
    )


@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_format_audio_sample_meta_data_dict_bad_input(mock_create_engine):
    test_db = NimbusMySQLAlchemy()
    invalid_is_wake_word = dict(TEST_AUDIO_SAMPLE_META_DATA_DATA_DICT)
    invalid_is_wake_word["isWakeWord"] = "test"
    invalid_noise_level = dict(TEST_AUDIO_SAMPLE_META_DATA_DATA_DICT)
    invalid_noise_level["noiseLevel"] = "test"

    with pytest.raises(BadDictionaryValueError):
        test_db.format_audio_sample_meta_data_dict(invalid_is_wake_word)
    with pytest.raises(BadDictionaryValueError):
        test_db.format_audio_sample_meta_data_dict(invalid_noise_level)


@patch("database_wrapper.create_engine")
def test_create_engine(mock_create_engine):
    mock_engine = Mock()
    mock_create_engine.return_value = mock_engine

    with open("testConfig.json", "w+") as test_config:
        json.dump(TEST_CONFIG_DICT, test_config)

    test_db = NimbusMySQLAlchemy(TEST_CONFIG_FILENAME)
    mock_create_engine.assert_called_once_with(SQLALCHEMY_DATABASE_URI)
    assert test_db.engine is mock_engine

    os.remove(TEST_CONFIG_FILENAME)


@patch("database_wrapper.create_engine", return_value=None)
def test_create_engine_bad_config(mock_create_engine):
    with open(TEST_CONFIG_FILENAME, "w+") as test_config:
        json.dump(TEST_CONFIG_DICT, test_config)

    with pytest.raises(BadConfigFileError, match="failed to connect"):
        test_db = NimbusMySQLAlchemy(TEST_CONFIG_FILENAME)

    os.remove(TEST_CONFIG_FILENAME)


def test_create_engine_missing_field():
    with open(TEST_CONFIG_FILENAME, "w+") as test_config:
        json.dump({}, test_config)

    with pytest.raises(BadConfigFileError, match="missing mysql field"):
        test_db = NimbusMySQLAlchemy(TEST_CONFIG_FILENAME)

    os.remove(TEST_CONFIG_FILENAME)


@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_insert_entity_view_error(mock_create_engine):
    test_db = NimbusMySQLAlchemy()

    with pytest.raises(InvalidOperationOnView):
        test_db.insert_entity(MockViewEntity, {});


@patch.object(NimbusMySQLAlchemy, "_create_engine")
def test_update_entity_view_error(mock_create_engine):
    test_db = NimbusMySQLAlchemy()

    with pytest.raises(InvalidOperationOnView):
        test_db.update_entity(MockViewEntity, {}, []);
