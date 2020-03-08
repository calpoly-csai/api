from mock import patch, Mock
from database_wrapper import *
from .TestEntity import TestEntity


data_dict = {
    "value_one": "test1",
    "value_two": "test2",
    "value_three": "test3"
}


@patch.object(NimbusMySQLAlchemy, "validate_and_format_entity_data")
@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_insert_entity(mock_create_session, mock_create_engine ,mock_validate):
    # Setup mocks and test_db instance
    mock_validate.return_value = data_dict
    test_db = NimbusMySQLAlchemy()
    test_db.session = Mock()

    # Insert entity and assert that add/commit were called
    test_db.insert_entity(TestEntity, data_dict)
    test_db.session.add.assert_called_once()
    test_db.session.commit.assert_called_once()

    # Assert that the entity inserted was populated with the right fields
    entity = test_db.session.add.call_args.args[0]

    for field in list(data_dict.keys()):
        assert getattr(entity, field) is data_dict[field]


@patch.object(NimbusMySQLAlchemy, "validate_and_format_entity_data")
@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_update_entity(mock_create_session, mock_create_engine, mock_validate):
    # Setup mocks and test_db instance
    mock_validate.return_value = data_dict
    test_db = NimbusMySQLAlchemy()
    test_db.session = Mock()

    # Insert entity and assert that add/commit were called
    test_db.update_entity(TestEntity, data_dict, ["value_one"])
    test_db.session.add.assert_called_once()
    test_db.session.commit.assert_called_once()

    # Assert that the entity inserted was populated with the right fields
    entity = test_db.session.add.call_args.args[0]

    for field in list(data_dict.keys()):
        assert getattr(entity, field) is data_dict[field]


@patch.object(NimbusMySQLAlchemy, "_create_engine")
@patch.object(NimbusMySQLAlchemy, "_create_database_session")
def test_update_entity_no_filter_fields_error(mock_create_engine, mock_create_session):
    test_db = NimbusMySQLAlchemy()
    try:
        test_db.update_entity(TestEntity, data_dict, [])
    except RuntimeError as e:
        if "requires filter_fields list" not in str(e):
            raise RuntimeError("Error not raised")
