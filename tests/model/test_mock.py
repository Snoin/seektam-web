# -*- coding: utf-8 -*-

from __future__ import absolute_import

import pytest
import sqlalchemy
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base

from tests.model import mock  # SUT


Base = declarative_base()
engine = None
mockdb = None


class SampleTable(Base):
    __tablename__ = 'sample_table'

    id = Column(Integer, primary_key=True)
    value = Column(Integer)


def setup_function(function):
    global engine
    global mockdb

    engine = sqlalchemy.create_engine('sqlite://')
    Base.metadata.bind = engine
    Base.metadata.create_all()

    mockdb = mock.MockDatabase(engine)


def test_init_reflect_tables():
    assert list(mockdb.tables()) == [SampleTable.__tablename__]


def test_init_reflect_table_using_base():
    mockdb = mock.MockDatabase(Base=Base)
    assert list(mockdb.tables()) == [SampleTable.__tablename__]


def test_init_raises_error_when_no_argument_given():
    with pytest.raises(ValueError):
        mock.MockDatabase()


def test_query_empty_table():
    res = mockdb.query('sample_table')

    assert len(res) == 0


def test_query_using_session():
    a = SampleTable(id=1, value=100)

    sess = mockdb.session()
    sess.add(a)
    sess.commit()

    sess = mockdb.session()
    newa = sess.query(SampleTable).one()
    assert newa == a


def test_insert_single():
    data = dict(id=1, value=100)

    mockdb.insert('sample_table', data)
    res = mockdb.query('sample_table')

    assert len(res) == 1
    assert res[0] == (data['id'], data['value'])


def test_insert_multi():
    datas = []
    datas.append(dict(id=1, value=100))
    datas.append(dict(id=2, value=200))

    for data in datas:
        mockdb.insert('sample_table', data)
    res = mockdb.query('sample_table')

    assert len(res) == len(datas)
    for idx, data in enumerate(datas):
        data_tuple = (data['id'], data['value'])
        assert res[idx] == data_tuple


def test_init_reset():
    mockdb.insert('sample_table', dict(id=1, value=100))
    mockdb.init()  # reset data; table should be truncaetd

    res = mockdb.query('sample_table')
    assert len(res) == 0
