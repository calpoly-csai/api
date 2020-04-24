# http://bytefish.de/blog/first_steps_with_sqlalchemy/
# https://docs.sqlalchemy.org/en/13/
# https://www.sqlalchemy.org/library.html
# ^ if 1.3 is not current release

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from datetime import datetime, timedelta  # noqa
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey  # noqa
from sqlalchemy.orm import relationship, backref  # noqa
from sqlalchemy.orm import sessionmaker
from pprint import pprint as pp
from sqlalchemy import inspect
import json

Base = declarative_base()


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    def __repr__(self):
        return "<Tag (name={})>".format(self.name)


# connection
# https://docs.sqlalchemy.org/en/13/dialects/mysql.html#module-sqlalchemy.dialects.mysql.mysqlconnector
# engine = create_engine('mysql+mysqlconnector://USERNAME:PASSWORD@HOST_NAME:3306/DATABASE_NAME')  # noqa
config_file = "config.json"
with open(config_file) as json_data_file:
    config = json.load(json_data_file)

if config.get("mysql", False):
    mysql_config = config["mysql"]
    RDBMS = "mysql"
    PIP_PACKAGE = "mysqlconnector"
    SQLALCHEMY_DATABASE_URI = "{}+{}://{}:{}@{}:{}/{}".format(
        RDBMS,
        PIP_PACKAGE,
        mysql_config["user"],
        mysql_config["password"],
        mysql_config["host"],
        mysql_config["port"],
        mysql_config["database"],
    )
    engine = create_engine(SQLALCHEMY_DATABASE_URI)

    if engine is None:
        print("failed to connect to MySQL")
        exit(1)
else:
    print("bad config file")
    exit(1)

# create metadata
Base.metadata.create_all(engine)

# create session
Session = sessionmaker(bind=engine)
session = Session()

# insert data
tag_cool = Tag(name="cool")
tag_car = Tag(name="car")
tag_animal = Tag(name="animal")

print("TAGS!!")
print(tag_cool)
print(tag_car)
print(tag_animal)
print()

# notice the `_new` key in the dictionary
session.add_all([tag_animal, tag_car, tag_cool])
pp(session.__dict__)
session.commit()

# query data
t1 = session.query(Tag).filter(Tag.name == "cool").first()

print("T1!!")
print(t1)
print()

# update entity
t1.name = "cool-up"
print("T1 again!! notice `cool-up`")
print(t1)
print()
pp(session.__dict__)
session.commit()

print("T1 again after commit!!")
print(t1)
print()

# delete
# notice the `_deleted` key inside the dictionary
session.delete(t1)
pp(session.__dict__)
session.commit()

inspector = inspect(engine)
print("table names", inspector.get_table_names())

print("dropping table Tag")
# https://www.pythonsheets.com/notes/python-sqlalchemy.html#drop-a-table
# https://stackoverflow.com/questions/35918605/how-to-delete-a-table-in-sqlalchemy  # noqa
print(Tag.__table__.drop(engine))
print("dropped??")

print("table names", inspector.get_table_names())
