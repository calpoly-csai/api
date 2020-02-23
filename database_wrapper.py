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
from typing import List, Optional, Union

import mysql.connector
import sqlalchemy
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from Entity.AudioSampleMetaData import AudioSampleMetaData, NoiseLevel
from Entity.Courses import Courses
from Entity.QuestionAnswerPair import QuestionAnswerPair, AnswerType
from Entity.Professors import Professors


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
        self.Courses = Courses
        self.Professors = Professors
        self.AudioSampleMetaData = AudioSampleMetaData
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

        __safe_create(self.Courses)
        __safe_create(self.Professors)
        __safe_create(self.AudioSampleMetaData)
        __safe_create(self.QuestionAnswerPair)

    def _create_database_session(self):
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        print("initialized database session")

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

    def create_AudioSampleMetaData_table(self) -> None:
        table_name = self.AudioSampleMetaData.__tablename__
        if table_name in self.inspector.get_table_names():
            print("table already exists")
            return

        self.AudioSampleMetaData.__table__.create(bind=self.engine)

    def save_question_answer_pair(self, qa_dict: dict) -> bool:
        """
        Save the given question answer pair into the database.

        Example input:
        {
            "can_we_answer": False,
            "answer_type": AnswerType.other,
            "question_format": "What is the meaning of life?",
            "answer_format": "Dr. Fizzbuzz says the answer is sqrt(1764)"
        }

        Args:
            qa_dict: a dictionary that corresponds to the fields in QuestionAnswerPair  # noqa

        Raises:
            BadDictionaryKeyError - ...
            BadDictionaryValueError - ...

        Returns:
            True if all is good, else False
        """
        # create an QuestionAnswerPair object with the given data
        qa_pair_data = QuestionAnswerPair()
        qa_pair_data.can_we_answer = qa_dict["can_we_answer"]
        qa_pair_data.answer_type = qa_dict["answer_type"]
        qa_pair_data.question_format = qa_dict["question_format"]
        qa_pair_data.answer_format = qa_dict["answer_format"]

        # insert this new qa_pair_data object into the QuestionAnswerPair table
        self.session.add(qa_pair_data)
        self.session.commit()
        return True

    @raises_database_error  # noqa - C901 "too complex" - agreed TODO: reduce complexity
    def save_audio_sample_meta_data(self, formatted_data: dict) -> bool:
        """
        Save the metadata into the NimbusDatabase.

        formatted_data at this point looks like:
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
            BadDictionaryKeyError - ...
            BadDictionaryValueError - ...

        Returns:
            True if all is good, else False
        """
        keys_i_care_about = {
            "isWakeWord",
            "firstName",
            "lastName",
            "gender",
            "noiseLevel",
            "location",
            "tone",
            "timestamp",
            "username",
            "filename",
        }

        print(formatted_data)

        if len(formatted_data) == 0:
            msg = "expected: {} but got: {}"
            msg = msg.format(keys_i_care_about, set(formatted_data.keys()))
            raise BadDictionaryKeyError(msg)

        # assert that the formatted_data does not have extra keys
        for k in formatted_data:
            if k not in keys_i_care_about:
                msg = "expected: {} but got: {}"
                msg = msg.format(keys_i_care_about, set(formatted_data.keys()))
                raise BadDictionaryKeyError(msg)

        # assert that the keys_i_care_about are in formatted_data
        for k in keys_i_care_about:
            if k not in formatted_data:
                msg = "expected: {} but got: {}"
                msg = msg.format(keys_i_care_about, set(formatted_data.keys()))
                raise BadDictionaryKeyError(msg)

        # create an AudioSampleMetaData object with the given metadata
        metadata = AudioSampleMetaData()

        isWW = formatted_data["isWakeWord"]
        if (isWW == "ww") or (isWW is True):
            metadata.is_wake_word = True
        elif (isWW == "nww") or (isWW is False):
            metadata.is_wake_word = False
        else:
            msg = "unexpected values for isWakeWord\n"
            msg += "expected 'ww' or True or 'nww' or False but got '{}'"
            msg = msg.format(formatted_data["isWakeWord"])
            raise BadDictionaryValueError(msg)

        metadata.first_name = formatted_data["firstName"]
        metadata.last_name = formatted_data["lastName"]
        metadata.gender = formatted_data["gender"]

        if (
            formatted_data["noiseLevel"] == "q"
            or formatted_data["noiseLevel"] == "quiet"
        ):
            metadata.noise_level = NoiseLevel.quiet
        elif (
            formatted_data["noiseLevel"] == "m"
            or formatted_data["noiseLevel"] == "medium"
        ):
            metadata.noise_level = NoiseLevel.medium
        elif (
            formatted_data["noiseLevel"] == "l"
            or formatted_data["noiseLevel"] == "loud"
        ):
            metadata.noise_level = NoiseLevel.loud
        else:
            msg = "unexpected values for noiseLevel\n"
            msg += "expected 'q' or 'm' or 'l' but got '{}'"
            msg = msg.format(formatted_data["noiseLevel"])
            raise BadDictionaryValueError(msg)

        metadata.location = formatted_data["location"]
        metadata.tone = formatted_data["tone"]
        metadata.timestamp = formatted_data["timestamp"]
        metadata.username = formatted_data["username"]

        metadata.filename = formatted_data["filename"]

        # insert this new metadata object into the AudioSampleMetaData table
        self.session.add(metadata)
        self.session.commit()

        return True

    def save_faculty(self, professor: dict) -> bool:
        """ 
         Save the given professor into the database. 
  
         Example input: 
         { 
             "id": 1, 
             "firstName": "Tim", 
             "lastName": "Kearns", 
             "phoneNumber": "805-123-4567" ,
             "researchInterests": "algorithms, databases",
             "email": "tkearns@calpoly.edu"
         } 
  
         Args: 
             professor: a dictionary that corresponds to the fields in Professor
  
         Raises: 
             BadDictionaryKeyError - ... 
             BadDictionaryValueError - ... 
  
         Returns: 
             True if all is good, else False 
         """ 
         professor_data= Professors()
         professor_data.id = professor["id"]
         professor_data.firstName = professor["firstName"]
         professor_data.lastName = professor["lastName"]
         professor_data.phoneNumber = professor["phoneNumber"]
         professor_data.researchInterests = professor["researchInterests"]
         professor_data.email = professor["email"]

         # insert this new professor_data object into the Professors table 
         self.session.add(professor_data) 
         self.session.commit() 
         return True



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

    def __init__(self, config_file: str = "config.json") -> None:
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

        if config.get("mysql", False):
            mysql_config = config["mysql"]
            self.connection = mysql.connector.connect(
                host=mysql_config["host"],
                user=mysql_config["user"],
                passwd=mysql_config["password"],
            )

            self.database = mysql_config["database"]

            if self.connection is None or self.database is None:
                raise BadConfigFileError("failed to connect to MySQL")
        else:
            msg = "config.json is missing {} field.".format("mysql")
            raise BadConfigFileError(msg)

    """Example:
    >> > db = NimbusDatabase("config.json")
    >> > db.get_property_from_related_entities(
        ["firstName", "lastName", "ohRoom"],
        "Professors", "OfficeHours", "professorId")
    [("Foaad", "Khosmood", "14-213"), ("John", "Clements", "14-210"), ...]"""

    def get_property_from_entity(
        self,
        prop: List[str],
        entity: str,
        condition_field: Optional[str] = None,
        condition_value: Optional[str] = None,
    ) -> List[str]:
        cursor = self.connection.cursor()
        cursor.execute("use `{}`".format(self.database))
        columns = ", ".join(prop)

        if (condition_value is not None) and (condition_field is not None):
            conditions = condition_field + " = " + '"' + condition_value + '"'
            statement = "SELECT {} FROM {} WHERE {}".format(columns, entity, conditions)

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
        condition_value: Optional[str] = None,
    ) -> List[str]:
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
        cursor.execute("use {}".format(self.database))
        cursor.execute("show tables")
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
        cursor.execute("use `{}`".format(self.database))
        cursor.execute("show tables")
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
        cursor.execute("use `{}`".format(self.database))
        cursor.execute("select distinct({}) from {}".format(prop, entity))
        # `fetchall` returns a list of single element tuples
        tups = cursor.fetchall()
        cursor.close()
        return [x[0] for x in tups]

    def get_bitcount(self, entity, prop) -> str:
        """
        """
        cursor = self.connection.cursor()
        cursor.execute("use `{}`".format(self.database))
        cursor.execute("select bit_count(`{}`) from `{}`".format(prop, entity))
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
        props = self.get_property_from_entity(
            prop=["*"],
            entity="Professors",
            condition_field="lastName",
            condition_value=lastName,
        )
        return props

    def get_course_properties(self, courseName) -> List[str]:
        # TODO: decide how we want to look up courses/ maybe create two methods
        #       Currently looks up by courseName
        """
        """

        # FIXME: resolve unused variable `props`, until then, commented out
        props = self.get_property_from_entity(
            ["*"], "Courses", condition_field="courseName", condition_value=courseName
        )
        return props

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


if __name__ == "__main__":
    db = NimbusMySQLAlchemy()

    db._create_all_tables()

    metadata = {
        "can_we_answer": False,
        "answer_type": AnswerType.other,
        "question_format": "What is the meaning of life?",
        "answer_format": "Dr. Fizzbuzz says the answer is sqrt(1764)",
    }

    db.save_question_answer_pair(metadata)
