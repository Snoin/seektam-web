# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FoodAlimentRelation(Base):
    __tablename__ = 'koreafood_food_aliment_rels'

    food_id = Column(
        Integer, ForeignKey('koreafood_foods.id'), primary_key=True)
    aliment_id = Column(
        Integer, ForeignKey('koreafood_aliments.id'), primary_key=True)


class Food(Base):
    __tablename__ = 'koreafood_foods'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(200), unique=True)
    category_big = Column(Unicode(20))
    category_small = Column(Unicode(20))


class Aliment(Base):
    __tablename__ = 'koreafood_aliments'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(200), unique=True)
    energy = Column(Float)
    moisture = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    nonfiborous = Column(Float)
    fiber = Column(Float)
    ash = Column(Float)
    calcium = Column(Float)
    phosphorus = Column(Float)
    iron = Column(Float)
    sodium = Column(Float)
    potassium = Column(Float)
    retinol_equivalent = Column(Float)
    retinol = Column(Float)
    betacarotene = Column(Float)
    thiamin = Column(Float)
    riboflavin = Column(Float)
    niacin = Column(Float)
    ascobic_acid = Column(Float)
