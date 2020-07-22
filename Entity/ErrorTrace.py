from sqlalchemy import Text, Integer, Column, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# EDITED Version of QuestionLog
class ErrorLog(Base):
    __tablename__ = "ErrorLog"
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    
    # ADDED
    error_code = Column(Text)
    stacktrace = Column(Text)

    timestamp = Column(TIMESTAMP)
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
