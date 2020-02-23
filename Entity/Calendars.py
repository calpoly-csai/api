from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

# This is the way SQLAlchemy initializes their special classes	
Base = declarative_base()

class Calendars(Base):
    __tablename__ = 'Calendars'

    calendar_id = Column(Integer, primary_key=True)
    date = Column(String(10))
    day = Column(Integer)
    month = Column(String(10))
    year = Column(Integer)
    raw_events_text = Column(Text)


    def __repr__(self):
        return "<Calendars (date={}, events={})>".format(
            self.date, self.raw_events_text)
        