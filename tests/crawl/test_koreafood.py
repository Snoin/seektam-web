# -*- coding: utf-8 -*-

import codecs
import os
import random

import pytest
from sqlalchemy.orm.exc import NoResultFound

from seektam.crawl import koreafood  # SUT
from seektam import model


cwd = os.path.dirname(os.path.realpath(__file__))
listfile_path = os.path.join(cwd, 'koreafood_list_sample.htm')


@pytest.fixture
def listfile():
    return codecs.open(listfile_path, encoding='euckr')


# This function can't be wrapped via pytest.fixture
# because it requires food code and order paramter.
def analysisfile(code, order):
    path = os.path.join(
        cwd, 'koreafood_detail_%s_%s.htm' % (code, order))
    return codecs.open(path, encoding='euckr', errors='ignore')


def trigger_error_func(*args, **kwarg):
    raise AttributeError('args=%s, kwarg=%s' % (args, kwarg))


class MockHTTPResponse(object):
    def __init__(self, content):
        self.content = content


class MockHTTPSession(object):
    def __init__(self, post):
        self.post = post


def test_foodlist_monkeypatch_work(monkeypatch):
    '''
    Test if koreafood.get_food_list() calls monkeypatched
    requests.get() method.
    '''

    monkeypatch.setattr(koreafood.requests, 'get', trigger_error_func)

    l = koreafood.get_food_list()
    with pytest.raises(AttributeError):
        l.next()


def test_foodlist_listfile_exists():
    assert os.path.isfile(listfile_path)


def test_foodlist_listfile_valid(listfile):
    data = listfile.read()
    expect_data = [
        (u'밥류', u'쌀밥', u'누룽지'),
        (u'밥류', u'쌀밥', u'누른밥'),
        (u'밥류', u'쌀밥', u'쌀밥'),
        (u'밥류', u'쌀밥', u'찰밥'),
        (u'밥류', u'쌀밥', u'현미밥'),
        (u'밥류', u'잡곡밥류', u'기장밥'),
        (u'밥류', u'잡곡밥류', u'땅콩밥'),
        (u'밥류', u'잡곡밥류', u'밤밥'),
        (u'밥류', u'잡곡밥류', u'보리밥'),
        (u'밥류', u'잡곡밥류', u'보리콩밥')]

    for cate_big, cate_mid, cate_small in expect_data:
        assert cate_big in data
        assert cate_mid in data
        assert cate_small in data


def test_foodlist_listfile_food_parsed(monkeypatch, listfile):
    monkeypatch.setattr(
        koreafood.requests, 'get',
        lambda _: MockHTTPResponse(listfile.read()))
    monkeypatch.setattr(
        koreafood, 'get_food_analysis',
        lambda _: {})  # alignment parse ignored

    food = koreafood.get_food_list().next()
    assert food.category_big == u'밥류'
    assert food.category_small == u'쌀밥'
    assert food.name == u'누룽지'


def _mock_foodlist_analysis_page(url, param):
    parsed_url = url.split('?')[-1]
    getargs = dict(
        map(lambda x: x.split('='), parsed_url.split('&')))

    code = getargs.get('mealcode', '')
    assert code != ''
    order = int(param.get('h_NutriPage', -9999))
    assert order == 1 or order == 2

    f = analysisfile(code, order)
    return MockHTTPResponse(content=f.read())


def test_foodlist_analysis_session_mocked(monkeypatch):
    monkeypatch.setattr(
        koreafood.requests, 'Session',
        lambda: MockHTTPSession(post=trigger_error_func))

    with pytest.raises(AttributeError):
        koreafood.get_food_analysis('NO_MEARNING')


def test_foodlist_analysis_exists(monkeypatch):
    monkeypatch.setattr(
        koreafood.requests, 'Session',
        lambda: MockHTTPSession(post=_mock_foodlist_analysis_page))

    koreafood.get_food_list().next()


def test_foodlist_analysis_parsed(monkeypatch):
    monkeypatch.setattr(
        koreafood.requests, 'Session',
        lambda: MockHTTPSession(post=_mock_foodlist_analysis_page))

    nurungji = koreafood.get_food_list().next()
    expect_aliment = {
        u'쌀,멥쌀,논벼,백미,(국내산),일반형,일품': [
            50, 185, 5.6, 2.6, 0.2, 41.3, 0.2, 0.2, 3, 45.5, 0.6,
            7.5, 52.5, 0, 0, 0, 0.1, 0.015, 0.5, 0
            ]
        }

    for k in nurungji.aliment:
        assert k in nurungji.aliment
        assert len(nurungji.aliment[k]) == len(expect_aliment[k])
        for a, b in zip(nurungji.aliment[k], expect_aliment[k]):
            assert float(a) == float(b)


def test_foodlist_listfile_next_called(monkeypatch, listfile):
    monkeypatch.setattr(
        koreafood.requests, 'get',
        lambda _: MockHTTPResponse(listfile.read()))

    l = koreafood.get_food_list()
    l.next()  # 1 called (9 items remained)

    monkeypatch.setattr(
        koreafood.requests, 'get',
        lambda _: trigger_error_func)

    for n in range(9):
        l.next()  # consume all lists

    with pytest.raises(AttributeError):
        l.next()  # requets next page


def test_foodlist_break_if_no_more_list(monkeypatch, listfile):
    monkeypatch.setattr(
        koreafood.requests, 'get',
        lambda _: MockHTTPResponse(listfile.read()))

    l = koreafood.get_food_list()
    for n in range(10):
        l.next()  # traverse all(10) list elements

    monkeypatch.setattr(
        koreafood.requests, 'get',
        lambda _: MockHTTPResponse(u'<html></html>'))

    # returns nothing, iterator should be stopped
    with pytest.raises(StopIteration):
        l.next()


class MockDBSession(object):
    def __init__(self, result=[]):
        self._call_count = 0
        self.result = result

    def filter(self, *args, **kwarg):
        return self

    def query(self, *args, **kwarg):
        return self

    def one(self):
        return self.result

    def all(self):
        return self.result


def dummy_error_func(*args, **kwarg):
    raise AttributeError('args=%s, kwarg=%s' % (args, kwarg))


def dummy_fuzzy_aliment(name='ALIMENT'):
    a = model.koreafood.Aliment()
    a.name = name
    a._aliment_dic = {}

    for column_name in dir(a):
        column = getattr(a, column_name)
        if column is not None:
            continue

        value = round(random.random() * 10000, 3)
        setattr(a, column_name, value)
        a._aliment_dic[column_name] = "{:,}".format(value)

    return a


def test_mockdbsession_mocks_sqlalchemy_session():
    expect = 10000
    sess = MockDBSession()
    sess.one = lambda: expect

    assert sess.one() == expect
    assert sess.query(model.koreafood.Aliment).one() == expect
    assert sess.query(model.koreafood.Aliment).filter(
        model.koreafood.Aliment.name == 'X').one() == expect


def test_mockdbsession_with_results_mocks_sqlalchemy_session():
    expect = 10000
    sess = MockDBSession(expect)

    assert sess.one() == expect
    assert sess.all() == expect
    assert sess.query().one() == expect
    assert sess.query().all() == expect
    assert sess.query().filter().one() == expect
    assert sess.query().filter().all() == expect


def test_mockdbsession_dummyfunc_raises_exception():
    sess = MockDBSession()
    sess.one = dummy_error_func

    with pytest.raises(AttributeError):
        sess.one()


def test_foodtomodel_no_query_if_no_aliments():
    sess = MockDBSession()
    sess.one = dummy_error_func
    food = koreafood.Food('FOOD')

    koreafood.food_to_model(sess, food)


def test_foodtomodel_query_if_aliments_exist():
    sess = MockDBSession()
    sess.one = dummy_error_func  # raise AttributeError if called
    food = koreafood.Food('FOOD')
    food.aliment = {'weight': 0}

    with pytest.raises(AttributeError):
        koreafood.food_to_model(sess, food)


def test_foodtomodel_returns_model_food():
    s = MockDBSession()
    f = koreafood.Food('FOOD')

    result = koreafood.food_to_model(s, f)

    assert isinstance(result, model.koreafood.Food)


def test_foodtomodel_reflects_model_food_without_aliment():
    sess = MockDBSession()
    food = koreafood.Food('FOOD')
    food.category_big = 'CATEGORY_BIG'
    food.category_small = 'CATEGORY_SMALL'

    result = koreafood.food_to_model(sess, food)

    assert result.name == food.name
    assert result.category_big == food.category_big
    assert result.category_small == food.category_small
    assert not result.aliments


def test_foodtomodel_query_aliment():
    expect = model.koreafood.Aliment(name='ALIMENT')
    s = MockDBSession(expect)
    f = koreafood.Food('FOOD')
    f.aliment = {'aliment': expect}

    result = koreafood.food_to_model(s, f)

    assert len(result.aliments) == 1
    assert result.aliments[0] == expect


def test_format_comma_appended():
    assert '{:,}'.format(12) == '12'
    assert '{:,}'.format(12345) == '12,345'
    assert '{:,}'.format(111.22) == '111.22'
    assert '{:,}'.format(1234.56789) == '1,234.56789'


def test_foodtomodel_parse_aliment():
    def raises_noresult(*args, **kwarg):
        raise NoResultFound

    s = MockDBSession()
    s.one = raises_noresult
    f = koreafood.Food('FOOD')
    a = dummy_fuzzy_aliment()

    # Function `food_to_model` takes argument food.aliment as dictionary of
    # lists(fixed order), so for testing we should reorder lists as
    # SUT-expected order.
    columns = [
        'weight', 'energy', 'moisture', 'protein', 'fat',
        'nonfiborous', 'fiber', 'ash', 'calcium', 'potassium',
        'retinol_equivalent', 'retinol', 'betacarotene',
        'thiamin', 'riboflavin', 'niacin', 'ascobic_acid'
        ]
    aliment_list = ['2.0']  # weight=1.0
    weight = float(aliment_list[0])
    for n in range(1, 1+len(columns[1:])):
        aliment_list.append('{:,}'.format(getattr(a, columns[n])))

    f.aliment = {a.name: aliment_list}
    result = koreafood.food_to_model(s, f)

    assert result.name == f.name
    assert result.category_big == f.category_big
    assert result.category_small == f.category_small
    assert len(result.aliments) == 1
    assert isinstance(result.aliments[0], model.koreafood.Aliment)
    for column_name in columns[1:]:
        c = getattr(result.aliments[0], column_name)
        assert c == getattr(a, column_name) / weight
