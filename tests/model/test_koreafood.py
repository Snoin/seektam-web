# -*- coding: utf-8 -*-

import pytest
from sqlalchemy import create_engine

from seektam.model import koreafood
from seektam.model import orm
from tests.model.mock import MockDatabase


engine = create_engine('sqlite://')
orm.Base.metadata.create_all(engine)


@pytest.fixture
def mockdb():
    return MockDatabase(engine)


def _mockdb_add_model(mockdb, model, **kwarg):
    sess = mockdb._Session()
    a = model(**kwarg)
    sess.add(a)
    sess.commit()
    return a


def test_koreafood_model_based_on_orm():
    assert koreafood.Base == orm.Base


def test_koreafood_aliment_relationship_1_1(mockdb):
    # insert test data
    a = _mockdb_add_model(
        mockdb, koreafood.Aliment,
        id=1001, name='aliment_1')

    f = _mockdb_add_model(
        mockdb, koreafood.Food,
        id=2001, name='food_1', aliments=[a])

    # query
    newsess = mockdb._Session()
    newf = newsess.query(koreafood.Food).filter(
        koreafood.Food.id == f.id).one()

    # validate
    assert len(newf.aliments) == 1
    assert newf.aliments[0].id == a.id


def test_koreafood_aliment_relationship_1_n(mockdb):
    N = 3
    aliments = []
    for n in range(1000, 1000+N):
        a = _mockdb_add_model(
            mockdb, koreafood.Aliment,
            id=n, name='aliment_%s' % n)
        aliments.append(a)

    f = _mockdb_add_model(
        mockdb, koreafood.Food,
        id=2001, name='food_1', aliments=aliments)

    newsess = mockdb._Session()
    newf = newsess.query(koreafood.Food).filter(
        koreafood.Food.id == f.id).one()

    assert len(newf.aliments) == N
    for n in range(N):
        assert newf.aliments[n].id == 1000+n
