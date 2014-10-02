# -*- coding: utf-8 -*-

from seektam.model import food
from seektam.model import orm


def test_food_model_based_on_orm():
    assert food.Base == orm.Base
