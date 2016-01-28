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


@manager.command
def fill_bundle_rating():
    bundles = Bundle.query

    for bundle in bundles:
        total_rating = db_session.query(func.sum(Pic.rating)).\
            filter(Pic.bundle_id == bundle.id).\
            scalar() or 0
        bundle.rating = total_rating
    db_session.commit()


@manager.command
def remove_bundle(bundle_id):
    bundle = Bundle.query.get(bundle_id)

    if not bundle:
        print 'Bundle not found'
        return False
    print bundle.name
    y_or_n = raw_input('y or n-->')

    if 'y' not in y_or_n.lower():
        return False

    db_session.delete(bundle)

    pics = Pic.query.filter(Pic.bundle_id == bundle_id)
    pic_ids = []
    for pic in pics:
        print 'remove pic:{}'.format(pic.id)
        pic_ids.append(pic.id)
        db_session.delete(pic)

    votes = PicVote.query.filter(or_(PicVote.win_id.in_(pic_ids),
                                     PicVote.lose_id.in_(pic_ids)
                                     ))
    for vote in votes:
        print 'remove vote of pics: {0}, {1}'.format(vote.win_id, vote.lose_id)
        db_session.delete(vote)

    db_session.commit()


@manager.command
def remove_pic(pic_id):
    pic = Pic.query.get(pic_id)

    pics = Pic.query.filter(Pic.bundle_id == pic.bundle_id).\
        order_by(asc(Pic.page)).all()
    page = 1
    for p in pics:
        if p.id != pic.id:
            p.page = page
            page += 1

    db_session.delete(pic)

    db_session.commit()


@manager.command
def resize_pics():
    bundle_ids = [bundle.id for bundle in Bundle.query.all()]
    db_session.commit()

    for bundle_id in bundle_ids:
        pics = Pic.query.filter(Pic.bundle_id == bundle_id).all()
        for pic in pics:
            pic_file_path = os.path.join(
                app.config['IMAGE_FOLDER'],
                '{0}'.format(pic.hash))
            try:
                img = Image.open(pic_file_path).convert("RGB")
            except:
                print pic.id, pic.bundle_id, pic.page
                continue
            width, height = img.size
            new_width, new_height = limit_pic_size(width, height)
            if width != new_width:
                img = img.resize((new_width, new_height), Image.ANTIALIAS)
            img.save(pic_file_path, quality=100)
            pic.width = new_width
            pic.height = new_height

        db_session.commit()


@manager.command
def make_cover():
    def get_cover_size(width, height):
        width_ratio = width * 1.0 / COVER_WIDTH
        height_ratio = height * 1.0 / COVER_HEIGHT
        if width_ratio > height_ratio:
            r_height = COVER_HEIGHT
            r_width = width / (height * 1.0 / COVER_HEIGHT)
        else:
            r_width = COVER_WIDTH
            r_height = height / (width * 1.0 / COVER_WIDTH)

        return int(r_width), int(r_height)

    bundle_ids = [bundle.id for bundle in Bundle.query.all()]
    db_session.commit()

    for bundle_id in bundle_ids:
        bundle = Bundle.query.get(bundle_id)
        pic = Pic.query.filter(Pic.bundle_id == bundle_id).\
            filter(Pic.height / Pic.width > 1).first()
        if not pic:
            print bundle_id
            continue

        pic_file_path = os.path.join(
            app.config['IMAGE_FOLDER'],
            '{0}'.format(pic.hash))
        try:
            img = Image.open(pic_file_path).convert("RGB")
        except:
            print pic.id, pic.bundle_id, pic.page
            continue

        width, height = img.size
        new_width, new_height = get_cover_size(width, height)
        img = img.resize((new_width, new_height), Image.ANTIALIAS)

        if new_width == COVER_WIDTH and new_height != COVER_HEIGHT:
            height_cut = (new_height - COVER_HEIGHT) / 2
            img = img.crop((0, height_cut, COVER_WIDTH,
                           height_cut + COVER_HEIGHT))
        elif new_height == COVER_HEIGHT and new_width != COVER_WIDTH:
            width_cut = (new_width - COVER_WIDTH) / 2
            img = img.crop((width_cut, 0, width_cut + COVER_WIDTH,
                           COVER_HEIGHT))

        m = hashlib.md5()
        m.update(pic.hash)
        name, ext = os.path.splitext(pic.hash)
        cover_hash = m.hexdigest() + ext
        cover_path = os.path.join(
            app.config['IMAGE_FOLDER'],
            'cover/{0}'.format(cover_hash))
        img.save(cover_path, quality=100)
        bundle.cover = cover_hash

        db_session.commit()


@manager.command
def compare_pic():
    """Compare two aligned images of the same size.

    Usage: python compare.py first-image second-image
    """
    from scipy import sum, average
    from numpy import asarray

    matrix_dict = {}

    def compare_images(img1, img2):
        # calculate the difference and its norms
        diff = img1 - img2  # elementwise for scipy arrays
        m_norm = sum(abs(diff))  # Manhattan norm
        return m_norm

    def to_grayscale(arr):
        "If arr is a color image (3D array),"
        " convert it to grayscale (2D array)."
        if len(arr.shape) == 3:
            # average over the last axis (color channels)
            return average(arr, -1)
        else:
            return arr

    def normalize(arr):
        rng = arr.max()-arr.min()
        amin = arr.min()
        return (arr-amin)*255/rng

    def get_matrix(pic_id):
        if pic_id not in matrix_dict:
            pic = db_session.query(Pic.hash).filter(Pic.id == pic_id).scalar()
            f = Image.open(app.config['STATIC_FOLDER'] + pic).\
                convert("RGB").resize((128, 128))
            # read images as 2D arrays (convert to grayscale for simplicity)
            matrix_dict[pic_id] = normalize(to_grayscale(asarray(f)))
        return matrix_dict[pic_id]

    pic_ids = [id[0] for id in
               db_session.query(Pic.id).
               filter(Pic.width / Pic.height < 1).order_by(Pic.id)]
    #pic_ids = [67, 68]
    print len(pic_ids)
    c = 0

    with open('similar2', 'w+') as f:
        for i in range(0, len(pic_ids)):
            for j in range(i + 1, len(pic_ids)):
                c += 1
                if c % 10000 == 0:
                    print c

                try:
                    img1 = get_matrix(pic_ids[i])
                    img2 = get_matrix(pic_ids[j])
                except:
                    print pic_ids[i], pic_ids[j]
                    continue
                n_m = compare_images(img1, img2)/128/128
                if n_m < 12:
                    f.write(
                        '{0} {1} {2}\n'.format(pic_ids[i], pic_ids[j], n_m))


@manager.command
def convert():
    couple_set = set()
    with open('similar2') as f:
        for l in f:
            picid1, picid2, similarity = tuple(l.split())
            if float(similarity) == 0 or 12 > float(similarity) < 10:
                continue

            pics = Pic.query.filter(Pic.id.in_([picid1, picid2])).all()
            if len(pics) != 2:
                continue
            if pics[0].bundle_id == pics[1].bundle_id:
                continue

            if pics[0].bundle_id < pics[1].bundle_id:
                couple_set.add((pics[0].bundle_id, pics[1].bundle_id))
            else:
                couple_set.add((pics[1].bundle_id, pics[0].bundle_id))

    for couple in couple_set:
        c = BundleCouple(
            bundleid1=couple[0],
            bundleid2=couple[1]
        )
        db_session.add(c)
        print couple

    db_session.commit()


if __name__ == "__main__":
    manager.run()
