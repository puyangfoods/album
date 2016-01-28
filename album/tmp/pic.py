from sqlalchemy import (
    Column,
    Integer,
    String,
)

from album.database import Base


class Pic(Base):
    __tablename__ = 'pic'

    id = Column(Integer, primary_key=True)
    bundle_id = Column(Integer)
    hash = Column(String(255))
    page = Column(SmallInteger)
    width = Column(Integer)
    height = Column(Integer)
    rating = Column(Integer, default=0)
