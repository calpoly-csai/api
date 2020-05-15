import time
import enum
from abc import ABC
import datetime
import re

from werkzeug.exceptions import BadRequestKeyError


class Validator(ABC):
    def __init__(self):
        super().__init__()

    def validate(self, data: dict) -> dict:
        """
        Takes in a dictionary of data and returns a dictionary of issues
        Parameters
        ----------
        - `data : dict` form data to validate

        Returns
        -------
        dict
            issues with the data
        """
        return data

    def fix(self, data: dict, issues) -> dict:
        """
        Takes measures to fill in missing data in form, cloning, mutating and then returning the data.
        If not possible, raises error.

        Parameters
        ----------
        - `data : dict` form data to fix
        - `issues: dict|list` lists of issues to fix for each form section

        Returns
        -------
        dict
            A fixed copy of the data

        Raises
        ------
        Exception
            when the issue with the data are not fixable.
        """
        return data


class WakeWordValidatorIssue(enum.Enum):
    DOES_NOT_EXIST = 1
    INVALID = 2


class WakeWordValidatorError(Exception):
    """Raised when.... bad data...

    Attributes:
        message: an explanation of... why bad data...
    """

    def __init__(self, message: str):
        self.message = message


class WakeWordValidator(Validator):
    """Ensures that the form metadata recieved from the REST API for the Wake Word audio is valid."""

    def __init__(self, validators=None):
        super().__init__()
        self.validators = validators or {
            "isWakeWord": lambda val: type(val) == str
            and (val == "true" or val == "false"),
            "noiseLevel": lambda level: type(level) == str
            and level in "qml"
            and len(level) == 1,
            "tone": lambda tone: type(tone) == str,
            "location": lambda location: type(location) == str,
            "gender": lambda gender: type(gender) == str
            and gender in "mf"
            and len(gender) == 1,
            "lastName": lambda lastName: type(lastName) == str,
            "firstName": lambda firstName: type(firstName) == str,
            "timestamp": lambda timestamp: str.isdigit(timestamp),
            "username": lambda username: type(username) == str,
            "emphasis": lambda emphasis: type(emphasis) == str,
            "script": lambda script: type(script) == str,
        }

    def validate(self, data):
        """
        Checks if the Wake Word audio metadata is complete and in its correct form.
        Returns array of issues.
        """
        issues = {}
        for key in self.validators:
            validator = self.validators[key]
            try:
                value = data[key]
                if not validator(value):
                    issues[key] = WakeWordValidatorIssue.INVALID
            except BadRequestKeyError as e:
                print("caught BadRequestKeyError: ", e.args)
                issues[key] = WakeWordValidatorIssue.DOES_NOT_EXIST
        return issues

    def fix(self, data, issues):
        """
        Attempts to fix Wake Word audio metadata.
        If the data issue is irreplaceable, raises WakeWordValidatorError.
        """
        form = data.copy()
        for key in issues:
            issue = issues[key]
            if issue == WakeWordValidatorIssue.DOES_NOT_EXIST:
                if key == "username":
                    form[key] = "guest"
                    print("fixed username", form[key])
                elif key == "timestamp":
                    form[key] = int(time.time())
                    print("fixed timestamp", form[key])
                elif key == "script" and form["isWakeWord"] == "ww":
                     form[key] = "nimbus"
                     print("Added 'script' value of 'nimbus'")
                else:
                    raise WakeWordValidatorError(
                        f"Required audio metadata '{key}' was not provided"
                    )
            elif issue == WakeWordValidatorIssue.INVALID:
                # TODO: anticipate invalid entries and correct them.
                raise WakeWordValidatorError(
                    f"{key} has invalid value of {form[key]} with a type of {type(form[key])}"
                )
        return form


class PhrasesValidatorError(Exception):
    """Unfixable data corruption in a query phrase object"""

    def __init__(self, message: str):
        super().__init__(self, message)
        self.message = message


class PhrasesValidatorIssue(enum.Enum):
    INVALID = 0
    DELIMITER_MISMATCH = 1
    TOKEN_VAR_MISMATCH = 2


class PhrasesValidator(Validator):
    """Validates new query phrases passed from the web app"""

    def __init__(self):
        super().__init__()
        self.error_messages = {
            PhrasesValidatorIssue.INVALID: "An unknown error occurred",
            PhrasesValidatorIssue.DELIMITER_MISMATCH: "The {field_name} field has mismatched bracket token delimiters (square braces).",
            PhrasesValidatorIssue.TOKEN_VAR_MISMATCH: "The {field_name} field has a differing number of format tokens and variables. Please pass the same number or tokens as variables",
        }

    def validate(self, data: dict) -> dict:
        """
        Ensures that:
        1. All tokens have an opening and closing delimiter.
        2. The number of tokens equals the number of provided variables.

        Parameters
        ----------
        `data : dict` A question answer pairing {question: {format: str, variables: str}, answer: {format: str, variables: str}}
        """
        issues = {"question": [], "answer": []}
        for field, form in data.items():
            # All tokens have an opening and closing delimiter
            if form["format"].count("]") != form["format"].count("["):
                issues[field].append(PhrasesValidatorIssue.DELIMITER_MISMATCH)
            # Number of tokens must equal number of variables
            if len(form["variables"]) != form["format"].count("["):
                issues[field].append(PhrasesValidatorIssue.TOKEN_VAR_MISMATCH)
        return issues

    def fix(self, data: dict, issues: dict) -> dict:
        """
        Fixes phrases data. 
        - Critical issues:
            1. Question delimiters don't match up.
            2. Question tokens don't the number of provided variables.
        - Non critical issues:
            1. Anything wrong with the answer. In this case only the question will be stored.

        Parameters
        ----------
        - `data : dict` A question answer pairing - {question: {format: str, variables: str}, answer: {format: str, variables: str}}
        - `issues: dict` lists of PhrasesValidatorIssues for the quesion answer pairing - {}

        Returns
        -------
        dict
            A fixed copy of the data

        Raises
        ------
        PhrasesValidatorError
            when the issue with the phrase data is not fixable.

        """
        form = data.copy()
        question = issues["question"]
        answer = issues["answer"]
        if len(question):
            err_msg = self.error_messages[question[0]].format(field_name="question")
            print(f"error message {err_msg}")
            raise PhrasesValidatorError(err_msg)
        if len(answer):
            form["answer"]["format"] = ""
            form["answer"]["variables"] = []
        return form


class FeedbackValidatorError(Exception):
    """Unfixable data corruption in a query phrase object"""

    def __init__(self, message: str):
        super().__init__(self, message)
        self.message = message


class FeedbackValidatorIssue(enum.Enum):
    MISSING_QUESTION = 0
    INVALID_TIMESTAMP = 1
    INVALID_TYPE = 2
    MISSING_ANSWER = 3
    CONVERT_UNIX_TO_DATETIME = 4


class FeedbackValidator(Validator):
    """Validates new query phrases passed from the web app"""

    def __init__(self):
        super().__init__()
        self.error_messages = {
            FeedbackValidatorIssue.MISSING_QUESTION: "Please provide a question in the passed data",
            FeedbackValidatorIssue.INVALID_TIMESTAMP: "Timestamp automatically set to current time",
            FeedbackValidatorIssue.CONVERT_UNIX_TO_DATETIME: "",
            FeedbackValidatorIssue.INVALID_TYPE: "Type not provided. Automatically set to OTHER",
            FeedbackValidatorIssue.MISSING_ANSWER: "Please provide an answer in the passed data",
        }

    def validate(self, data: dict) -> dict:
        """
        Ensures that:
        1. Timestamp is valid
        2. A correct answer type is assigned
        3. A question exists
        4. An answer exists

        Parameters
        ----------
        `data : dict` A feedback object {type: String, timestamp: datetime, question: String, answer: String}
        """
        issues = []
        no_content = re.compile("\W")
        # Timestamp is valid
        if "timestamp" not in data or type(data["timestamp"]) != int:
            issues.append(FeedbackValidatorIssue.INVALID_TIMESTAMP)

        elif "timestamp" in data and type(data["timestamp"]) == int:
            issues.append(FeedbackValidatorIssue.CONVERT_UNIX_TO_DATETIME)

        # A correct type is assigned
        if (
            "type" not in data
            or type(data["type"]) != str
            or data["type"] not in ["fact", "related", "stats", "other"]
        ):
            issues.append(FeedbackValidatorIssue.INVALID_TYPE)

        #  A question exists
        if (
            "question" not in data
            or type(data["question"]) != str
            or no_content.match(data["question"])
        ):
            issues.append(FeedbackValidatorIssue.MISSING_QUESTION)

        # An answer exists
        if (
            "answer" not in data
            or type(data["answer"]) != str
            or no_content.match(data["answer"])
        ):
            issues.append(FeedbackValidatorIssue.MISSING_ANSWER)

        return issues

    def fix(self, data: dict, issues: dict) -> dict:
        """
        Fixes feedback data. 
        - Critical issues:
            1. An invalid timestamp is present
            2. An invalid type is present
            3. No question or answer is provided

        Parameters
        ----------
        - `data : dict` A feedback object {type: String, timestamp: datetime, question: String, answer: String}
        - `issues: dict` lists of FeedbackValidatorIssues

        Returns
        -------
        dict
            A fixed copy of the data

        Raises
        ------
        FeedbackValidatorError
            when the issue with the feedback data is not fixable.

        """

        form = data.copy()

        for issue in issues:
            # fixes invalid timestamp (set to current datetime)
            if issue == FeedbackValidatorIssue.INVALID_TIMESTAMP:
                print("Inferred query timestamp on server")
                form["timestamp"] = datetime.datetime.now()

            # converts a valid unix timestamp to a Python Datetime object
            elif issue == FeedbackValidatorIssue.CONVERT_UNIX_TO_DATETIME:
                form["timestamp"] = datetime.datetime.fromtimestamp(form["timestamp"])

            # fixes invalid type (set to OTHER)
            elif issue == FeedbackValidatorIssue.INVALID_TYPE:
                print(f"Changed query type from invalid form to 'other'")
                form["type"] = "other"

            # raises errors for missing answer or missing questions
            elif issue == FeedbackValidatorIssue.MISSING_ANSWER:
                raise FeedbackValidatorError(
                    self.error_messages[FeedbackValidatorIssue.MISSING_ANSWER]
                )
            elif issue == FeedbackValidatorIssue.MISSING_QUESTION:
                raise FeedbackValidatorError(
                    self.error_messages[FeedbackValidatorIssue.MISSING_QUESTION]
                )
        return form
