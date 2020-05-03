from sqlalchemy import Column, Integer, String, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import SET
import enum

Base = declarative_base()


class SectionType(enum.Enum):
    activity = Act = 0
    seminar = Sem = 1
    independent = Ind = 2
    lab = 3
    lecture = Lec = 4


class ProfessorSectionView(Base):
    __tablename__ = "Professor_Teaches_Section"
    id = Column(Integer, primary_key=True)
    id_sections = Column(Integer)
    profAliasId = Column(Integer)
    section_name = Column(String(255))
    instructor = Column(String(255))
    profEmailAlias = Column(String(255))
    title = Column(String(255))
    phone = Column(String(255))
    office = Column(String(255))
    type = Column(Enum(SectionType))
    days = Column(SET("M", "T", "W", "R", "F"))
    start = Column(String(255))
    end = Column(String(255))
    location = Column(String(255))
    department = Column(String(255))
    firstName = Column(String(50))
    lastName = Column(String(50))
    phoneNumber = Column(String(20))
    researchInterests = Column(Text)
    email = Column(String(255))
    is_view = True

    def __repr__(self):
        D = self.__dict__
        attributes = [
            f"{k}={D.get(k)}" for k in self.__dir__() if not k.startswith("_")
        ]
        attributes_string = ", ".join(attributes)
        return f"{self.__class__.__name__}({attributes_string})"
