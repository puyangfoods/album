#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import urllib
from math import ceil


class Pagination(object):

    def __init__(self, current_page, per_page, total_count,
                 base_url, query):
        self.current_page = current_page
        self.per_page = per_page
        self.total_count = total_count
        self.base_url = base_url
        self.query = query

    @property
    def max_page(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.max_page

    def iter_pages(self):
        for num in xrange(1, self.max_page + 1):
            yield num

    def generate_url(self, page):
        new_query = []
        has_page = False
        for key, value in self.query:
            if key == 'page':
                new_query.append((key, page))
                has_page = True
            else:
                new_query.append((key, value))

        if not has_page:
            new_query.append(('page', page))
        query_string = '?' + urllib.urlencode(new_query) if new_query else ''
        return self.base_url + query_string


def pk_rating(original_rating):
    Rwin = original_rating['win']
    Rlose = original_rating['lose']

    Ewin = 1.0 / (1 + math.pow(10, (Rlose - Rwin) / 400.0))
    Elose = 1.0 / (1 + math.pow(10, (Rwin - Rlose) / 400.0))

    return {'win': Rwin + 16 * (1 - Ewin),
            'lose': Rlose + 16 * (0 - Elose)}


def limit_pic_size(width, height):
    MAX_HEIGHT = 1000.0
    MAX_WIDTH = 1000.0
    width = float(width)
    height = float(height)

    if width / height > 1 and width > MAX_WIDTH:
        ratio = width / MAX_WIDTH
        width = MAX_WIDTH
        height = height / ratio
    elif height / width >= 1 and height > MAX_HEIGHT:
        ratio = height / MAX_HEIGHT
        height = MAX_HEIGHT
        width = width / ratio

    return int(width), int(height)
