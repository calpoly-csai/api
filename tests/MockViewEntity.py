from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class MockViewEntity(Base):
    __tablename__ = "Test"
    entity_id = Column(Integer, primary_key=True)
    value_one = Column(String(64))
    value_two = Column(String(64))
    value_three = Column(String(64))
    is_view = True

    def __repr__(self):
        return "<MockViewEntity (value_one={}, value_two={}, value_three={})>".format(
            self.value_one, self.value_two, self.value_three
        )
