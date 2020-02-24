from builtins import str

from sqlalchemy import Column, Integer, String, Text, Enum,
from sqlalchemy.ext.declarative import declarative_base
import enum
from sqlalchemy.dialects.mysql import SET

'''
Column types of 'Clubs' table gathered from SQLWorkbench

idClubs int(11) AI PK
types varchar(255)
desc text
contactEmail varchar(45)
contactEmail2 varchar(45)
contactPerson varchar(45)
contactPhone varchar(15)
box varchar(45)
advisorId int(11) #foreign id 
affiliation varchar(255)
'''

Base = declarative_base()

class Clubs(enum.Enum):
    __tablename__ = "Clubs"
    id_clubs = Column(Integer, primary_key = True)
    club_name = Column(String(512)) #Added club_name
    types = Column(String(255))
    desc = Column(Text)
    contact_email = Column(String(45))
    contact_email_2 = Column(String(45))
    contact_person = Column(String(45))
    contact_phone = Column(String(15))
    box = Column(String(45))
    advisor_id = Column(Integer)
    affiliation = Column(String(255))

    def __repr__(self):
        return "<Clubs (id = {}, "
'''
class Clubs:
    def __init__(self, idClubs, types, desc, contactEmail, contactEmail2,
                 contactPerson, contactPhone, box, advisorId, affiliation):
        self.idClubs = idClubs
        self.types = types
        self.desc = desc
        self.contactEmail = contactEmail
        self.contactEmail2 = contactEmail2
        self.contactPerson = contactPerson
        self.contactPhone = contactPhone
        self.box = box
        self.advisorId = advisorId
        self.affiliation = affiliation
'''