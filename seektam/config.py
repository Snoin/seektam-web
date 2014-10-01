# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import os.path

from click import echo

from .web.app import app

__all__ = 'load_config',


def load_config(config_file=None):
    u"""설정파일을 읽습니다."""
    if config_file is None:
        try:
            config_file = os.environ['SEEKTAM_WEB_CONFIG']
        except KeyError:
            echo(u'설정 파일을 지정해주세요.')
            raise SystemExit(1)
    if not os.path.isfile(config_file):
        echo(u'지정한 파일이 올바른 설정 파일이 아닙니다.')
        raise SystemExit(1)
    elif not config_file.endswith('.py'):
        echo(u'설정 파일은 .py 파일이어야 합니다.')
        raise SystemExit(1)
    config = {}
    execfile(config_file, {}, config)
    app.config.update(config)
