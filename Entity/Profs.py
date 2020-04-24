from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

# This is the way SQLAlchemy initializes their special classes
Base = declarative_base()


class Profs(Base):
    __tablename__ = "Profs"
    firstName = Column(String(50), primary_key=True)
    lastName = Column(String(50))
    phoneNumber = Column(String(20))
    researchInterests = Column(Text)
    email = Column(String(255))
    OfficeHours = Column(Text)
    Platform = Column(Text)
    LatestQuarter = Column(Text)
    Office = Column(Text)
    department = Column(String(255))
    title = Column(String(255))

    def __repr__(self):
        D = self.__dict__
        attributes = [
            f"{k}={D.get(k)}" for k in self.__dir__() if not k.startswith("_")
        ]
        attributes_string = ", ".join(attributes)
        return f"{self.__class__.__name__}({attributes_string})"