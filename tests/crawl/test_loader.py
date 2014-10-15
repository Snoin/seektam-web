# -*- coding: utf-8 -*-

import random

import pytest
import sqlalchemy
from sqlalchemy.orm.exc import NoResultFound

from seektam.crawl import koreafood
from seektam.crawl import loader  # SUT
from seektam.model import koreafood as food
from tests.model import mock


class MockSession(object):
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
    a = food.Aliment()
    a.id = random.randint(1, 10000)
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


def test_mocksession_mocks_sqlalchemy_session():
    expect = 10000
    sess = MockSession()
    sess.one = lambda: expect

    assert sess.one() == expect
    assert sess.query(food.Aliment).one() == expect
    assert sess.query(food.Aliment).filter(
        food.Aliment.name == 'X').one() == expect


def test_mocksession_with_results_mocks_sqlalchemy_session():
    expect = 10000
    sess = MockSession(expect)

    assert sess.one() == expect
    assert sess.all() == expect
    assert sess.query().one() == expect
    assert sess.query().all() == expect
    assert sess.query().filter().one() == expect
    assert sess.query().filter().all() == expect


def test_mocksession_dummyfunc_raises_exception():
    sess = MockSession()
    sess.one = dummy_error_func

    with pytest.raises(AttributeError):
        sess.one()


def test_foodtomodel_no_query_if_no_aliments():
    sess = MockSession()
    sess.one = dummy_error_func
    food = koreafood.Food('FOOD')

    loader.food_to_model(sess, food)


def test_foodtomodel_query_if_aliments_exist():
    sess = MockSession()
    sess.one = dummy_error_func  # raise AttributeError if called
    food = koreafood.Food('FOOD')
    food.aliment = {'weight': 0}

    with pytest.raises(AttributeError):
        loader.food_to_model(sess, food)


def test_foodtomodel_returns_model_food():
    s = MockSession()
    f = koreafood.Food('FOOD')

    result = loader.food_to_model(s, f)

    assert isinstance(result, food.Food)


def test_foodtomodel_reflects_model_food_without_aliment():
    sess = MockSession()
    food = koreafood.Food('FOOD')
    food.category_big = 'CATEGORY_BIG'
    food.category_small = 'CATEGORY_SMALL'

    result = loader.food_to_model(sess, food)

    assert result.name == food.name
    assert result.category_big == food.category_big
    assert result.category_small == food.category_small
    assert not result.aliments


def test_foodtomodel_query_aliment():
    expect = food.Aliment(name='ALIMENT')
    s = MockSession(expect)
    f = koreafood.Food('FOOD')
    f.aliment = {'aliment': expect}

    result = loader.food_to_model(s, f)

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

    s = MockSession()
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
    result = loader.food_to_model(s, f)

    assert result.name == f.name
    assert result.category_big == f.category_big
    assert result.category_small == f.category_small
    assert len(result.aliments) == 1
    assert isinstance(result.aliments[0], food.Aliment)
    for column_name in columns[1:]:
        c = getattr(result.aliments[0], column_name)
        assert c == getattr(a, column_name) / weight


@pytest.fixture
def mockdb():
    engine = sqlalchemy.create_engine('sqlite://')
    food.Base.metadata.create_all(engine)

    return mock.MockDatabase(engine)


def test_addmodel_insert_no_filter(mockdb):
    a = food.Aliment(name='FOOD')
    filter_func = ''

    ret = loader.add_model(mockdb._Session(), food.Aliment, filter_func, a)
    assert ret is True

    session = mockdb._Session()
    result = session.query(food.Aliment).one()
    assert result == a


def test_addmodel_deny_insert_on_duplicate(mockdb):
    a = food.Aliment(name='ALIMENT_EXPECT')
    b = food.Aliment(name=a.name)
    filter_func = food.Aliment.name == a.name

    # should be added
    ret1 = loader.add_model(mockdb._Session(), food.Aliment, '', a)
    # should NOT be added; duplicated name
    ret2 = loader.add_model(mockdb._Session(), food.Aliment, filter_func, b)
    assert ret1 is True
    assert ret2 is False

    session = mockdb._Session()
    result = session.query(food.Aliment).one()
    assert result == a


def test_addfood_insert(mockdb):
    a = food.Food(name='FOOD')
    assert loader.add_food(mockdb._Session(), a) is True
    assert loader.add_food(mockdb._Session(), a) is False


def test_addaliment_insert(mockdb):
    a = food.Aliment(name='Aliment')
    assert loader.add_aliment(mockdb._Session(), a) is True
    assert loader.add_aliment(mockdb._Session(), a) is False
