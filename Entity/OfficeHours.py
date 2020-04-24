from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

# This is the way SQLAlchemy initializes their special classes
Base = declarative_base()


class OfficeHours(Base):
    __tablename__ = "OfficeHours"

    id = Column(Integer, primary_key=True)
    Name = Column(Text)
    Office = Column(Text)
    Email = Column(Text)
    Monday = Column(Text)
    Tuesday = Column(Text)
    Wednesday = Column(Text)
    Thursday = Column(Text)
    Friday = Column(Text)
    OfficeHours = Column(Text)
    Phone = Column(Text)
    Platform = Column(Text)
    LatestQuarter = Column(Text)

    def __repr__(self):
        return "<Office Hours (Name={}, Office={}, Email={}, Monday={}, Tuesday={}, Wednesday={}, Thursday={}, Friday={})>".format(
            self.Name,
            self.Office,
            self.Email,
            self.Monday,
            self.Tuesday,
            self.Wednesday,
            self.Thursday,
            self.Friday,
        )


if __name__ == "__main__":

    oh = OfficeHours()

    print(oh)
