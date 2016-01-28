from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    SmallInteger,
)

from album.database import Base


class Bundle(Base):
    __tablename__ = 'bundle'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    theme = Column(String(255))
    cover = Column(String(255))
    created_at = Column(DateTime)
    rating = Column(Integer, default=0)


class BundleTag(Base):
    __tablename__ = 'bundle_tag'

    id = Column(Integer, primary_key=True)
    bundle_id = Column(Integer)
    tag = Column(String(255))
    created_at = Column(DateTime)


class Pic(Base):
    __tablename__ = 'pic'

    id = Column(Integer, primary_key=True)
    bundle_id = Column(Integer)
    hash = Column(String(255))
    page = Column(SmallInteger)
    width = Column(Integer)
    height = Column(Integer)
    rating = Column(Integer, default=0)


class PicVote(Base):
    __tablename__ = 'pic_vote'

    id = Column(Integer, primary_key=True)
    win_id = Column(Integer)
    lose_id = Column(Integer)
    ip = Column(String(45))
    created_at = Column(DateTime)


class BundleCouple(Base):
    __tablename__ = 'bundle_couple'

    id = Column(Integer, primary_key=True)
    bundleid1 = Column(Integer)
    bundleid2 = Column(Integer)
