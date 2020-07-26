from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Clubs(Base):
    __tablename__ = "Clubs"
    id_clubs = Column(Integer, primary_key=True)
    club_name = Column(String(255))
    types = Column(String(255))
    desc = Column(Text)
    contact_email = Column(String(255))
    contact_email_2 = Column(String(255))
    contact_person = Column(String(255))
    # TODO: how big can a phone number be including extionsions and formatting?
    contact_phone = Column(String(255))
    box = Column(String(3))
    advisor = Column(String(255))
    affiliation = Column(String(255))
    is_view = False
    synonyms = ["frat", "extracurricular", "group"]

    def __repr__(self):
        D = self.__dict__
        attributes = [
            f"{k}={D.get(k)}" for k in self.__dir__() if not k.startswith("_")
        ]
        attributes_string = ", ".join(attributes)
        return f"{self.__class__.__name__}({attributes_string})"
