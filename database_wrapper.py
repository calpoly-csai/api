"""A wrapper module for the Nimbus data storage systems.

This module includes various adapters for interfacing with
different databases and storage locations.

    Typical usage example:

    db = NimbusMySQL(config_file="config.json")
    ents = db.get_entities()
"""
#!/usr/bin/env python3
import mysql.connector
from abc import ABC, abstractmethod
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
    def get_entities(self) -> str:
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
                passwd=mysql_config['password']
            )

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

    def close(self) -> None:
        """Close the database connection"""
        self.connection.close()
        super().close()
