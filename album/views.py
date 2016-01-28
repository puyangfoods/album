#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import hashlib
import os
import random
import urlparse

from PIL import Image

from sqlalchemy import (
    func,
    desc,
    asc
)

from flask import (
    send_from_directory, render_template, redirect, request, url_for
)

from werkzeug import secure_filename

from album import app
from album.database import db_session
from album.tools import (
    limit_pic_size,
    pk_rating,
    Pagination
)

from album.models import (
    Pic,
    PicVote,
    Bundle,
    BundleTag,
    BundleCouple,
)


def _fill_bundles_cover(bundles):
    bundle_ids = [bundle.id for bundle in bundles]
    pics = Pic.query.\
        filter(Pic.bundle_id.in_(bundle_ids)).\
        group_by(Pic.bundle_id)

    pic_dict = {}

    # should sync with cover css
    fixed_width = 190
    for pic in pics:
        if not pic.width:
            pic.width = 10
            pic.height = 10
        height = pic.height / (pic.width * 1.0 / fixed_width)
        pic_dict[pic.bundle_id] = {
            'hash': pic.hash,
            'width': '{}px'.format(fixed_width),
            'height': '{}px'.format(height),
        }

    for bundle in bundles:
        bundle.pic_dict = pic_dict[bundle.id]
        if len(bundle.name) > 10:
            bundle.name = bundle.name[:9] + '..'

    return bundles


@app.route('/')
@app.route('/all')
def bundles():
    page = int(request.args.get('page', 1))
    count = db_session().query(func.count(Bundle.id)).scalar()
    per_page = 100
    bundles = Bundle.query.\
        order_by(desc(Bundle.rating), desc(Bundle.id)).\
        offset((page - 1) * per_page).\
        limit(per_page).\
        all()
    bundles = _fill_bundles_cover(bundles)
    pagination = Pagination(page, per_page, count, request.base_url,
                            urlparse.parse_qsl(request.query_string))
    if page == 1:
        recent_bundles = Bundle.query.\
            filter(Bundle.created_at <= datetime.date.today()).\
            order_by(desc(Bundle.created_at)).\
            limit(6).\
            all()
    else:
        recent_bundles = []
    return render_template('bundles.html',
                           recent_bundles=recent_bundles,
                           bundles=bundles,
                           pagination=pagination)


@app.route('/tag/<string:tag>')
def tag_bundles(tag):
    bundle_ids = [
        t[0] for t in
        db_session.query(BundleTag.bundle_id).
        filter(BundleTag.tag.like(u'%{}%'.format(tag))).all()]
    count = len(bundle_ids)
    page = int(request.args.get('page', 1))

    per_page = 100
    bundles = db_session().query(Bundle).\
        filter(Bundle.id.in_(bundle_ids)).\
        order_by(desc(Bundle.rating), desc(Bundle.id)).\
        offset((page - 1) * per_page).\
        limit(per_page).\
        all()
    bundles = _fill_bundles_cover(bundles)
    pagination = Pagination(page, per_page, count, request.base_url,
                            urlparse.parse_qsl(request.query_string))

    return render_template('tag_bundles.html',
                           bundles=bundles,
                           pagination=pagination)


@app.route('/tags')
def tag_index():
    res = db_session.query(BundleTag.tag,
                           func.count(BundleTag.bundle_id).label('count')).\
        group_by(BundleTag.tag).\
        order_by(desc('count')).\
        all()
    return render_template('tag_index.html', tag_count_list=res)


@app.route('/top')
def top():
    pics = Pic.query.order_by(desc(Pic.rating)).limit(20)
    bundle_ids = [pic.bundle_id for pic in pics]
    bundles = Bundle.query.filter(Bundle.id.in_(bundle_ids))
    bundle_dict = {bundle.id: bundle for bundle in bundles}
    print bundle_dict

    return render_template('top.html', pics=pics, bundle_dict=bundle_dict)


@app.route('/bundle/<int:bundle_id>', defaults={'page': 1})
@app.route('/bundle/<int:bundle_id>/<int:page>')
def bundle_detail(bundle_id, page):
    pic = Pic.query.filter(Pic.bundle_id == bundle_id).\
        filter(Pic.page == page).\
        first()

    if not pic:
        pic = Pic.query.filter(Pic.bundle_id > bundle_id).first()
        return redirect('/bundle/{0}/1'.format(pic.bundle_id))

    max_page = db_session().query(func.max(Pic.page)).\
        filter(Pic.bundle_id == bundle_id).\
        scalar() or 1

    next_page = {'bundle_id': bundle_id, 'page': int(page) + 1}
    if max_page == page:
        next_page['bundle_id'] = db_session().query(Pic.bundle_id).\
            filter(Pic.bundle_id > bundle_id).\
            limit(1).\
            scalar()
        next_page['page'] = 1

    bundle = Bundle.query.filter(Bundle.id == pic.bundle_id).first()
    tags = [t[0] for t in
            db_session.query(BundleTag.tag).
            filter(BundleTag.bundle_id == bundle_id)]
    pagination = Pagination(page, 1, max_page, request.base_url,
                            urlparse.parse_qsl(request.query_string))

    return render_template('bundle_detail.html',
                           pic=pic, bundle=bundle, tags=tags,
                           next_page=next_page,
                           pagination=pagination)


def do_pk():
    win = request.form.getlist('win')[0]
    lose = request.form.getlist('lose')[0]

    too_frequent = False

    one_min_ago = datetime.datetime.now() - datetime.timedelta(minutes=1)
    ip_vote_count = db_session.query(func.count(PicVote.id)).\
        filter(PicVote.ip == request.remote_addr).\
        filter(PicVote.created_at > one_min_ago).\
        scalar()

    # single ip 10 votes per minute
    if ip_vote_count > 25:
        too_frequent = True

    if not too_frequent:
        vote_ids = [win, lose]
        same_vote = PicVote.query.\
            filter(PicVote.win_id.in_(vote_ids)).\
            filter(PicVote.lose_id.in_(vote_ids)).\
            filter(PicVote.ip == request.remote_addr).\
            filter(PicVote.created_at > datetime.date.today()).\
            first()

        if same_vote:
            too_frequent = True

    if not too_frequent:
        vote = PicVote(
            win_id=win,
            lose_id=lose,
            ip=request.remote_addr,
            created_at=datetime.datetime.now()
        )
        db_session.add(vote)

        win_pic = Pic.query.filter(Pic.id == win).first()
        lose_pic = Pic.query.filter(Pic.id == lose).first()

        updated_rating = pk_rating(
            {'win': win_pic.rating, 'lose': lose_pic.rating})

        win_pic.rating = updated_rating['win']
        lose_pic.rating = updated_rating['lose']

        win_bundle = Bundle.query.\
            filter(Bundle.id == win_pic.bundle_id).\
            first()
        lose_bundle = Bundle.query.\
            filter(Bundle.id == lose_pic.bundle_id).\
            first()

        updated_rating = pk_rating(
            {'win': win_bundle.rating, 'lose': lose_bundle.rating})

        win_bundle.rating = updated_rating['win']
        lose_bundle.rating = updated_rating['lose']

        db_session.commit()

    return win


@app.route('/pk', methods=['GET', 'POST'])
def pk():
    if request.method == 'POST':
        win_pic_id = do_pk()
    else:
        win_pic_id = ''
    win_pic_id = ''
    if win_pic_id:
        pic1 = Pic.query.get(win_pic_id)
    else:
        pic1 = db_session.query(Pic).\
            order_by(func.rand()).\
            first()

    pic2 = db_session.query(Pic)

    if pic1.width / pic1.height >= 1:
        pic2 = pic2.filter(Pic.width / Pic.height >= 1)
    else:
        pic2 = pic2.filter(Pic.width / Pic.height < 1)

    pic2 = pic2.order_by(func.rand()).\
        first()

    pics = [pic1, pic2]

    for pic in pics:
        pic.bundle = Bundle.query.get(pic.bundle_id)

    return render_template('pk.html',
                           pics=pics)


@app.route('/similar/<int:id>')
def similar(id):
    couple = BundleCouple.query.filter(BundleCouple.id >= id).\
        order_by(asc(BundleCouple.id)).first()
    bundle1 = Bundle.query.get(couple.bundleid1)
    pics1 = Pic.query.filter(Pic.bundle_id == couple.bundleid1).\
        all()

    bundle2 = Bundle.query.get(couple.bundleid2)
    pics2 = Pic.query.filter(Pic.bundle_id == couple.bundleid2).\
        all()

    next_id = db_session.query(BundleCouple.id).filter(BundleCouple.id > id).\
        order_by(asc(BundleCouple.id)).first()[0]

    return render_template('similar.html', pics1=pics1, pics2=pics2,
                           bundle1=bundle1, bundle2=bundle2, next_id=next_id)


@app.route("/uploadbundle", methods=['GET', 'POST'])
def uploadbundle():
    ALLOWED_EXTENSIONS = set(['jpg'])

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    def getMD5(source):
        m = hashlib.md5()
        m.update(source)
        return m.hexdigest()

    def random_number(length):
        assert(length > 0)
        return random.randrange(10 ** (length - 1), 10 ** length)

    if request.method == 'POST':
        files = request.files.getlist('file[]')
        if len(files) > 3:
            bundle_name = request.form['bundle_name']
            tags = request.form['tags'].split()
            theme = request.form['theme']
            created_at = request.form['created_at']
            password = request.form['password']
        else:
            return redirect(url_for('uploadbundle'))

        if password != 'jojopakman$ecret':
            return redirect(url_for('uploadbundle'))

        bundle = Bundle(
            name=bundle_name,
            theme=theme,
            created_at=created_at,
        )
        db_session.add(bundle)
        db_session.flush()

        for t in tags:
            tag = BundleTag(
                bundle_id=bundle.id,
                tag=t,
                created_at=datetime.datetime.now()
            )
            db_session.add(tag)

        page = 1
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                #TODO regenerate if collide
                hash_name = getMD5('{0}{1:%Y%m%d%H%M%S}{2}'.format(
                    name, datetime.datetime.now(), random_number(9)))
                new_name = '{0}{1}'.format(hash_name, ext)

                full_path = os.path.join(
                    app.config['IMAGE_FOLDER'],
                    '{0}{1}'.format(hash_name, ext))
                img = Image.open(file).convert("RGB")
                width, height = img.size
                new_width, new_height = limit_pic_size(width, height)
                if width != new_width:
                    img = img.resize((new_width, new_height), Image.ANTIALIAS)
                img.save(full_path, quality=100)
                pic = Pic(
                    bundle_id=bundle.id,
                    hash=new_name,
                    page=page,
                    width=new_width,
                    height=new_height,
                    rating=0,
                )
                db_session.add(pic)
                page += 1
        db_session.commit()
        return redirect(url_for('bundle_detail', bundle_id=bundle.id))
    return render_template('uploadbundle.html')


@app.route('/sitemap')
def sitemap_index():
    pass


@app.route('/sitemap/bundles')
def sitemap_bundle():
    pass


@app.route('/images/<path:filename>')
def send_pic(filename):
    return send_from_directory(app.config['IMAGE_FOLDER'], filename)


@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
