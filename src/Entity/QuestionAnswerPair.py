from sqlalchemy import Column, Integer, Text, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from .Entity import Entity
import enum

# This is the way SQLAlchemy initializes their special classes
Base = declarative_base()


class AnswerType(enum.Enum):
    """
    The Nimbus club spent many hours manually categorizing
    many question_formats as one of the following AnswerTypes
    """

    fact = 1  # a simple property of a Nimbus entity.
    related = 2  # a property of two or more related Nimbus entities.
    statistics = 3  # an aggregation of a property of a Nimbus entity
    other = 4  # something difficult or unknown.


class QuestionAnswerPair(Entity, Base):
    __tablename__ = "QuestionAnswerPair"
    id = Column(Integer, primary_key=True)
    # SQLAlchemy resolves Boolean to TINYINT within MYSQL
    can_we_answer = Column(Boolean)
    verified = Column(Boolean)
    answer_type = Column(Enum(AnswerType))
    question_format = Column(Text)
    answer_format = Column(Text)
    is_view = False

    validators = {
        "question": {
            "validate": lambda data: "question" in data
            and type(data["question"]) == str,
            "error_message": "Question wasn't provided as a string.",
        },
        "answer": {
            "validate": lambda data: "answer" in data and type(data["answer"]) == str,
            "error_message": "Answer wasn't provided as a string.",
        },
        "type": {
            "validate": lambda data: "type" in data
            and data["type"].lower() in [t.name for t in AnswerType],
            "error_message": "Provided QAPair type is not provided or not supported.",
        },
        "verified": {
            "validate": lambda data: type(data["verified"]) == bool
            or data["verified"] in ["true", "false"],
            "error_message": "Verified is not a boolean-like value.",
        },
        "isAnswerable": {
            "validate": lambda data: type(data["isAnswerable"]) == bool
            or data["isAnswerable"] in ["true", "false"],
            "error_message": "isAnswerable is not a boolean-like value.",
        },
        "id": {
            "validate": lambda data: type(data["id"]) == int or data["id"].is_digit(),
            "error_message": "id is not a valid type or not provided.",
        },
    }

    formatters = {
        "question": lambda form: ("question_format", form["question"]),
        "answer": lambda form: ("answer_format", form["answer"]),
        "type": lambda form: ("answer_type", AnswerType[form["type"].lower()])
        if "type" in form
        else AnswerType.other,
        "isAnswerable": lambda form: (
            "can_we_answer",
            form["isAnswerable"]
            if type(form["isAnswerable"]) == bool
            else form["isAnswerable"] == "true",
        ),
        "verified": lambda form: (
            "verified",
            form["verified"]
            if type(form["verified"]) == bool
            else form["verified"] == "true",
        ),
        "id": lambda form: ("id", int(form["id"])),
    }

    def validate(self, data):
        required_fields = ["question", "answer", "type"]
        optional_fields = ["isAnswerable", "verified"]
        for field in required_fields:
            validator = self.validators[field]
            valid = validator["validate"](data)
            if not valid:
                raise Exception(validator["error_message"])
        for field in optional_fields:
            if field not in data:
                continue
            validator = self.validators[field]
            valid = validator["validate"](data)
            if not valid:
                raise Exception(validator["error_message"])

    def format(self, data) -> dict:
        form = {}
        for field, val in data.items():
            if field not in self.formatters:
                continue
            key, value = self.formatters[field](form)
            form[key] = value
        return form

    def update(self, data: dict) -> bool:
        try:
            for key, value in data.items():
                # validate
                validator = self.validators[key]
                valid = validator["validate"](data)
                if not valid:
                    raise Exception(validator["error_message"])
                # format
                name, value = self.formatters[key](data)
                # update
                setattr(self, name, value)
        except Exception:
            return False
        return True

    def get_data(self):
        return {
            "can_we_answer": self.can_we_answer,
            "verified": self.verified,
            "answer_type": self.answer_type,
            "question_format": self.question_format,
            "answer_format": self.answer_format,
        }

    def __repr__(self):
        """
        A lazy __repr__ inspired by https://stackoverflow.com/a/60087190
        """
        D = self.__dict__
        attributes = [
            f"{k}={D.get(k)}" for k in self.__dir__() if not k.startswith("_")
        ]
        attributes_string = ", ".join(attributes)
        return f"{self.__class__.__name__}({attributes_string})"  # noqa
