#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import json
import os
import requests
import urllib

from PIL import Image

from flask.ext.script import Manager
from sqlalchemy import (
    func,
    or_,
    asc,
)

from album import app
from album.database import db_session
from album.models import (
    Pic,
    Bundle,
    PicVote,
    BundleCouple,
)
from album.tools import (
    limit_pic_size,
)

manager = Manager(app)


COVER_WIDTH = 180
COVER_HEIGHT = 270


@manager.command
def detect_face(bundle_id, page):
    pic = Pic.query.\
        filter(Pic.bundle_id == bundle_id, Pic.page == page).first()
    pic_url = 'http://meinvpai.in/images/{}'.format(pic.hash)
    api_url = 'http://apicn.faceplusplus.com/detection/detect'
    params = {
        'api_key': app.config['FACEPP_API_KEY'],
        'api_secret': app.config['FACEPP_API_SECRET'],
        'url': pic_url,
        'mode': 'oneface',
        'attribute': 'pose'
    }
    r = requests.get('{0}?{1}'.format(api_url, urllib.urlencode(params)))
    print json.dumps(r.json(), indent=4)


# fill the pic's width and height data
@manager.command
def fill_image_size():
    pics = Pic.query.all()
    for pic in pics:
        try:
            width, height = Image.open(
                app.config['STATIC_FOLDER'] + pic.hash).size
            pic.width = width
            pic.height = height
        except:
            print pic.bundle_id

    db_session.commit()



if __name__ == "__main__":
    manager.run()
