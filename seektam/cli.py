# -*- coding: utf-8 -*-

""":mod:`seektam.cli` --- Command-line interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from __future__ import absolute_import

import functools

from click import group, option, Path

from .config import load_config
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


main = cli
