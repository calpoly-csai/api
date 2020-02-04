from sqlalchemy import Column, Integer, String, Text, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
import enum

# This is the way SQLAlchemy initializes their special classes
Base = declarative_base()


class NoiseLevel(enum.Enum):
    quiet = 1
    medium = 2
    loud = 3


class AudioSampleMetaData(Base):
    __tablename__ = 'AudioSampleMetaData'
    id = Column(Integer, primary_key=True)
    # I think... SQLAlchemy will resolve this to TINYINT in MYSQL
    is_wake_word = Column(Boolean)
    # TODO: run a magical SQL script that support emojis in first_name
    first_name = Column(String(255))
    last_name = Column(String(255))
    gender = Column(String(3))
    noise_level = Column(Enum(NoiseLevel))
    location = Column(String(255))
    tone = Column(String(255))
    timestamp = Column(Integer)
    username = Column(String(255))
    # Text chosen because filename is standarized concatenation of above fields
    filename = Column(Text)

    def __repr__(self):
        string = "<AudioSampleMetaData ( id={}, is_wake_word={}, "
        string += "first_name={}, last_name={}, gender={}, noise_level={}, "
        string += "location={}, tone={}, timestamp={}, username={} )>"
        return (string.format(self.id, self.is_wake_word, self.first_name,
                              self.last_name, self.gender, self.noise_level,
                              self.location, self.tone, self.timestamp,
                              self.username))
