"""A wrapper module for the Nimbus data storage systems.

This module includes various adapters for interfacing with
different databases and storage locations.

    Typical usage example:

    connection = connect_to_mysql('config.json')
    bar = foo.FunctionBar()
"""
#!/usr/bin/env python3
import mysql.connector
import json

MYSQL_TYPE = mysql.connector.connection_cext.CMySQLConnection


class MySQLAdapter:
    """An adapter for mysql-connector-python to fit our program.

    The MySQLAdapter makes the mysql-connector-python interface
    compatible with the our program's interface.

    Attributes:
        connection: The mysql-connector-python connection object.
        database: the database to execute queries on.
    """

    def __init__(self,
                 mysql_connection_object: MYSQL_TYPE,
                 database: str) -> None:
        """Inits MySQLAdapter with mysql_connection_object.

        Args:
            mysql_connection_object: object representing a mysql connection.
            database: the database to execute queries on.

        Returns:
            None
        """
        self.connection = mysql_connection_object
        self.database = database

    def get_entities(self) -> str:
        """Yields a list of all entities in the database."""
        cursor = self.connection.cursor()
        cursor.execute('use {}'.format(self.database))
        cursor.execute('show tables')
        # `fetchall` returns a list of single element tuples
        tups = cursor.fetchall()
        cursor.close()
        for x in tups:
            yield x[0]

    def get_relationships(self) -> str:
        """Returns a list of all relationships between entities in database."""
        pass


class UnsupportedDatabaseError(Exception):
    """Raised when operation tries to connect to an unsupported database type.

    Attributes:
        message: an explanation of why the expected database is unsupported.
    """

    def __init__(self, message: str):
        self.message = message


def connect(database_type: str = 'mysql', config_file: str = 'config.json'):
    """Returns the connection object after connecting to a database

    Args:
        database_type: An optional variable for choosing the database. (default=420)
        config_file: the filename string of the config file. (default=

    Returns:
        a connection object
    """
    if database_type:
        return connect_to_mysql(config_file)
    else:
        return None  # ???


def connect_to_mysql(config_file):
    """Connect to a MySQL database given a configuration file in JSON format.

    Args:
        config_file: the config.JSON filename with a "mysql" key.

    Returns:
        the mysql-connector-python connection object

    Raises:
        UnsupportedDatabaseError: If an unknown database type found.
    """
    with open(config_file) as json_data_file:
        config = json.load(json_data_file)

    if config.get('mysql', False):
        mysql_config = config['mysql']
        return mysql.connector.connect(
            host=mysql_config['host'],
            user=mysql_config['user'],
            passwd=mysql_config['password']
        )
    else:
        raise UnsupportedDatabaseError("sorry, idk this database type.")
