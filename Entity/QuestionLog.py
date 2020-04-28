from sqlalchemy import Text, Integer, Column, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class QuestionLog(Base):
    __tablename__ = "QuestionLog"
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    timestamp = Column(TIMESTAMP)

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
