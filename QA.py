from typing import Callable, Dict, Any
import functools
import re
from Entity.Courses import Courses
from Entity.Locations import Locations
from Entity.Professors import Professors
from Entity.Clubs import Clubs
from Entity.Sections import Sections
from database_wrapper import NimbusMySQLAlchemy
from pandas import read_csv

Extracted_Vars = Dict[str, Any]
DB_Data = Dict[str, Any]
DB_Query = Callable[[Extracted_Vars], DB_Data]
Answer_Formatter = Callable[[Extracted_Vars, DB_Data], str]


tag_lookup = {
    'PROF': Professors,
    'CLUB': Clubs,
    'COURSE': Courses,
    'SECRET_HIDEOUT': Locations,
    'SECTION': Sections
}

class QA:
    """
    A class for wrapping functions used to answer a question.
    """

    def __init__(self, q_format, db_query, format_answer):
        """
        Args:
            q_format (str): Question format string
            db (NimbusDatabase): Object used to access remote database
            db_query (DB_Query): Function used to get data from database. Takes
                a dict of extracted variables and returns a dict of variables
                from the database.
            format_function (Answer_Formatter): Function used to format answer
                string. Takes two dicts--one of extracted variables and one of
                data retrieved from the database--and returns a str.
        """
        self.q_format = q_format
        self.db_query = db_query
        self.format_answer = format_answer

    def _get_data_from_db(self, extracted_vars):
        return self.db_query(extracted_vars)

    def _format_answer(self, extracted_vars, db_data):
        return self.format_answer(extracted_vars, db_data)

    def answer(self, extracted_vars):
        db_data = self._get_data_from_db(extracted_vars)
        return self._format_answer(extracted_vars, db_data)

    def __repr__(self):
        return self.q_format

    def __hash__(self):
        return hash(self.q_format)


def create_qa_mapping(qa_list):
    """
    Creates a dictionary whose values are QA objects and keys are the question
    formats of those QA objects.

    Args:
        qa_list (list(QA))
    """
    return {qa.q_format: qa for qa in qa_list}


# def _string_sub(a_format, extracted_vars, db_data):
#     """
#     Substitutes values in a string based off the contents of the extracted_vars
#     and db_data dictionaries. Keys from the dictionaries in the a_format string
#     will be replaced with their associated value.
#
#     Example input/output:
#         a_format: "{professor1_ex}'s office is {office1_db}."
#         extracted_vars: {"professor1": "Dr. Khosmood"}
#         db_data: {"office1": "14-213"}
#
#         "Dr. Khosmood's office is 14-213"
#
#     Args:
#         a_format (str): String to be formatted. Variables to be substituted should
#             be in curly braces and end in "_ex" for keys from extracted_vars and "_db"
#             for keys from db_data.
#         extracted_vars (Extracted_Vars)
#         db_data (Db_Data)
#
#     Returns:
#         A formatted answer string
#     """
#     # Adds "_ex" to the end of keys in extracted_vars
#     extracted_vars = {
#         k + "_ex": v for k, v in extracted_vars.items()
#     }
#     # Adds "_db" to the end of keys in db_data
#     db_data = {
#         k + "_db": v for k, v in db_data.items()
#     }
#     return a_format.format(**extracted_vars, **db_data)
#
#
# def _single_var_string_sub(a_format, extracted_vars, db_data):
#     """
#     Like _string_sub for cases where there's max one item in either dict
#
#     Example input/output:
#         a_format: "{ex}'s office is {db}."
#         extracted_vars: {"professor1": "Dr. Khosmood"}
#         db_data: {"office1": "14-213"}
#
#         "Dr. Khosmood's office is 14-213"
#
#     Args:
#         a_format (str): String to be formatted. {ex} will be substituted with
#             the value from extracted_vars and {db} will be substituted with the
#             value from db_data
#         extracted_vars (Extracted_Vars)
#         db_data (Db_Data)
#
#     Returns:
#         A formatted answer string
#     """
#     # Gets value from a dictionary with a single item
#     ex_val = next(iter(extracted_vars.values())) if extracted_vars else ''
#     db_val = next(iter(db_data.values())) if db_data else ''
#     return a_format.format(ex=ex_val, db=db_val)
#
#
# def string_sub(a_format):
#     return functools.partial(_string_sub, a_format)
#
#
# def single_var_string_sub(a_format):
#     return functools.partial(_single_var_string_sub, a_format)


def _string_sub(a_format, extracted_info, db_data):
    if db_data is None:
        return None
    else:
        return a_format.format(ex=extracted_info['normalized entity'], db=db_data)


def string_sub(a_format):
    return functools.partial(_string_sub, a_format)


def _get_property(prop, extracted_info):
    ent_string = extracted_info["normalized entity"]
    ent = tag_lookup[extracted_info['tag']]
    try:
        db = NimbusMySQLAlchemy()
        value = db.get_property_from_entity(prop=prop, entity=ent, identifier=ent_string)
    except IndexError:
        return None
    else:
        return value


def get_property(prop):
    return functools.partial(_get_property, prop)


def _yes_no(a_format, pred, extracted_info, db_data):
    if pred is None:
        result = 'Yes' if db_data else 'No'
    elif type(pred) == str:
        result = 'Yes' if re.search(pred, db_data) else 'No'
    else:
        result = 'Yes' if pred(db_data) else 'No'
    return a_format.format(y_n=result, yes_no=result, ex=extracted_info['normalized entity'])


def yes_no(a_format, pred=None):
    return functools.partial(_yes_no, a_format, pred)


def generate_fact_QA(csv):
    df = read_csv(csv)
    text_in_brackets = r'\[[^\[\]]*\]'
    qa_objs = []
    for i in range(len(df)):
        q = df['question_format'][i]
        a = df['answer_format'][i]
        matches = re.findall(text_in_brackets, a)
        extracted = None
        if len(matches) == 1:
            db_data = matches[0]
        elif '..' in matches[1]:
            db_data = matches[1]
            extracted = matches[0]
        else:
            db_data = matches[0]
            extracted = matches[1]
        prop = db_data.split('..', 1)[1][0:-1]
        a = a.replace(db_data, '{db}')
        if extracted is not None:
            a = a.replace(extracted, '{ex}')
        o = QA(
            q_format=q,
            db_query=get_property(prop),
            format_answer=string_sub(a)
        )
        qa_objs.append(o)

    return qa_objs
