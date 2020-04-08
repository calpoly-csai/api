from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

# This is the way SQLAlchemy initializes their special classes
Base = declarative_base()

class OfficeHours(Base):
    __tablename__ = "OfficeHours"

    id = Column(Integer, primary_key=True) 
    name = Column(Text)
    office = Column(Text)
    email = Column(Text)
    monday = Column(Text)
    tuesday = Column(Text)
    wednesday = Column(Text)
    thursday = Column(Text)
    friday = Column(Text)

    def __repr__(self):
        return "<Office Hours (Name={}, Office={}, Email={}, Monday={}, Tuesday={}, Wednesday={}, Thursday={}, Friday={})>".format(
            self.name, self.office, self.email, self.monday, self.tuesday, self.wednesday, self.thursday, self.friday)

if __name__ == "__main__":
    
    oh = OfficeHours()

    print(oh)
