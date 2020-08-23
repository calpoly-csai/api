from typing import Callable, Dict, Any, List, Tuple
import functools
import re
from Entity.Courses import Courses
from Entity.Locations import Locations
from Entity.Profs import Profs
from Entity.Clubs import Clubs
from Entity.Sections import Sections
from Entity.ProfessorSectionView import ProfessorSectionView
from database_wrapper import NimbusMySQLAlchemy
import itertools

Extracted_Vars = Dict[str, Any]
DB_Data = Dict[str, Any]
DB_Query = Callable[[Extracted_Vars], DB_Data]
Answer_Formatter = Callable[[Extracted_Vars, DB_Data], str]


tag_lookup = {
    "PROF": Profs,
    "CLUB": Clubs,
    "COURSE": Courses,
    "SECRET_HIDEOUT": Locations,
    "SECTION": Sections,
    "PROF_SECTION": ProfessorSectionView,
}


class QA:
    """
    A class for wrapping functions used to answer a question.
    """

    def __init__(self, q_format, db_query, format_answer, db):
        """
        Args:
            q_format (str): Question format string
            db (NimbusDatabase): Object used to access remote database
            db_query (DB_Query): Function used to get data from database. Takes
                a dict of extracted variables and returns a dict of variables
                from the database.
            format_answer (Answer_Formatter): Function used to format answer
                string. Takes two dicts--one of extracted variables and one of
                data retrieved from the database--and returns a str.
        """
        self.db = db
        self.q_format = q_format
        self.db_query = db_query
        self.format_answer = format_answer

    def answer(self, extracted_vars):
        db_data = self.db_query(extracted_vars, self.db)
        answer = self.format_answer(extracted_vars, db_data)
        return answer

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


def _string_sub(a_format, extracted_info, db_data):
    if None in db_data.values():
        return None
    else:
        return a_format.format(ex=extracted_info["normalized entity"], **db_data)


def string_sub(a_format):
    return functools.partial(_string_sub, a_format)


def _get_property(
    prop: str, table: str, extracted_info: Extracted_Vars, db: NimbusMySQLAlchemy
):
    ent_string = extracted_info["normalized entity"]
    if table is None:
        ent = tag_lookup[extracted_info["tag"]]
    else:
        ent = tag_lookup[table]
    try:
        value = db.get_property_from_entity(
            prop=prop, entity=ent, identifier=ent_string
        )
    except IndexError:
        return {f"db_{prop}": None}
    else:
        return {f"db_{prop}": value}


def get_property(prop: str, table: str = None):
    return functools.partial(_get_property, prop, table)


def _get_property_list(
    prop: str,
    joiner: str,
    table: str,
    extracted_info: Extracted_Vars,
    db: NimbusMySQLAlchemy,
):
    ent_string = extracted_info["normalized entity"]
    if table is None:
        ent = tag_lookup[extracted_info["tag"]]
    else:
        ent = tag_lookup[table]

    try:
        values = db._get_property_from_entity(
            prop=prop, entity=ent, identifier=ent_string
        )
    except IndexError:
        return {f"db_{prop}": None}
    else:
        exact_matches = get_all_exact_matches(values)
        return {f"db_{prop}": _grammatical_join(exact_matches, joiner)}


def get_property_list(prop: str, joiner: str, table: str = None):
    return functools.partial(_get_property_list, prop, joiner, table)


def _generic_answer_formatter(
    a_format: str, pred: Any, extracted_info: Extracted_Vars, db_data: DB_Data
):

    if type(pred) == str:
        t_f = re.search(pred, db_data)
    elif callable(pred):
        t_f = pred(db_data)
    else:
        t_f = bool(db_data)

    y_n = "Yes" if t_f else "No"
    _not = "" if t_f else "not"
    not_not = "not" if t_f else ""

    return a_format.format(
        y_n=y_n,
        yes_no=y_n,
        _not=_not,
        not_not=not_not,
        t_f=t_f,
        db=db_data,
        ex=extracted_info,
    )


def generic_answer_formatter(a_format: str, pred: Any = None):
    return functools.partial(_generic_answer_formatter, a_format, pred)


def _grammatical_join(substrings: list, last_two_join: str = "and"):
    if len(substrings) == 0:
        return ""
    elif len(substrings) == 1:
        return substrings[0]
    elif len(substrings) == 2:
        return f"{substrings[0]} {last_two_join} {substrings[1]}"
    else:
        substrings.append(f"{last_two_join} {substrings.pop()}")
        return ", ".join(substrings)


def format_prof_office_hours(extracted_vars: Extracted_Vars, db_data: DB_Data):
    prof = extracted_vars["PROF"]["normalized entity"]
    days = db_data["PROF"]["OfficeHours"]
    return _format_prof_office_hours(prof, days)


def _format_prof_office_hours(prof: str, days: str):
    hours = lambda x: x[1]

    week = []
    for token in days.split(", "):
        try:
            d, h = token.split(" ", 1)
        except ValueError:
            continue
        week.append((d, h))

    if not week:
        return f"{prof} currently has no office hours"

    week.sort(key=hours)
    groups = []
    keys = []
    for key, group in itertools.groupby(week, hours):
        groups.append(list(group))
        keys.append(key)

    if keys[0] == "on leave":
        return f"{prof} is currently on leave"

    substrings = []
    for g in groups:
        ds = [d for d, _ in g]
        k = hours(g[0]).replace("-", "to")
        substrings.append(f"{_grammatical_join(ds)} {k}")

    return f"{prof} has office hours {_grammatical_join(substrings)}"


def _chain_db_access(
    fns: List[DB_Query], extracted_vars: Extracted_Vars, db: NimbusMySQLAlchemy
) -> DB_Data:
    """
    Combines behavior of a list of database access functions

    Args:
        fns: List of database access functions to run
        extracted_vars: Dictionary of extracted information to run fns against

    Returns:
        A dictionary of database data
    """
    db_data = dict()
    for fn in fns:
        for key, val in fn(extracted_vars, db).items():
            index = 1
            while key in db_data:
                key = f"{key}{index}"
                index += 1
            db_data[key] = val
    return db_data


# Actually returns partial[Dict[str, Any]]
def chain_db_access(fns: List[DB_Query]) -> DB_Query:
    return functools.partial(_chain_db_access, fns)


def get_all_exact_matches(matches):
    exact = matches[-1][1]
    exact_matches = []
    for match in reversed(matches):
        if match[1] == exact:
            exact_matches.append(match[2])
    return exact_matches


def generate_qa_pairs(qa_pairs: Tuple[str, str], db: NimbusMySQLAlchemy):
    qa_objs = []
    for pair in qa_pairs:
        q, a = pair
        db_access_fns = []
        tokens = a.split()
        for i, token in enumerate(tokens):
            # I get errors if I don't cast token to a string here, even though str.split() should
            # return a list of strings
            match = re.match(r"\[(.*?)\]", str(token))
            if not match:
                continue
            else:
                subtokens = match.group(1).split("..")
                # Match is an entity
                if len(subtokens) == 1:
                    tokens[i] = "{ex}"
                # Match is a single-item property
                elif len(subtokens) == 2:
                    ent, prop = subtokens
                    db_access_fns.append(get_property(prop))
                    tokens[i] = "{db_" + prop + "}"
                elif len(subtokens) == 3:
                    ent, prop, third = subtokens
                    if third in tag_lookup:
                        # third is a table name
                        db_access_fns.append(get_property(prop, third))
                    else:
                        # third is the string used to join the last two of a list of items
                        db_access_fns.append(get_property_list(prop, third))
                    tokens[i] = "{db_" + prop + "}"
                elif len(subtokens) == 4:
                    ent, prop, table, joiner = subtokens
                    db_access_fns.append(get_property_list(prop, joiner, table))
                    tokens[i] = "{db_" + prop + "}"

        o = QA(
            q_format=q,
            db_query=chain_db_access(db_access_fns),
            format_answer=string_sub(" ".join(tokens)),
            db=db,
        )
        qa_objs.append(o)

    return qa_objs
