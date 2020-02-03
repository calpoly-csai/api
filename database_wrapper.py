#!/usr/bin/env python3
"""A wrapper module for the Nimbus data storage systems.

This module includes various adapters for interfacing with
different databases and storage locations.

    Typical usage example:

    db = NimbusMySQL(config_file="config.json")
    ents = db.get_entities()
"""
import json
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pprint import pprint as pp
from typing import List, Optional, Union

import mysql.connector
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, Table,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

import Entity
from Entity.Courses import Courses
from Entity.AudioSampleMetaData import AudioSampleMetaData, NoiseLevel
from sqlalchemy import inspect


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

    def __init__(self, config_file: str = 'config.json') -> None:
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
            condition_value: Optional[str] = None) -> List[str]:
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
            condition_value: Optional[str] = None) -> List[str]:
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


class NimbusMySQLAlchemy():  # NimbusMySQLAlchemy(NimbusDatabase):
    """
    """

    def __init__(self, config_file: str = 'config.json') -> None:
        # # sqlalchemy needs a Base class for all the database entities
        # self.Base = declarative_base()
        self.engine = None  # gets set according to config_file
        self.Courses = Courses
        self.AudioSampleMetaData = AudioSampleMetaData

        with open(config_file) as json_data_file:
            config = json.load(json_data_file)

        if config.get('mysql', False):
            mysql_config = config['mysql']
            RDBMS = "mysql"
            PIP_PACKAGE = "mysqlconnector"
            SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}".format(
                RDBMS, PIP_PACKAGE, mysql_config['user'],
                mysql_config['password'], mysql_config['host'],
                mysql_config['port'], mysql_config['database'])
            self.engine = create_engine(SQLALCHEMY_DATABASE_URI)

            if self.engine is None:
                raise BadConfigFileError('failed to connect to MySQL')
        else:
            msg = "config.json is missing {} field.".format('mysql')
            raise BadConfigFileError(msg)

        self.inspector = inspect(self.engine)
        self._create_database_session()
        print("initialized NimbusMySQLAlchemy")

    def _create_all_tables(self):
        # TODO: reconsider if this even works???
        # self.Base.metadata.create_all(self.engine)
        # TODO: go with this instead... more explicit...
        self.Courses.__table__.create(bind=self.engine)
        self.AudioSampleMetaData.__table__.create(bind=self.engine)

    def _create_database_session(self):
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        print("initialized database session")

    def get_course_properties(self, department: str,
                              course_num: Union[str, int]) -> List[Courses]:
        return (
            # sqlalchemy doesn't use type annotations
            # and thus does not necessarily promise a List[Courses]
            # even so we can expect .all() to return a list
            # so long as there is no error in the MySQL syntax
            self.session.query(Courses).filter(
                Courses.dept == department,
                Courses.courseNum == course_num).all())

    def create_AudioSampleMetaData_table(self) -> None:
        table_name = self.AudioSampleMetaData.__tablename__
        if table_name in self.inspector.get_table_names():
            print("table already exists")
            return

        self.AudioSampleMetaData.__table__.create(bind=self.engine)

    def save_audio_sample_meta_data(self, formatted_data: dict) -> bool:
        """
        Save the metadata into the NimbusDatabase.

        formatted_data this point looks like:
        {
            "isWakeWord": True,
            "firstName": "john",
            "lastName": "doe",
            "gender": "f",
            "noiseLevel": "q",
            "location": "here",
            "tone": "serious-but-not-really",
            "timestamp": 1577077883,
            "username": "guest"
        }

        Returns:
            True if all is good, else False
        """
        keys_i_care_about = {
            'isWakeWord', 'firstName', 'lastName', 'gender', 'noiseLevel',
            'location', 'tone', 'timestamp', 'username'
        }

        if len(formatted_data) == 0:
            raise Exception("I did not get the keys I care about")

        for k in formatted_data:
            if k not in keys_i_care_about:
                # TODO: make this a better message
                raise Exception("I did not get the keys I care about")

        # create an AudioSampleMetaData object with the given metadata
        metadata = AudioSampleMetaData()

        # TODO: @waidhoferj
        #       maybe category does make sense for readability here?
        if formatted_data['isWakeWord'] == 'ww':
            metadata.is_wake_word = True
        elif formatted_data['isWakeWord'] == 'nww':
            metadata.is_wake_word = True
        else:
            raise Exception("unexpected values for isWakeWord")

        metadata.first_name = formatted_data['firstName']
        metadata.last_name = formatted_data['lastName']
        metadata.gender = formatted_data['gender']

        if formatted_data['noiseLevel'] == 'q':
            metadata.noise_level = NoiseLevel.quiet
        elif formatted_data['noiseLevel'] == 'm':
            metadata.noise_level = NoiseLevel.medium
        elif formatted_data['noiseLevel'] == 'l':
            metadata.noise_level = NoiseLevel.loud
        else:
            raise Exception("unexpected values for noiseLevel")

        metadata.location = formatted_data['location']
        metadata.tone = formatted_data['tone']
        metadata.timestamp = formatted_data['timestamp']
        metadata.username = formatted_data['username']

        # insert this new metadata object into the AudioSampleMetaData table
        self.session.add(metadata)
        self.session.commit()

        pass

    def _execute(self, query: str):
        return self.engine.execute(query)

    def __del__(self):
        print("NimbusMySQLAlchemy closed")


class NimbusMySQL(NimbusDatabase):
    """An adapter for mysql-connector-python to fit our program.

    The NimbusMySQL makes the mysql-connector-python interface
    compatible with the our program's interface.

    Attributes:
        config_file: a JSON file with the mysql details.
    """

    def __init__(self, config_file: str = 'config.json') -> None:
        """
        Inits Nimbus Database using the hostname, username, password
        found inside the config_file.

        Args:
            config_file: a JSON file with a 'mysql' object that holds
            the connection details.

        Returns:
            None

        Raises:
            BadConfigFileError: If the config_file fields are unexpected.
        """
        self.connection = None  # gets set according to config_file
        self.database = None  # gets set according to config_file

        with open(config_file) as json_data_file:
            config = json.load(json_data_file)

        if config.get('mysql', False):
            mysql_config = config['mysql']
            self.connection = mysql.connector.connect(
                host=mysql_config['host'],
                user=mysql_config['user'],
                passwd=mysql_config['password'])

            self.database = mysql_config['database']

            if self.connection is None or self.database is None:
                raise BadConfigFileError('failed to connect to MySQL')
        else:
            msg = "config.json is missing {} field.".format('mysql')
            raise BadConfigFileError(msg)

    '''Example:
    >> > db = NimbusDatabase("config.json")
    >> > db.get_property_from_related_entities(
        ["firstName", "lastName", "ohRoom"],
        "Professors", "OfficeHours", "professorId")
    [("Foaad", "Khosmood", "14-213"), ("John", "Clements", "14-210"), ...]'''

    def get_property_from_entity(
            self,
            prop: List[str],
            entity: str,
            condition_field: Optional[str] = None,
            condition_value: Optional[str] = None) -> List[str]:
        cursor = self.connection.cursor()
        cursor.execute('use `{}`'.format(self.database))
        columns = ", ".join(prop)

        if (condition_value is not None) and (condition_field is not None):
            conditions = condition_field + " = " + "\"" + condition_value + "\""
            statement = "SELECT {} FROM {} WHERE {}".format(
                columns, entity, conditions)

        elif (condition_value is None) and (condition_field is None):
            statement = "SELECT {} FROM {}".format(columns, entity)

        else:
            print("choose both condition field and condition value")
            return []

        # print(statement)
        cursor.execute(statement)
        tups = cursor.fetchall()
        cursor.close()

        return tups

    def get_property_from_related_entities(
            self,
            prop: List[str],
            entity1: str,
            entity2: str,
            key1: str,
            key2: Optional[str] = None,
            condition_field: Optional[str] = None,
            condition_value: Optional[str] = None) -> List[str]:
        return []

    def get_fields_of_entity(self, entity1: str) -> str:
        cursor = self.connection.cursor()
        # don't know why the line below is a syntactically wrong.
        # cursor.execute('use {}'.format(self.database))
        cursor.execute("SHOW COLUMNS FROM {}".format(entity1))
        fields = cursor.fetchall()
        cursor.close()
        return fields

    def yield_entities(self) -> str:
        """Yields a list of all entities in the database."""
        cursor = self.connection.cursor()
        cursor.execute('use {}'.format(self.database))
        cursor.execute('show tables')
        # `fetchall` returns a list of single element tuples
        tups = cursor.fetchall()
        cursor.close()
        for x in tups:
            yield x[0]

    def get_entities(self) -> str:
        """
        Returns a list of all entities in the database.

        Example:
        >>> from database_wrapper import NimbusMySQL
        >>> db = NimbusMySQL()
        >>> db.get_entities()
        ['Clubs', 'Corequisites', 'Corrections', 'Courses', 'OfficeHours',
        'PolyRatings', 'Prerequisites', 'Professors', 'ResearchInterests',
        'ResponseFormats', 'ShortNames']
        """
        cursor = self.connection.cursor()
        cursor.execute('use `{}`'.format(self.database))
        cursor.execute('show tables')
        # `fetchall` returns a list of single element tuples
        tups = cursor.fetchall()
        cursor.close()
        return [x[0] for x in tups]

    def get_relationships(self) -> str:
        """Returns a list of all relationships between entities in database."""
        pass

    def get_unique(self, entity, prop) -> str:
        """
        """
        cursor = self.connection.cursor()
        cursor.execute('use `{}`'.format(self.database))
        cursor.execute('select distinct({}) from {}'.format(prop, entity))
        # `fetchall` returns a list of single element tuples
        tups = cursor.fetchall()
        cursor.close()
        return [x[0] for x in tups]

    def get_bitcount(self, entity, prop) -> str:
        """
        """
        cursor = self.connection.cursor()
        cursor.execute('use `{}`'.format(self.database))
        cursor.execute('select bit_count(`{}`) from `{}`'.format(prop, entity))
        # `fetchall` returns a list of single element tuples
        tups = cursor.fetchall()
        cursor.close()
        return [x[0] for x in tups]

    def get_professor_properties(self, lastName) -> List[str]:
        # TODO: need to change the get property from entity to accept multiple
        #       condition fields and values, currently just looks by last name
        """
        To get a particular professor's properties
        """

        # FIXME: resolve unused variable `props`, until then, commented out
        props = self.get_property_from_entity(prop=["*"],
                                              entity="Professors",
                                              condition_field="lastName",
                                              condition_value=lastName)
        return props

    def get_course_properties(self, courseName) -> List[str]:
        # TODO: decide how we want to look up courses/ maybe create two methods
        #       Currently looks up by courseName
        """
        """

        # FIXME: resolve unused variable `props`, until then, commented out
        props = self.get_property_from_entity(["*"],
                                              "Courses",
                                              condition_field="courseName",
                                              condition_value=courseName)
        return props

    def close(self) -> None:
        """Close the database connection"""
        self.connection.close()
        super().close()


if __name__ == "__main__":
    db = NimbusMySQLAlchemy()
    course_list = db.get_course_properties('CSC', 357)
    print("course_list:", course_list)
    course_list = db.get_course_properties('CSC', '357')
    print("course_list:", course_list)
    csc357 = course_list[0]
    print("course_list[0].courseName", csc357.courseName)

    db.create_AudioSampleMetaData_table()

    metadata = {
        "isWakeWord": True,
        "firstName": "john",
        "lastName": "doe",
        "gender": "f",
        "noiseLevel": "q",
        "location": "here",
        "tone": "serious-but-not-really",
        "timestamp": 1577077883,
        "username": "guest"
    }

    db.save_audio_sample_meta_data(metadata)
