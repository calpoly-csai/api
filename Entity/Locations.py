from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Locations(Base):
    __tablename__ = 'Locations'
    location_id = Column(Integer, primary_key = True)
    building_number = Column(String(5))
    name = Column(String(100))
    longitude = Column(String(255))
    latitude = Column(String(255))

    def __repr__(self):
        return "<Locations (building_number = {}, name = {}, longitude = {}, latitude = {})>".format(
            self.building_number, self.name, self.longitude, self.latitude)