#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import hashlib
import os
import random
import urlparse

from sqlalchemy import (
    func,
    desc,
    asc
)

from flask import (
    send_from_directory, render_template, redirect, request, url_for
)

from werkzeug import secure_filename

from huatuo import app
from huatuo.database import db_session
from huatuo.tools import (
    limit_pic_size,
    pk_rating,
    Pagination
)

from huatuo.models import (
    Bundle,
)


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

@app.route('/sitemap')
def sitemap_index():
    pass


@app.route('/sitemap/bundles')
def sitemap_bundle():
    pass


@app.route('/images/<path:filename>')
def send_pic(filename):
    return send_from_directory(app.config['IMAGE_FOLDER'], filename)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
