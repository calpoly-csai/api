from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from Entity.EntityToken import EntityToken # unsure about this import

Base = declarative_base()


class EntitySynonyms(EntityToken, Base):
    __tablename__ = "EntitySynonyms"
    __mapper_args__ = {"concrete": True}
    id = Column(Integer, primary_key=True)
    synonym = Column(String(64))
    entity = Column(String(64), ForeignKey("EntityToken.id"))

    def validate(self, data):
        required_fields = ["id", "synonym", "entity"]
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
        return {"synonym": self.synonym, "entity": self.entity, "id": self.id}
