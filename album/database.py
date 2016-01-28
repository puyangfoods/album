#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#from album.settings import SQLALCHEMY_MYSQL_URI_PARAMS
from album import app

engine = create_engine(
    "mysql://{username}:{password}@{hostname}:{port}/{dbname}"
    "?charset=utf8".format(**app.config['SQLALCHEMY_MYSQL_URI_PARAMS']))

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from album import models
    Base.metadata.create_all(bind=engine)
