from typing import Callable, Dict, Any

Extracted_Vars = Dict[str, Any]
DB_Data = Dict[str, Any]
DB_Query = Callable[[Extracted_Vars], DB_Data]
Answer_Formatter = Callable[[Extracted_Vars, DB_Data], str]


class QA:
    """
    A class for wrapping functions used to answer a question.
    """

    def __init__(self, q_format, db, db_query, format_function):
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
        self.db = db
        self.db_query = db_query
        self.format_function = format_function

    def _get_data_from_db(self, extracted_vars):
        return self.db_query(extracted_vars)

    def _format_answer(self, extracted_vars, db_data):
        return self.format_function(extracted_vars, db_data)

    def answer(self, extracted_vars):
        db_data = self._get_data_from_db(extracted_vars)
        return self._format_answer(extracted_vars, db_data)

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
