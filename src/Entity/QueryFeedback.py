from sqlalchemy import Column, DateTime, Text, Enum, Integer
from sqlalchemy.ext.declarative import declarative_base
import enum
from .QuestionAnswerPair import AnswerType


# This is the way SQLAlchemy initializes their special classes
Base = declarative_base()


class QueryFeedback(Base):
    __tablename__ = "QueryFeedback"
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    answer = Column(Text)
    answer_type = Column(Enum(AnswerType))
    timestamp = Column(DateTime)
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
