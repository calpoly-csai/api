#!/usr/bin/env python3
"""A wrapper module for the Nimbus data storage systems.

This module includes various adapters for interfacing with
different databases and storage locations.

    Typical usage example:

    db = NimbusMySQL(config_file="config.json")
    ents = db.get_entities()
"""
import json
import csv
from abc import ABC, abstractmethod
from typing import List, Optional, Union


import sqlalchemy
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from Entity.AudioSampleMetaData import AudioSampleMetaData, NoiseLevel
from Entity.Calendars import Calendars
from Entity.Courses import Courses
from Entity.Locations import Locations
from Entity.QuestionAnswerPair import QuestionAnswerPair
from Entity.Professors import Professors, ProfessorsProperties
from Entity.Clubs import Clubs
from Entity.Sections import Sections, SectionType

from fuzzywuzzy import fuzz


GREEN_COLOR_CODE = "\033[92m"
YELLOW_COLOR_CODE = "\033[93m"
PURPLE_COLOR_CODE = "\033[95m"
CYAN_COLOR_CODE = "\033[96m"
RESET_COLOR_CODE = "\033[00m"

UNION_ENTITIES = Union[
    AudioSampleMetaData, Calendars, Courses, Professors, QuestionAnswerPair
]
UNION_PROPERTIES = Union[ProfessorsProperties]

default_tag_column_dict = {
    Calendars: {"date"},
    Courses: {"courseName", "courseNum", "dept"},
    Locations: {"building_number", "name"},
    Professors: {"firstName", "lastName"},
    Clubs: {"club_name"},
    Sections: {"section_name"}
}

EXPECTED_KEYS_BY_ENTITY = {
    AudioSampleMetaData : [
        "is_wake_word",
        "first_name",
        "last_name",
        "gender",
        "noise_level",
        "location",
        "tone",
        "timestamp",
        "username",
        "filename",
    ],
    Clubs : [
        "club_name",
        "types",
        "desc",
        "contact_email",
        "contact_email_2",
        "contact_person",
        "contact_phone",
        "box",
        "advisor",
        "affiliation"
    ],
    Locations : [
        "building_number",
        "name",
        "longitude",
        "latitude"
    ],
    Sections : [
        "section_name",
        "instructor",
        "alias",
        "title",
        "phone",
        "office",
        "type",
        "days",
        "start",
        "end",
        "location",
        "department"
    ]
}

class BadDictionaryKeyError(Exception):
    """Raised when the given JSON/dict is missing some required fields.

    Attributes:
        message: an explanation of what fields are missing.
    """

    def __init__(self, message: str):
        self.message = message


class BadDictionaryValueError(Exception):
    """Raised when the given JSON/dict has unexpected wake

    Attributes:
        message: an explanation.
    """

    def __init__(self, message: str):
        self.message = message


class NimbusDatabaseError(Exception):
    """Raised when we have a database querying problem.

    Attributes:
        message: an explanation of the data querying problem.
    """

    def __init__(self, message: str):
        self.message = message


class UnsupportedDatabaseError(Exception):
    """Raised when operation tries to connect to an unsupported database type.

    Attributes:
        message: an explanation of why the expected database is unsupported.
    """

    def __init__(self, message: str):
        self.message = message


class BadConfigFileError(Exception):
    """Raised when the config.json file is badly formatter (e.g missing field).

    Attributes:
        message: an explanation.
    """

    def __init__(self, message: str):
        self.message = message


"""
utilities.py
"""


def get_current_time():
    """
    Useful for answering questions like "Is prof availible now/tomorrow?"
    """
    pass


class NimbusDatabase(ABC):
    """
    An abstract class for interacting with the Nimbus database.
    Concrete subclasses, such as NimbusMySQL,
    should implement these operations such as `connect`
    """

    def __init__(self, config_file: str = "config.json") -> None:
        """
        Inits Nimbus Database using the hostname, username, password
        found inside the config_file.
        """
        pass

    @abstractmethod
    def get_property_from_entity(
        self,
        prop: List[str],
        entity: str,
        condition_field: Optional[str] = None,
        condition_value: Optional[str] = None,
    ) -> List[str]:
        """A high-order function to get properties from objects in the database.

        Example:
        >>> db = NimbusDatabase("config.json")
        >>> db.get_property_from_entity(["firstName", "lastName"],
                                        "Professors")
        [("Foaad", "Khosmood"), ("John", "Clements"), ...]

        >>> db.get_property_from_entity(["firstName", "lastName"],
                                        "Professors", "firstName", "Foaad")
        [("Foaad", "Khosmood")]

        Args:
            entity: a string representing a table in the database.
            prop: string(s) representing a field in the given table.
            condition_field: (optional) string representing the column name.
            condition_value: (optional) string representing the cell value.

        Returns:
            The list of prop of the entity (e.g. firstName of Professor)
        """
        pass

    @abstractmethod
    def get_property_from_related_entities(
        self,
        prop: List[str],
        entity1: str,
        entity2: str,
        key1: str,
        key2: Optional[str] = None,
        condition_field: Optional[str] = None,
        condition_value: Optional[str] = None,
    ) -> List[str]:
        """A higher-order function to ????

        Example:
        >>> db = NimbusDatabase("config.json")
        >>> db.get_property_from_related_entities(
                        ["firstName", "lastName", "ohRoom"],
                        "Professors", "OfficeHours", "professorId")
        [("Foaad", "Khosmood", "14-213"), ("John", "Clements", "14-210"), ...]

        >>> db.get_property_from_related_entities(
                        ["firstName", "lastName"],
                        "Professors", "OfficeHours",
                        "professorId", "firstName", "Foaad")
        [("Foaad", "Khosmood", "14-213")]

        Args:
            entity: TODO
            prop: TODO

        Returns:
            TODO
        """
        pass

    @abstractmethod
    def get_entities(self) -> str:
        pass

    @abstractmethod
    def get_fields_of_entity(self, entity1: str) -> str:
        """
        TODO:
        given an entity,
        return all the field names of that table in the database.
        """
        pass

    @abstractmethod
    def get_unique(self, entity) -> str:
        pass

    @abstractmethod
    def get_bitcount(self, entity) -> str:
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Simple Implementation Example:
        ```
        self.connection.close()
        super().close()
        ```
        """
        print("database connection was closed.")
        pass

    def __del__(self) -> None:
        """
        This method can make sure that the database connection is closed
        before garbage references are collected.

        There are reasons to not use `__del__`:
        https://stackoverflow.com/q/1481488

        Example:
            >>> import database_wrapper
            >>> db = database_wrapper.NimbusMySQL()
            >>> del db
            database object is being garbage collected...
            database connection was closed.
        """
        print("database object is being garbage collected...")
        self.close()
        return


def raises_database_error(func):
    """A Python decorator for mapping to NimbusDatabaseError

    Resources:
        https://realpython.com/primer-on-python-decorators/#simple-decorators
        https://docs.python.org/3/library/exceptions.html
    """

    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except sqlalchemy.exc.DataError as e:
            # TODO: consider security tradeoff of displaying
            #       internal server errors
            #       versus development time (being able to see errors quickly)
            # HINT: security always wins, so try to raise a smaller message
            raise NimbusDatabaseError(str(e.args)) from e
        except Exception as e:
            # TODO: consider security tradeoff of displaying
            #       internal server errors
            #       versus development time (being able to see errors quickly)
            # HINT: security always wins, so try to catch the EXACT exception
            raise e

    return wrapper


class NimbusMySQLAlchemy:  # NimbusMySQLAlchemy(NimbusDatabase):
    """
    """

    def __init__(self, config_file: str = "config.json") -> None:
        self.engine = None  # gets set according to config_file
        self.Clubs = Clubs
        self.Sections = Sections
        self.Calendars = Calendars
        self.Courses = Courses
        self.Professors = Professors
        self.AudioSampleMetaData = AudioSampleMetaData
        self.Locations = Locations
        self.QuestionAnswerPair = QuestionAnswerPair

        with open(config_file) as json_data_file:
            config = json.load(json_data_file)

        if config.get("mysql", False):
            mysql_config = config["mysql"]
            RDBMS = "mysql"
            PIP_PACKAGE = "mysqlconnector"
            SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}".format(
                RDBMS,
                PIP_PACKAGE,
                mysql_config["user"],
                mysql_config["password"],
                mysql_config["host"],
                mysql_config["port"],
                mysql_config["database"],
            )
            self.engine = create_engine(SQLALCHEMY_DATABASE_URI)

            if self.engine is None:
                raise BadConfigFileError("failed to connect to MySQL")
        else:
            msg = "config.json is missing {} field.".format("mysql")
            raise BadConfigFileError(msg)

        self.inspector = inspect(self.engine)
        self._create_database_session()
        print("initialized NimbusMySQLAlchemy")

    @staticmethod
    def validate_input_keys(input_data: dict, expected_keys: set):
        if len(input_data) == 0:
            msg = "expected: {} but got: {}"
            msg = msg.format(expected_keys, set(input_data.keys()))
            raise BadDictionaryKeyError(msg)

        # assert that the formatted_data does not have extra keys
        for k in input_data:
            if k not in expected_keys:
                msg = "expected: {} but got: {}"
                msg = msg.format(expected_keys, set(input_data.keys()))
                raise BadDictionaryKeyError(msg)

        # assert that the keys_i_care_about are in formatted_data
        for k in expected_keys:
            if k not in input_data:
                msg = "expected: {} but got: {}"
                msg = msg.format(expected_keys, set(input_data.keys()))
                raise BadDictionaryKeyError(msg)

    def _create_all_tables(self):
        def __safe_create(SQLAlchemy_object):
            table_name = SQLAlchemy_object.__tablename__
            print(f"creating {table_name}...")
            if table_name in self.inspector.get_table_names():
                print(f"<{table_name}> already exists")
                return
            SQLAlchemy_object.__table__.create(bind=self.engine)
            print(f"<{table_name}> created")
            return

        __safe_create(self.Clubs)
        __safe_create(self.Sections)
        __safe_create(self.Calendars)
        __safe_create(self.Courses)
        __safe_create(self.Professors)
        __safe_create(self.AudioSampleMetaData)
        __safe_create(self.Locations)
        __safe_create(self.QuestionAnswerPair)

    def _create_database_session(self) -> None:
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        print("initialized database session")

    def get_all_qa_pairs(self):

        qa_entity = QuestionAnswerPair

        query_session = self.session.query(qa_entity.question_format, qa_entity.answer_format)
        result = query_session.all()

        return result

    def return_qa_pair_csv(self):
        data = self.get_all_qa_pairs()

        with open('qa_pair.csv', 'w') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(['question_format', 'answer_format'])
            for row in data:
                csv_out.writerow(row)

    def partial_fuzzy_match(self, tag_value, identifier):
        return fuzz.partial_ratio(tag_value, identifier)

    def full_fuzzy_match(self, tag_value: str, identifier: str) -> int:
        return fuzz.ratio(tag_value, identifier)

    def get_property_from_entity(
        self, prop: str, entity: UNION_ENTITIES, identifier: str,
        tag_column_map: dict = default_tag_column_dict
    ) -> str:
        """
        This function implements the abstractmethod to get a column of values
        from a NimbusDatabase entity.

        Example:
        >>> db = NimbusMySQLAlchemy()
        >>> db.get_property_from_entity(
            prop="email",
            entity=Entity.Professors.Professors,
            entity_string="Khosmood",
        )
        >>> ["foaad@calpoly.edu"]

        Args:
            prop: the relevant property value to retrieve from matching entities
            entity: the type of entity we want to get the property from
            identifier: a string that identifies the entity in some way (i.e., a professor's name)
            tag_column_map: a dictionary mapping entity types to columns that identify the entities
                ex:
                {Professors: {"firstName", "lastName"}}

        Returns:
            A list of values for `prop`,
            such that the `entity` matches `identifier`.
        """

        MATCH_THRESHOLD = 80

        # TODO: be smart by check only Professor.firstName Professor.lastName
        # TODO: only check Course.dept, Course.course_num, Course.course_name
        tag_props = []
        for k in entity.__dict__:
            if k in tag_column_map[entity]:
                tag_props.append(k)

        results = []
        query_obj = self.session.query(entity)
        for row in query_obj.all():
            total_similarity = 0
            tags = []
            for tag_prop in tag_props:
                total_similarity += self.full_fuzzy_match(str(row.__dict__[tag_prop]), identifier)
                tags.append(str(row.__dict__[tag_prop]))

            if total_similarity > MATCH_THRESHOLD:
                results.append((total_similarity, tags, str(row.__dict__[prop])))

        if len(results) < 1:
            return None

        sorted_results = sorted(results, key=lambda pair: pair[0])
        return sorted_results[-1][2]

    def get_course_properties(
        self, department: str, course_num: Union[str, int]
    ) -> List[Courses]:
        return (
            # sqlalchemy doesn't use type annotations
            # and thus does not necessarily promise a List[Courses]
            # even so we can expect .all() to return a list
            # so long as there is no error in the MySQL syntax
            self.session.query(Courses)
            .filter(Courses.dept == department, Courses.courseNum == course_num)
            .all()
        )

    def validate_and_format_entity_data(self, entity_type, data_dict: dict):
        """
        Validates that the data_dict's fields matches the entity_type's fields, and formats the data_dict
        if necessary.

        data_dict should be a dictionary of field names and values, looking like:
        {
            "fieldOne": valueOne,
            "..."  : ...
        }

        Raises:
            BadDictionaryKeyError - ...
            BadDictionaryValueError - ...

        Returns:
            The formatted data_dict if there was formatted run, otherwise an unmodified data_dict
        """

        format_method_by_entity = {
            AudioSampleMetaData : self.format_audio_sample_meta_data_dict
        }

        # Format data (if needed), and validate data
        if entity_type in format_method_by_entity:
            data_dict = format_method_by_entity[entity_type](data_dict)

        self.validate_input_keys(data_dict, EXPECTED_KEYS_BY_ENTITY[entity_type])
        return data_dict


    def insert_entity(self, entity_type, data_dict: dict) -> bool:
        """
        Inserts an entity into the database. The keys of data_dict should follow camelCase
        so they can be translated into snake_case.

        data_dict should be a dictionary of field names and values, looking like:
        {
            "fieldOne": valueOne,
            "..."  : ...
        }

        Raises:
            BadDictionaryKeyError - ...
            BadDictionaryValueError - ...

        Returns:
            True if all is good, else False
        """

        # Validate and format entity data
        formatted_data = self.validate_and_format_entity_data(entity_type, data_dict)

        # Grab the entity class attributes and initialize entity
        entity_attributes = entity_type.__dict__
        entity = entity_type()

        # Logging...
        print("{}Inserting into {}...{}".format(
              CYAN_COLOR_CODE, entity_attributes['__tablename__'], RESET_COLOR_CODE))

        # Grab the entity class fields by cleaning the attributes dictionary 
        # and discard anything with underscores in the front or back
        # Note: Make sure you don't label any important data fields with underscores in the front or back!
        entity_fields = dict(filter(lambda i: not (i[0][0] == '_' or i[0][-1] == '_'), 
                                    entity_attributes.items()))

        # Ignore the first field, since it's assumed to be a primary key
        # Populate the entity with values from formatted_data
        for entity_field in list(entity_fields.keys())[1:]:
            setattr(entity, entity_field, formatted_data[entity_field])

        # Perform the INSERT
        print("Saving to database: {}...".format(entity))
        self.session.add(entity)
        self.session.commit()
        print("{}Saved!\n{}".format(GREEN_COLOR_CODE, RESET_COLOR_CODE))

        return True

    def update_entity(self, entity_type, data_dict: dict, filter_fields: list) -> bool:
        """
        Updates an entity in the database. The keys of data_dict should follow camelCase
        so they can be translated into snake_case.

        data_dict should be a dictionary of field names and values, looking like:
        {
            "fieldOne": valueOne,
            "..."  : ...
        }

        filter_fields is a list of variable names (strings) to match for when running an 
        update query. If not provided, raises an error since it's not an update.

        ex: passing in filter_fields=["name", "title"] will check for an existing entity that has the
        same 'name' and 'title' values in the data_dict.

        Raises:
            RuntimeError - ...
            BadDictionaryKeyError - ...
            BadDictionaryValueError - ...

        Returns:
            True if all is good, else False
        """

        # If we're not filtering for anything, we shouldn't be calling update_entity
        if len(filter_fields) == 0:
            raise RuntimeError("update_entity for {} requires filter_fields list to filter by.".format(entity_type))

        # Validate and format entity data
        formatted_data = self.validate_and_format_entity_data(entity_type, data_dict)

        # Grab the entity class attributes and initialize entity to None
        entity_attributes = entity_type.__dict__

        # Run a SELECT query to see if an entity that matches the values under the fields in the filter_fields list exists
        query = self.session.query(entity_type)
        for field in filter_fields:
            query = query.filter(getattr(entity_type, field) == formatted_data[field])
        entity = query.first()

        if entity:
            print("{}Updating {} in {}...{}".format(
                  YELLOW_COLOR_CODE, entity, entity_attributes['__tablename__'], RESET_COLOR_CODE))
        else:
            entity = entity_type()
            print("{}Matching Entity not found - Inserting {} in {}...{}".format(
                  YELLOW_COLOR_CODE, entity, entity_attributes['__tablename__'], RESET_COLOR_CODE))

        # Grab the entity class fields by cleaning the attributes dictionary - 
        # discard anything with underscores in the front or back
        # Note: Make sure you don't label any important data fields with underscores in the front or back!
        entity_fields = dict(filter(lambda i: not (i[0][0] == '_' or i[0][-1] == '_'), 
                                    entity_attributes.items()))

        # Ignore the first field, since it's assumed to be a primary key
        # Populate the entity with values from formatted_data
        for entity_field in list(entity_fields.keys())[1:]:
            setattr(entity, entity_field, formatted_data[entity_field])

        # Perform the actual UPDATE/INSERT
        print("Saving to database: {}...".format(entity))
        self.session.add(entity)
        self.session.commit()
        print("{}Saved!\n{}".format(GREEN_COLOR_CODE, RESET_COLOR_CODE))

        return True

    def format_audio_sample_meta_data_dict(self, data_dict: dict) -> dict:
        """
        raw_data_dict at this point looks like:
        {
            "isWakeWord": True,
            "firstName": "jj",
            "lastName": "doe",
            "gender": "f",
            "noiseLevel": "q",
            "location": "here",
            "tone": "serious-but-not-really",
            "timestamp": 1577077883,
            "username": "guest",
            "filename": "ww_q_serious-but-not-really_here_m_doe_jj_1577077883_guest.wav"  # noqa because too hard.
        }

        Raises:
            BadDictionaryValueError - ...

        Returns:
            A new, formatted data dictionary
        """

        is_wake_word_by_label = {
            "ww" : True,
            "nww" : False,
            True : True,
            False : False
        }

        noise_level_by_label = {
            "q" : NoiseLevel.quiet,
            "quiet" : NoiseLevel.quiet,
            "m" : NoiseLevel.medium,
            "medium" : NoiseLevel.medium,
            "l" : NoiseLevel.loud,
            "loud" : NoiseLevel.loud
        }

        data_dict["first_name"] = data_dict.pop("firstName")
        data_dict["last_name"] = data_dict.pop("lastName")

        if data_dict["isWakeWord"] in is_wake_word_by_label:
            data_dict["is_wake_word"] = is_wake_word_by_label[data_dict.pop("isWakeWord")]
        else:
            msg = "unexpected values for isWakeWord\n"
            msg += "expected 'ww' or True or 'nww' or False but got '{}'"
            msg = msg.format(raw_data_dict["isWakeWord"])
            raise BadDictionaryValueError(msg)

        if data_dict["noiseLevel"] in noise_level_by_label:
            data_dict["noise_level"] = noise_level_by_label[data_dict.pop("noiseLevel")]
        else:
            msg = "unexpected values for noiseLevel\n"
            msg += "expected 'q' or 'm' or 'l' but got '{}'"
            msg = msg.format(data_dict["noiseLevel"])
            raise BadDictionaryValueError(msg)

        return data_dict

    def _execute(self, query: str):
        return self.engine.execute(query)

    def __del__(self):
        print("NimbusMySQLAlchemy closed")


if __name__ == "__main__":
    db = NimbusMySQLAlchemy()
    db._create_all_tables()

    data = {
        "isWakeWord": True,
        "firstName": "jj",
        "lastName": "doe",
        "gender": "f",
        "noiseLevel": "q",
        "location": "here",
        "tone": "serious-but-not-really",
        "timestamp": 1577077883,
        "username": "guest",
        "filename": "ww_q_serious-but-not-really_here_m_doe_jj_1577077883_guest.wav"  # noqa because too hard.
    }

    db.insert_entity(AudioSampleMetaData, data)

    data = {
        "building_number": 1,
        "name": "Administration",
        "longitude": -120.658561,
        "latitude": 35.300960
    }

    db.update_entity(Locations, data, ['building_number'])

    data = {
        "club_name": "Cal Poly Computer Science and Artificial Intelligence",
        "types": "Academic, Special Interest",
        "desc": "The Computer Science and Artificial Intelligence club provides...",
        "contact_email": "maikens@calpoly.edu",
        "contact_email_2": "fkurfess@calpoly.edu",
        "contact_person": "Miles Aikens",
        "contact_phone": "7349723564",
        "box": "89",
        "advisor": "Franz Kurfess",
        "affiliation": "None"
    }

    db.insert_entity(Clubs, data)

    data = {
        "section_name": "CSC 480_06",
        "instructor": "Kauffman, Daniel Alexander",
        "alias": "dkauffma",
        "title": "Instructor AY",
        "phone": "+1.805.756.2824",
        "office": "014-0254A",
        "type": SectionType.lab,
        "days": set({'M', 'W', 'F'}),
        "start": "10:10 AM",
        "end": "11:00 AM",
        "location": "014-0257",
        "department": "CENG-Computer Science & Software Engineering"
    }

    db.insert_entity(Sections, data)
    
