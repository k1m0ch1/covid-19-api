from flask_login import UserMixin
from sqlalchemy import Column, MetaData, ForeignKey
from sqlalchemy import String, Text, DateTime, Integer, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import Timestamp, EmailType
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
import shortuuid

NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata, cls=Timestamp)


def ServerTimestamp(cannull):
    return Column(
        DateTime(timezone=False),
        nullable=cannull,
        server_default=text("(now() at time zone 'utc')")
    )


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(String(22), primary_key=True, default=shortuuid.uuid)
    name = Column(String(100), unique=True)
    email = Column(EmailType, unique=True, nullable=True)
    birthdate = Column(Date, nullable=True)
    phone = Column(String(16), nullable=True)
    created = ServerTimestamp(False)
    updated = ServerTimestamp(True)

    def get_id(self):
        return self.id


class Place(Base):
    __tablename__ = 'places'

    id = Column(String(22), primary_key=True, default=shortuuid.uuid)
    name = Column(Text, nullable=False)
    lng = Column(String(50), nullable=False)
    lat = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    created = ServerTimestamp(False)
    updated = ServerTimestamp(True)

    story = relationship("Story")


class Story(Base):
    __tablename__ = 'stories'

    id = Column(String(100), primary_key=True, default=shortuuid.uuid)
    place_id = Column(String(100), ForeignKey(Place.id), nullable=False)
    user_id = Column(String(100), ForeignKey(User.id), nullable=True)
    availability = Column(String(100), nullable=False)
    num = Column(Integer(), nullable=True)
    price = Column(Integer(), nullable=True)
    validity = Column(String(50), nullable=True)
    created = ServerTimestamp(False)
    updated = ServerTimestamp(True)
