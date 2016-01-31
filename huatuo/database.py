#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#from huatuo.settings import SQLALCHEMY_MYSQL_URI_PARAMS
from huatuo import app

engine = create_engine(
    "mysql+pymysql://{username}:{password}@{hostname}:{port}/{dbname}"
    "?charset=utf8".format(**app.config['SQLALCHEMY_MYSQL_URI_PARAMS']))

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from huatuo import models
    Base.metadata.create_all(bind=engine)
