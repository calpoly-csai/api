from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import SET
import enum

# This is the way SQLAlchemy initializes their special classes
Base = declarative_base()


class CollegeStanding(enum.Enum):
    """
    https://docs.sqlalchemy.org/en/13/core/type_basics.html#sqlalchemy.types.Enum
    """

    first_year = freshman = FR = 1  # 'FReshman'
    second_year = sophomore = SO = 2  # 'SOphomore'
    third_year = junior = JR = 3  # 'JunioR'
    fourth_year = senior = SR = 4  # 'SenioR'
    graduate = GR = 5  # 'GRaduate'
    not_applicable = NA = 6  # 'NotApplicable/Unknown'


class Courses(Base):
    __tablename__ = "Courses"
    # TODO: update schema and this Courses class to follow snake_case convention
    id = Column(Integer, primary_key=True)
    dept = Column(String(5))
    courseNum = Column(Integer)
    termsOffered = Column(SET("F", "W", "SP", "SU", "TBD"))
    units = Column(String(5))
    courseName = Column(String(255))
    raw_concurrent_text = Column(Text)
    raw_recommended_text = Column(Text)
    raw_prerequisites_text = Column(Text)

    def __repr__(self):
        return "<Courses (dept={}, course_num={})>".format(self.dept, self.courseNum)
