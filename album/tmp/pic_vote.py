from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

from album.database import Base


class PicVote(Base):
    __tablename__ = 'pic_vote'

    id = Column(Integer, primary_key=True)
    win_id = Column(Integer)
    lose_id = Column(Integer)
    ip = Column(String(45))
    created_at = Column(DateTime, default=datetime.datetime.now())
