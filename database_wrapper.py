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


UNION_ENTITIES = Union[
    Calendars, Courses, Professors, AudioSampleMetaData, QuestionAnswerPair
]
UNION_PROPERTIES = Union[ProfessorsProperties]


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

    def _create_database_session(self):
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


    def get_property_from_entity(
        self, prop: str, entity: UNION_ENTITIES, entity_string: str
    ) -> List[UNION_ENTITIES]:
        """
        ISSUE: 1)Don't know which column/attribute entity_string corresponds to
                 for conditional filtering
               2)Current code checks all attribute and returns row that contains
                 entity string.
                    -> Complication: return entity that
        """

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
            prop: ...
            entity: ...
            entity_string: ...

        Returns:
            A list of values for `prop`
            such that the `entity` matches the `entity_string`.

        Raises:
            ...
        """
        # TODO: be smart by check only Professor.firstName Professor.lastName
        # TODO: only check Course.dept, Course.course_num, Course.course_name
        props = []
        for k in entity.__dict__:
            if not k.startswith("_"):
                props.append(entity.__dict__[k])

        results = []
        # FIXME: this is not good querying!
        # TODO: don't be so lazy!
        for p in props:
            query_obj = self.session.query(entity)
            res = query_obj.filter(p.contains(entity_string)).all()
            results += res
        return [x.__dict__.get(prop) for x in results]



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

    def save_section(self, formatted_data: dict) -> bool:
        """
        Save the given section into the database

         Example input:
         {
             "section_name": "CSC 480_06"
             "instructor": "Kauffman, Daniel Alexander"
             "alias": "dkauffma"
             "title": "Instructor AY"
             "phone": "+1.805.756.2824"
             "office": "014-0254A"
             "type": Lab
             "days": SET('M', 'W', 'F')
             "start": "10:10 AM"
             "end": "11:00 AM"
             "location": "014-0257"
             "department": "CENG-Computer Science & Software Engineering"
         }

         Args:
             formatted_data: a dictionary that corresponds to the fields in Sections

         Raises:
             BadDictionaryKeyError - ...
             BadDictionaryValueError - ...

         Returns:
             True if all is good, else False
        """

        section = Sections()
        section.section_name = formatted_data['section_name']
        section.instructor = formatted_data['instructor']
        section.alias = formatted_data['alias']
        section.title = formatted_data['title']
        section.phone = formatted_data['phone']
        section.office = formatted_data['office']
        section.type = formatted_data['type']
        section.days = formatted_data['days']
        section.start = formatted_data['start']
        section.end = formatted_data['end']
        section.location = formatted_data['location']
        section.department = formatted_data['department']

        self.session.add(section)
        self.session.commit()
        return True

    def save_club(self, formatted_data: dict) -> bool:
        """
        Save the given club into the database.

         Example input:
         {
             "club_name": Cal Poly Computer Science and Artificial Intelligence
             "types": Academic, Special Interest
             "desc": The Computer Science and Artificial Intelligence club provides..."
             "contact_email": maikens@calpoly.edu
             "contact_email_2": fkurfess@calpoly.edu
             "contact_person": Miles Aikens
             "contact_phone": 7349723564
             "box": 89
             "advisor": Franz Kurfess
             "affiliation": None
         }

         Args:
             formatted_data: a dictionary that corresponds to the fields in Clubs

         Raises:
             BadDictionaryKeyError - ...
             BadDictionaryValueError - ...

         Returns:
             True if all is good, else False
        """

        club_data = Clubs()
        club_data.club_name = formatted_data['club_name']
        club_data.types = formatted_data['types']
        club_data.desc = formatted_data['desc']
        club_data.contact_email = formatted_data['contact_email']
        club_data.contact_email_2 = formatted_data['contact_email_2']
        club_data.contact_person = formatted_data['contact_person']
        club_data.contact_phone = formatted_data['contact_phone']
        club_data.box = formatted_data['box']
        club_data.advisor = formatted_data['advisor']
        club_data.affiliation = formatted_data['affiliation']

        self.session.add(club_data)
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

        self.validate_input_keys(formatted_data, keys_i_care_about)
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

    def save_course(self, course_data: dict):
        """
        Save the course into the NimbusDatabase.

        course_data this point looks like:
        {
            "dept": CPE,
            "courseNum": 357,
            "units": 4,
            "termsOffered": "F,W,SP",
            "courseName": "Systems Programming",
            "raw_concurrent_text": "N/A",
            "raw_recommended_text": "N/A",
            "raw_prerequisites_text": "CSC/CPE,102,and,CSC/CPE,103,with,..."
        }

        Raises:
            BadDictionaryKeyError - ...
            BadDictionaryValueError - ...

        Returns:
            True if all is good, else False
        """
        expected_keys = {'dept', 'courseNum', 'units',
                         'termsOffered', 'courseName', 'raw_concurrent_text',
                         'raw_recommended_text', 'raw_prerequisites_text'}
        self.validate_input_keys(course_data, expected_keys)

        course = self.session.query(Courses).filter_by(dept=course_data['dept'],
                                                       courseNum=course_data['courseNum']).first()
        if not course:
            print("Adding new course: {} {}".format(course_data['dept'],
                                                    course_data['courseNum']))
            course = Courses()
        else:
            print("Updating course: {} {}".format(course_data['dept'],
                                                  course_data['courseNum']))

        course.dept = course_data['dept']
        course.courseNum = course_data['courseNum']
        course.termsOffered = course_data['termsOffered']
        course.units = course_data['units']
        course.courseName = course_data['courseName']
        course.raw_concurrent_text = course_data['raw_concurrent_text']
        course.raw_recommended_text = course_data['raw_recommended_text']
        course.raw_prerequisites_text = course_data['raw_prerequisites_text']

        self.session.add(course)
        self.session.commit()

    def save_location(self, location_data: dict):
        """
        Save the given location data into the database.

        Example Input:
        {
            "building_number": 1,
            "name": "Administration",
            "longitude": -120.658561,
            "latitude": 35.300960
        }
        Args:
            location_data: a dictionary that corresponds to the fields in Locations

        Raises:
            BadDictionaryKeyError - ...
            BadDictionaryValueError - ...

        Returns:
            True if all good, else False
        """
        location = Locations()
        location.building_number = location_data["building_number"]
        location.name = location_data["name"]
        location.longitude = location_data["longitude"]
        location.latitude = location_data["latitude"]

        self.session.add(location)
        self.session.commit()
        return True

    def save_calendar(self, calendar_data: dict):
        """
         Save the given calendar into the database.

         Example input:
         {
             "date": 7_4_2020,
             "day": 4,
             "month": July,
             "year": 2020,
             "raw_events_text": ['Academic holiday - Independence Day Observed']
         }

         Args:
             calendar_data: a dictionary that corresponds to the fields in Calendar

         Raises:
             BadDictionaryKeyError - ...
             BadDictionaryValueError - ...

         Returns:
             True if all is good, else False
        """

        calendar = Calendars()
        calendar.date = calendar_data["date"]
        calendar.day = calendar_data["day"]
        calendar.month = calendar_data["month"]
        calendar.year = calendar_data["year"]
        calendar.raw_events_text = calendar_data["raw_events_text"]

        self.session.add(calendar)
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

        professor_data = Professors()
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


if __name__ == "__main__":
    db = NimbusMySQLAlchemy()

    db._create_all_tables()

    data = {
        "building_number": 1,
        "name": "Administration",
        "longitude": -120.658561,
        "latitude": 35.300960,
    }

    db.save_location(data)


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

    db.save_club(data)

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

    db.save_section(data)

    print(
        "\n", "\n", "What clubs does is Kurfess advise?", "\n", "\n",
        db.get_property_from_entity(
            prop="club_name", entity=Clubs, entity_string="Kurfess"
        )
    )

    print(
        "\n", "\n", "What sections is Kauffman teaching?", "\n", "\n",
        db.get_property_from_entity(
            prop="section_name", entity=Sections, entity_string="Kauffman"
        )
    )

    print(
        "\n", "\n", "What is the long & lat of Admin building?", "\n", "\n",
        [
            (x, y)
            for x, y in zip(
            db.get_property_from_entity(
                prop="longitude", entity=Locations, entity_string="Admin"
            ),
            db.get_property_from_entity(
                prop="latitude", entity=Locations, entity_string="Admin"
            ),
        )
        ]
    )

    print(
        "\n", "\n", "What courses are about Algo?", "\n", "\n",
        db.get_property_from_entity(
            prop="courseName", entity=Courses, entity_string="Algo"
        )
    )

    print(
        "\n", "\n", "What courses are about Design?", "\n", "\n",
        db.get_property_from_entity(
            prop="courseName", entity=Courses, entity_string="Design"
        )
    )

    print(
        "\n", "\n", "What courses are somehow related to 357?", "\n", "\n",
        db.get_property_from_entity(
            prop="courseName", entity=Courses, entity_string="357"
        )
    )


    print("\n\nQA Tuple list\n\n", db.get_all_qa_pairs(), "\n\n")
    db.return_qa_pair_csv()

