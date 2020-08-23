from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

# This is the way SQLAlchemy initializes their special classes
Base = declarative_base()


class Profs(Base):
    __tablename__ = "Profs"
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone_number = Column(String(20))
    research_interests = Column(Text)
    email = Column(String(255), primary_key=True)
    office_hours = Column(Text)
    platform = Column(Text)
    latest_quarter = Column(Text)
    office = Column(Text)
    department = Column(String(255))
    title = Column(String(255))
    is_view = True
    synonyms = ["professors", "teachers", "lecturers", "faculty", "staff", "administration", "instructors", "educators", "TA"]

    def __repr__(self):
        D = self.__dict__
        attributes = [
            f"{k}={D.get(k)}" for k in self.__dir__() if not k.startswith("_")
        ]
        attributes_string = ", ".join(attributes)
        return f"{self.__class__.__name__}({attributes_string})"
