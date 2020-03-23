import pytest

from database_wrapper import *
from mock import patch, Mock
from .TestEntity import TestEntity


TEST_ENTITY_DATA_DICT = {
    "value_one": "test1",
    "value_two": "test2",
    "value_three": "test3"
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
    "filename": "ww_q_serious-fake_m_doe_jj_1577077883_guest.wav"
}


@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_validate_input_keys(mock_create_session, mock_create_engine):
    test_db = NimbusMySQLAlchemy()
    test_db.validate_input_keys(TEST_ENTITY_DATA_DICT, TEST_ENTITY_DATA_DICT.keys())


@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_validate_input_keys_no_input(mock_create_session, mock_create_engine):
    test_db = NimbusMySQLAlchemy
    with pytest.raises(BadDictionaryKeyError):
        test_db.validate_input_keys({}, [])


@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_validate_input_keys_extra_keys(mock_create_session, mock_create_engine):
    test_db = NimbusMySQLAlchemy
    extra_key_dict = dict(TEST_ENTITY_DATA_DICT)
    extra_key_dict["value_extra"] = "test4"
    with pytest.raises(BadDictionaryKeyError):
        test_db.validate_input_keys(extra_key_dict, TEST_ENTITY_DATA_DICT.keys())


@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_validate_input_keys_missing_keys(mock_create_session, mock_create_engine):
    test_db = NimbusMySQLAlchemy
    missing_key_dict = {"value_one": "test1"}
    with pytest.raises(BadDictionaryKeyError):
        test_db.validate_input_keys(missing_key_dict, TEST_ENTITY_DATA_DICT.keys())


@patch.object(NimbusMySQLAlchemy, "validate_and_format_entity_data")
@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_insert_entity(mock_create_session, mock_create_engine, mock_validate):
    # Setup mocks and test_db instance
    mock_validate.return_value = TEST_ENTITY_DATA_DICT
    test_db = NimbusMySQLAlchemy()
    test_db.session = Mock()

    # Insert entity and assert that add/commit were called
    test_db.insert_entity(TestEntity, TEST_ENTITY_DATA_DICT)
    test_db.session.add.assert_called_once()
    test_db.session.commit.assert_called_once()

    # Assert that the entity inserted was populated with the right fields
    entity = test_db.session.add.call_args.args[0]
    for field in list(TEST_ENTITY_DATA_DICT.keys()):
        assert getattr(entity, field) is TEST_ENTITY_DATA_DICT[field]


@patch.object(NimbusMySQLAlchemy, "validate_and_format_entity_data")
@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_update_entity_no_match(mock_create_session, mock_create_engine, mock_validate):
    # Setup mocks and test_db instance
    mock_validate.return_value = TEST_ENTITY_DATA_DICT
    mock_session = Mock()
    mock_query = Mock()

    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None

    test_db = NimbusMySQLAlchemy()
    test_db.session = mock_session

    # Insert entity and assert that add/commit were called
    test_db.update_entity(TestEntity, TEST_ENTITY_DATA_DICT, ["value_one"])
    test_db.session.add.assert_called_once()
    test_db.session.commit.assert_called_once()

    # Assert that the entity inserted was populated with the right fields
    entity = test_db.session.add.call_args.args[0]
    for field in list(TEST_ENTITY_DATA_DICT.keys()):
        assert getattr(entity, field) is TEST_ENTITY_DATA_DICT[field]


@patch.object(NimbusMySQLAlchemy, "validate_and_format_entity_data")
@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_update_entity_match(mock_create_session, mock_create_engine, mock_validate):
    # Setup mocks and test_db instance
    mock_validate.return_value = TEST_ENTITY_DATA_DICT
    mock_session = Mock()
    mock_query = Mock()

    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = TestEntity

    test_db = NimbusMySQLAlchemy()
    test_db.session = mock_session

    # Insert entity and assert that add/commit were called
    test_db.update_entity(TestEntity, TEST_ENTITY_DATA_DICT, ["value_one"])
    test_db.session.add.assert_called_once()
    test_db.session.commit.assert_called_once()

    # Assert that the entity inserted was populated with the right fields
    entity = test_db.session.add.call_args.args[0]
    for field in list(TEST_ENTITY_DATA_DICT.keys()):
        assert getattr(entity, field) is TEST_ENTITY_DATA_DICT[field]


@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_update_entity_no_filter_fields_error(mock_create_session, mock_create_engine):
    test_db = NimbusMySQLAlchemy()
    with pytest.raises(RuntimeError, match="filter"):
        test_db.update_entity(TestEntity, TEST_ENTITY_DATA_DICT, [])


@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_invalid_entity_type(mock_create_session, mock_create_engine):
    test_db = NimbusMySQLAlchemy()
    with pytest.raises(KeyError):
        test_db.insert_entity(TestEntity, TEST_ENTITY_DATA_DICT)
    with pytest.raises(KeyError):
        test_db.update_entity(TestEntity, TEST_ENTITY_DATA_DICT, ["test"])


@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_format_audio_sample_meta_data_dict(mock_create_session, mock_create_engine):
    test_db = NimbusMySQLAlchemy()
    test_db.format_audio_sample_meta_data_dict(dict(TEST_AUDIO_SAMPLE_META_DATA_DATA_DICT))


@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_format_audio_sample_meta_data_dict_bad_input(mock_create_session, mock_create_engine):
    test_db = NimbusMySQLAlchemy()
    invalid_is_wake_word = dict(TEST_AUDIO_SAMPLE_META_DATA_DATA_DICT)
    invalid_is_wake_word["isWakeWord"] = "test"
    invalid_noise_level = dict(TEST_AUDIO_SAMPLE_META_DATA_DATA_DICT)
    invalid_noise_level["noiseLevel"] = "test"

    with pytest.raises(BadDictionaryValueError):
        test_db.format_audio_sample_meta_data_dict(invalid_is_wake_word)
    with pytest.raises(BadDictionaryValueError):
        test_db.format_audio_sample_meta_data_dict(invalid_noise_level)
    
