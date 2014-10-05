# -*- coding: utf-8 -*-

"""Mocking test utility.

"""

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session


class MockDatabase(object):
    """ In-memory DB for safer, faster testing """

    def __init__(self, engine=None, Base=None):
        '''Create in-memory mocking DB instance.

        :class:`MockDatabase` mocks targeting database's all table and
        its structure, and maps to in-memory DB. For performance and
        `Fresh Fixture <http://xunitpatterns.com/Fresh%20Fixture.html>`
        strategy, :class:`MockDatabase` does not retrieve any data in
        mapped engine.

        Args:
            engine (sqlalchemy.engine.Engine):
                Reflects engine's declarative base.
            Base (sqlalchemy.ext.declarative.api.Base):
                Reflects this declarative base.
        '''

        if engine is None and Base is None:
            raise ValueError('No mocking target spcified.')

        if engine:
            self.target_engine = engine
            self.TBase = declarative_base()
            self.TBase.metadata.reflect(bind=self.target_engine)
        elif Base:
            self.TBase = Base

        self.init()

    def init(self):
        '''Initialize(reset) mocked in-memory copy.
        '''
        self.url = 'sqlite://'
        self.mock_engine = sqlalchemy.create_engine(self.url)

        self.MBase = declarative_base()
        self.MBase.metadata = self.TBase.metadata
        self.MBase.metadata.bind = self.mock_engine
        self.MBase.metadata.create_all()
        self._Session = scoped_session(sessionmaker(bind=self.mock_engine))

    def session(self):
        '''Get session object which can access to mocked DB.

        Returns:
            :class:`sqlalchemy.orm.session.Session` session instance.
        '''
        return self._Session()

    def tables(self):
        '''Get all list of tables.

        Returns:
            A dict mapping keys to the corresponding table name.
            Each value is represented as a :class:`sqlalchemy.sql.schema.Table`
            instances.
        '''
        return self.MBase.metadata.tables

    def insert(self, tablename, data):
        '''Insert given data in tablename.

        Args:
            tablename (str): Name of table. Note that given table name must
                be exists in MockDatabase's metadata.
            data (dict): Key-value pair which you want to write to table.
                All keys in data should be equal to table's column name,
                and each value should be equal to table's column type.
                Note that if you don't specify some optional column,
                it'll be automatically inserted as default column value
                (e.g. Current time when CURRENT_TIMESTAMP() has been set).

        Raises:
            sqlalchemy.exc.OperationalError: SQL operational error.
        '''
        table = self.MBase.metadata.tables[tablename]
        s = self._Session()
        s.execute(table.insert().values(**data))
        s.commit()

    def query(self, tablename):
        ''' Get all data from table.

        Returns:
            A tuple of every rows in table. Each row is presented as list.
            When table is empty, it returns empty tuple.
        '''

        table = self.MBase.metadata.tables[tablename]
        s = self._Session()
        return s.execute(table.select()).fetchall()
