from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from Entity.Entity import Entity

Base = declarative_base()


class EntityToken(Entity, Base):
    __tablename__ = "EntityTokens"
    __mapper_args__ = {"concrete": True}
    id = Column(String(32), primary_key=True)
    description = Column(Text)
    name = Column(String(64))

    def validate(self, data):
        required_fields = ["id", "description", "name"]
        for field in required_fields:
            if field not in data:
                raise Exception(
                    f"Required field `{field}` wasn't provided. Please provide the following[{required_fields}]"
                )

    def format(self, data) -> dict:
        form = data.copy()
        for key in form:
            form[key] = str(form[key])
        return form

    def get_data(self):
        return {"name": self.name, "description": self.description, "id": self.id}
