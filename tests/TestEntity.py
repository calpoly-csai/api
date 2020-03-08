from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TestEntity(Base):
    __tablename__ = "Test"
    entity_id = Column(Integer, primary_key=True)
    value_one = Column(String(64))
    value_two = Column(String(64))
    value_three = Column(String(64))

    def __repr__(self):
        return "<TestEntity (value_one={}, value_two={}, value_three={})>".format(
            self.value_one, self.value_two, self.value_three
        )
