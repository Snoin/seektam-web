# -*- coding: utf-8 -*-

import click
import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

from seektam.cli import loader, shell
from seektam.crawl import koreafood
from seektam.model import orm
from seektam.model import koreafood as koreafood_model
from tests.crawl.test_koreafood import listfile  # noqa
from tests.crawl.test_koreafood import MockHTTPResponse
from tests.crawl.test_koreafood import MockHTTPSession
from tests.crawl.test_koreafood import _mock_foodlist_analysis_page


@pytest.fixture
def clirunner():
    return click.testing.CliRunner()


def test_loader_argument_requires_url(clirunner):
    res = clirunner.invoke(loader)
    assert res.exit_code == 2


def test_loader_argument_takes_db_url(clirunner, monkeypatch):
    monkeypatch.setattr(koreafood, 'get_food_list', lambda: [])

    res = clirunner.invoke(loader, ['sqlite://'])  # SQLite memory
    assert res.exit_code == 0


def test_loader_builds_db_model_if_new(clirunner, monkeypatch, tmpdir):
    # We have no interest in list parsing, so let's ignore it
    monkeypatch.setattr(koreafood, 'get_food_list', lambda: [])

    # Create clean SQLite DB (just new file ;)
    url = 'sqlite:///'+tmpdir.join('new.db').strpath

    # Trigger DB creation
    res = clirunner.invoke(loader, [url])

    # Test result
    assert res.exit_code == 0
    Base = declarative_base()
    Base.metadata.reflect(create_engine(url))
    assert Base.metadata.tables.keys() == orm.Base.metadata.tables.keys()


def test_loader_inserts_food_element(  # noqa
    clirunner, monkeypatch, tmpdir, listfile):
    # Mocking for Nurungji-only food list
    monkeypatch.setattr(
        koreafood.requests, 'get',
        lambda _: MockHTTPResponse(listfile.read()))
    monkeypatch.setattr(
        koreafood.requests, 'Session',
        lambda: MockHTTPSession(post=_mock_foodlist_analysis_page))

    food = koreafood.get_food_list().next()
    monkeypatch.setattr(
        koreafood, 'get_food_list', lambda: [food])

    # Trigger SUT command
    url = 'sqlite:///'+tmpdir.join('new.db').strpath
    res = clirunner.invoke(loader, [url])

    # Test result
    assert res.exit_code == 0
    session = sessionmaker(create_engine(url))()

    mfood = session.query(koreafood_model.Food).one()
    assert mfood.name == food.name
    assert mfood.category_big == food.category_big
    assert mfood.category_small == food.category_small
    assert len(mfood.aliments) == 1


def test_shell_not_config(fx_cli_runner):
    res = fx_cli_runner.invoke(shell, [])
    assert res.exit_code == 1
    assert u'설정 파일을 지정해주세요' in res.output


def test_shell_invalid_config(fx_cli_runner, fx_invalid_cfg_file):
    res = fx_cli_runner.invoke(shell, ['-c', fx_invalid_cfg_file])
    assert res.exit_code == 1
    assert u'설정 파일은 .py 파일이어야 합니다.' in res.output


def test_shell_run(fx_cli_runner, fx_py_cfg_file):
    res = fx_cli_runner.invoke(shell, ['-c', fx_py_cfg_file])
    assert res.exit_code == 0
    assert '(InteractiveConsole)' in res.output
