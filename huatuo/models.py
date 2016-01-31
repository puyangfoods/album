from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    SmallInteger,
)

from huatuo.database import Base


class Bundle(Base):
    __tablename__ = 'bundle'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    theme = Column(String(255))
    cover = Column(String(255))
    created_at = Column(DateTime)
    rating = Column(Integer, default=0)
