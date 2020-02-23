from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base


# This is the way SQLAlchemy initializes their special classes
Base = declarative_base()

class Professors(Base):
    __tablename__ = 'Professors'
    id = Column(Integer, primary_key=True)
    firstName = Column(String(50))
    lastName = Column(String(50))
    phoneNumber = Column(String(20))
    researchInterests = Column(Text)
    email = Column(String(255))