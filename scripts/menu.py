# -*- coding: utf-8 -*-

import requests
import json
import datetime
import time
import logging
import threading

logger = logging.getLogger(__name__)

handler = logging.FileHandler('menu.log')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

CONST_STATUS_OPEN = 1
CONST_STATUS_CLOSE = 4
CONST_STATUS_BOOKING = 5

def get_menu(rid):
    data = {
        'requests':[
            {
                'method': "GET",
                'url': "/v4/restaurants/{}/mutimenu".format(rid)
            }],
        'timeout':10000
    }

    headers = {
        'accept':'application/json, text/plain, */*',
        'accept-encoding':'gzip, deflate',
        'accept-language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        'content-length':'215',
        'content-type':'application/json;charset=UTF-8',
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    }
    response = requests.post(
        'https://www.ele.me/restapi/batch',
        data=json.dumps(data),
        headers=headers
    )

    resp_data = json.loads(json.loads(response.text)[0]['body'])
    return resp_data

def get_rst_info(rid, geohash):
    data = {
        'requests':[
            {
                'method': "GET",
                'url': "/v4/restaurants/{}?geohash={}".format(rid, geohash)

            }],
        'timeout':10000
    }

    headers = {
        'accept':'application/json, text/plain, */*',
        'accept-encoding':'gzip, deflate',
        'accept-language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
        'content-length':'215',
        'content-type':'application/json;charset=UTF-8',
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    }
    response = requests.post(
        'https://www.ele.me/restapi/batch',
        data=json.dumps(data),
        headers=headers
    )

    resp_data = json.loads(json.loads(response.text)[0]['body'])
    return resp_data

rid_map = {
    1: 422336,
    2: 497698,
    3: 520557,
    4: 621800
}

rid_geohash_map = {
    1: 'wtw37se14q1',
    2: 'wtw37we70zf',
    3: 'wtw3s57w6h4',
    4: 'wtw3s6tjr69',
}

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def check_sold_out():
    def _check_open_time():
        hour = datetime.datetime.now().hour
        return (10 <= hour < 20)

    if not _check_open_time():
        return

    sold_out_data = {}
    ts = int(time.time())
    time_str = datetime.datetime.now().strftime('%H:%M:%S')
    print time_str
    sold_out_data['ts'] = ts
    sold_out_data['time_str'] = time_str
    for pyid, eleme_rid in rid_map.iteritems():
        menu = get_menu(eleme_rid)
        rst_info = get_rst_info(eleme_rid, rid_geohash_map[pyid])
        shop_data = {}
        shop_data['status'] = rst_info['status']
        shop_data['deliver_amount'] = rst_info['minimum_order_amount']
        print 'rid: {} status:{} deliver_amount:{}'.format(
            pyid, shop_data['status'], shop_data['deliver_amount'])
        for category in menu:
            if category['name'] in [u'好评榜', u'热销榜']:
                continue
            #print category['name']
            for food in category['foods']:
                if food['specfoods'][0]['price'] < 10:
                    continue
                #print '\t' + food['name']
                food_data = {
                    'all_empty': False,
                    'empty_list': []
                }
                all_empty = True
                has_empty = False

                for spec in food['specfoods']:
                    if spec['stock'] == 0:
                        print '\t\t' + spec['name'].encode('utf8') + str(spec['stock'])
                        food_data['empty_list'].append(spec['name'])
                        has_empty = True
                    else:
                        all_empty = False
                if all_empty:
                    print '\t' + food['name'].encode('utf8')
                food_data['all_empty'] = all_empty

                if has_empty:
                    shop_data[food['name']] = food_data
        sold_out_data['shop{}'.format(pyid)] = shop_data
    logger.info(json.dumps(sold_out_data))

check_sold_out()
