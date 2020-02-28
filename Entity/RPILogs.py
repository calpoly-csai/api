from sqlalchemy import Column, Integer, Text, Enum, Boolean 
from sqlalchemy.ext.declarative import declarative_base 
import enum

# This is the way SQLAlchemy initializes their special classes 
Base = declarative_base() 


class RPILogs(Base):
    __tablename__ = "RPILogs"
    id = Column(Integer, primary_key=True)
    normalized_question = Column(String(255))
    entity = Column(String(225))
    input_question = Column(String(225))
    prediction = Column(String(225))


class RPILogsProperties(enum.Enum):
    normalized_question = RPILogs.normalized_question
    entity = RPILogs.entity
    input_question = RPILogs.input_question
    prediction = RPILogs.prediction
