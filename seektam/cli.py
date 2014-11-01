# -*- coding: utf-8 -*-

""":mod:`seektam.cli` --- Command-line interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from __future__ import absolute_import

import code
import functools

from click import argument, group, option, Path
from flask import _request_ctx_stack
from sqlalchemy import create_engine
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker

from .config import load_config
from .crawl import koreafood
from .model.orm import Base
from .web.app import app

__all__ = 'cli', 'global_option', 'main', 'runserver'


def global_option(f):
    @functools.wraps(f)
    def internal(*args, **kwargs):
        load_config(kwargs.pop('config'))
        f(*args, **kwargs)

    config = option('--config', '-c', type=Path(exists=True),
                    help=u'설정 파일 (.py)')
    return config(internal)


@group()
def cli():
    u"""Seektam 서비스를 위한 명령어 모음집"""


@cli.command()
@argument('url')
def loader(url):
    u"""농식품종합정보시스템 식품 정보(식단명 및 재료)를 DB에 저장합니다.

    :param URL: 저장할 데이터베이스 URL (ex. mysql://scott@tiger:example.com/dbname)
    """
    engine = create_engine(url)
    Session = scoped_session(sessionmaker(engine))
    sess = Session()

    Base.metadata.bind = engine
    Base.metadata.create_all()

    for food in koreafood.get_food_list():
        mfood = koreafood.food_to_model(sess, food)
        sess.merge(mfood)
        sess.commit()


@cli.command()
@option('--debug/--no-debug', '-d/-D', default=False,
        help=u'Werkzeug 디버거 활성화 (실 서비스 사용 금지)')
@option('--reload/--no-reload', '-r/-R', default=False,
        help=u'리로더 활성화 (실 서비스 사용시 안전치 못할 수 있음)')
@global_option
def runserver(debug, reload):
    u"""Flask web application을 실행합니다."""
    app.run(
        port=app.config['PORT'],
        debug=debug,
        use_debugger=debug,
        use_reloader=reload
    )


@cli.command()
@global_option
def shell():
    """Flask application context 속을 Python shell로 봅니다."""
    with app.test_request_context():
        context = dict(app=_request_ctx_stack.top.app)
        code.interact(local=context)


main = cli
