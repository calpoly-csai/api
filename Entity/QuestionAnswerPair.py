from sqlalchemy import Column, Integer, Text, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
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


class QuestionAnswerPair(Base):
    __tablename__ = "QuestionAnswerPair"
    id = Column(Integer, primary_key=True)
    # SQLAlchemy resolves Boolean to TINYINT within MYSQL
    can_we_answer = Column(Boolean)
    verified = Column(Boolean)
    answer_type = Column(Enum(AnswerType))
    question_format = Column(Text)
    answer_format = Column(Text)
    is_view = False

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
