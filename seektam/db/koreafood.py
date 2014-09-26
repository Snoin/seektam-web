# -*- coding: utf-8 -*-

'''
농식품종합정보시스템 식단관리(메뉴젠) 데이터 가져오기
http://koreanfood.rda.go.kr/
'''

import urllib

import lxml.html
from lxml.cssselect import CSSSelector
import requests


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
