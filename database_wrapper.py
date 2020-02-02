#!/usr/bin/env python3
"""A wrapper module for the Nimbus data storage systems.

This module includes various adapters for interfacing with
different databases and storage locations.

    Typical usage example:

    db = NimbusMySQL(config_file="config.json")
    ents = db.get_entities()
"""
import mysql.connector
from abc import ABC, abstractmethod
from typing import Optional, List
import json


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
        cursor = self.connection.cursor()
        cursor.execute('use `{}`'.format(self.database))
        # FIXME: resolve unused variable `props`, until then, commented out
        # props = get_property_from_entity(self, ["*"],
        #                                  "Professors",
        #                                  condition_field="lastName",
        #                                  condition_value=lastName)
        tups = cursor.fetchall()
        cursor.close()
        return [x[0] for x in tups]

    def get_course_properties(self, courseName) -> List[str]:
        # TODO: decide how we want to look up courses/ maybe create two methods
        #       Currently looks up by courseName
        """
        """
        cursor = self.connection.cursor()
        cursor.execute('use `{}`'.format(self.database))
        # FIXME: resolve unused variable `props`, until then, commented out
        # props = get_property_from_entity(self, ["*"],
        #                                  "Courses",
        #                                  condition_field="courseName",
        #                                  condition_value=courseName)
        tups = cursor.fetchall()
        cursor.close()
        return [x[0] for x in tups]

    def get_club_properties(self, clubName):
        """
        Gives all of the properties of a club in the database. 

        Args:
            clubName: a string representing the name of the club

        Returns:
            TODO: Determine type of the return based on the get_property_from_entity() method
        """
        pass


    def get_course_schedule(self, courseName):
        """
        Describes all of the days and times during the week that a course takes place. 

        Args:
            courseName: a string representing the name of the course

        Returns:
            TODO: Determine type of the return based on the get_property_from_entity() method
        """
        pass

    def get_professor_schedule(self, lastName):
        """
        Gives all of the properties of a club in the database. 

        Args:
            lastName: a string representing the last name of the professor
            TODO: Choose exactly how to be referencing professors

        Returns:
            TODO: Determine type of the return based on the get_property_from_related_entity() method
        """
        pass

    def get_course_prerequisites(self, courseName):
        """
        Gives the prerequisite courses for a given course in the database. 

        Args:
            courseName: a string representing the name of the course

        Returns:
            TODO: Determine type of the return based on the get_property_from_related_entity() method
        """
        pass

    def get_professor_research_interests(self, lastName):
        """
        Gives the research interests of a specific professor. 

        Args:
            lastName: a string representing the lastName of the professor
            TODO: Choose exactly how to be referencing professors
        Returns:
            TODO: Determine type of the return based on the get_property_from_related_entity() method
        """
        pass

    def get_professors_with_interest(self, interest):
        """
        Gives the professors who have a specific research interest. 

        Args:
            interest: a string representing a research interest professors may have

        Returns:
            TODO: Determine type of the return based on the get_property_from_related_entity() method
        """
        pass

    def get_professor_polyrating(self, lastName):
        """
        Gives the average polyrating of a specific professor. 
    
        Args:
            lastName: a string representing the lastName of the professor
            TODO: Choose exactly how to be referencing professors
        Returns:
            TODO: Determine type of the return based on the get_property_from_related_entity() method
        """
        pass

    def close(self) -> None:
        """Close the database connection"""
        self.connection.close()
        super().close()


