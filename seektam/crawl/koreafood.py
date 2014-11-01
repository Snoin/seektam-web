# -*- coding: utf-8 -*-

'''
농식품종합정보시스템 식단관리(메뉴젠) 데이터 가져오기
http://koreanfood.rda.go.kr/
'''
from __future__ import absolute_import

import urllib

import lxml.html
from lxml.cssselect import CSSSelector
import requests
from sqlalchemy.orm.exc import NoResultFound

from ..model import koreafood


class Food(object):
    def __init__(self, name):
        self.name = name
        self.category_big = u''
        self.category_small = u''
        self.aliment = {}


def get_food_analysis(code):
    filter_entry = CSSSelector('#anal_Table > tr')
    filter_column = CSSSelector('.c_l_b')

    param = dict(mealcode=code, mealname='')
    post_param = dict(meal_CD=code, meal_NM='', h_NutriPage=0)
    url = 'http://koreanfood.rda.go.kr/mgn/mgn_User_meal_analysis.aspx'

    session = requests.Session()
    result = {}

    for n in range(1, 2+1):
        post_param['h_NutriPage'] = n
        r = session.post(
            '{}?{}'.format(url, urllib.urlencode(param)), post_param)
        h = lxml.html.fromstring(r.content)
        for elem in list(filter_entry(h)[:-1]):  # 합계 제외
            data = [x.text for x in filter_column(elem)]
            if data[0] not in result:
                result[data[0]] = [data[1]]  # 식품명 및 중량 기록

            result[data[0]] += data[2:]  # 나머지 데이터 기록

    return result


def get_food_list():
    filter_category = CSSSelector('.list_data_01 > .a_c')
    filter_foodname = CSSSelector('.eumsiknm')
    param = dict(
        qPage=0, s_firstSort='', s_secondSort='', t_mealName='',
        mealcd='', mealnm='', strflag='true')

    n = 1
    while True:
        param['qPage'] = n
        r = requests.get(
            'http://koreanfood.rda.go.kr/mgn/mgnmealinfo_mealquery.aspx?'
            + urllib.urlencode(param))
        h = lxml.html.fromstring(r.content)

        categories = map(lambda x: x.text, filter_category(h))
        entry = None
        for entry in filter_foodname(h):
            food = Food(entry.text.strip())
            food.category_big = categories[0]
            food.category_small = categories[1]

            arg = entry.attrib['href'].split('?')[1].split('&')
            code = filter(lambda x: x.startswith('meal_code'), arg)[0]
            code = code.split('=')[-1]
            food.aliment = get_food_analysis(code)

            yield food

            categories = categories[3:]

        if entry is None:
            break
        n = n+1


def food_to_model(sess, food):
    ret = []
    mfood = koreafood.Food()
    mfood.name = food.name
    mfood.category_big = food.category_big
    mfood.category_small = food.category_small

    for k in food.aliment:
        try:
            maliment = sess.query(koreafood.Aliment).filter(
                koreafood.Aliment.name == k).one()
        except NoResultFound:
            arr = food.aliment[k]
            maliment = koreafood.Aliment()

            # FIXME: take food.aliment as dict(dict()), not dict(list())
            columns = [
                'weight', 'energy', 'moisture', 'protein', 'fat',
                'nonfiborous', 'fiber', 'ash', 'calcium', 'potassium',
                'retinol_equivalent', 'retinol', 'betacarotene',
                'thiamin', 'riboflavin', 'niacin', 'ascobic_acid'
                ]

            maliment.name = k
            arr = map(lambda x: x.replace(',', ''), arr)
            weight = float(arr[0]) if arr[0] else 1.0
            for c in columns[1:]:
                setattr(maliment, c, float(arr[columns.index(c)]) / weight)

        ret.append(maliment)

    mfood.aliments = ret
    return mfood
