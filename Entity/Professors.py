from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
import enum

# This is the way SQLAlchemy initializes their special classes
Base = declarative_base()


class Professors(Base):
    __tablename__ = "Professors"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone_number = Column(String(20))
    research_interests = Column(Text)
    email = Column(String(255))
    is_view = False

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        D = self.__dict__
        attributes = [
            f"{k}={D.get(k)}" for k in self.__dir__() if not k.startswith("_")
        ]
        attributes_string = ", ".join(attributes)
        return f"{self.__class__.__name__}({attributes_string})"


class ProfessorsProperties(enum.Enum):
    first_name = Professors.first_name
    last_name = Professors.last_name
    phone_number = Professors.phone_number
    research_interests = Professors.research_interests
    email = Professors.email
