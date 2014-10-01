# -*- coding: utf-8 -*-

import codecs
import os

import pytest

from seektam.db import koreafood  # SUT


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


class MockResponse(object):
    def __init__(self, content):
        self.content = content


class MockSession(object):
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
        lambda _: MockResponse(listfile.read()))
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
    return MockResponse(content=f.read())


def test_foodlist_analysis_session_mocked(monkeypatch):
    monkeypatch.setattr(
        koreafood.requests, 'Session',
        lambda: MockSession(post=trigger_error_func))

    with pytest.raises(AttributeError):
        koreafood.get_food_analysis('NO_MEARNING')


def test_foodlist_analysis_exists(monkeypatch):
    monkeypatch.setattr(
        koreafood.requests, 'Session',
        lambda: MockSession(post=_mock_foodlist_analysis_page))

    koreafood.get_food_list().next()


def test_foodlist_analysis_parsed(monkeypatch):
    monkeypatch.setattr(
        koreafood.requests, 'Session',
        lambda: MockSession(post=_mock_foodlist_analysis_page))

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
        lambda _: MockResponse(listfile.read()))

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
        lambda _: MockResponse(listfile.read()))

    l = koreafood.get_food_list()
    for n in range(10):
        l.next()  # traverse all(10) list elements

    monkeypatch.setattr(
        koreafood.requests, 'get',
        lambda _: MockResponse(u'<html></html>'))

    # returns nothing, iterator should be stopped
    with pytest.raises(StopIteration):
        l.next()
