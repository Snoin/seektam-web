# -*- coding: utf-8 -*-

import pytest

from seektam.web.app import app


@pytest.fixture
def fx_flask_client():
    app.config['TESTING'] = True
    return app.test_client()


@pytest.fixture
def fx_invalid_cfg_file(tmpdir):
    path = str(tmpdir) + '/invalid.php'
    with open(path, 'w') as f:
        f.write("<?php die('joke :)'); ?>")
    return path


@pytest.fixture
def fx_py_cfg_file(tmpdir):
    path = str(tmpdir) + '/test.cfg.py'
    with open(path, 'w') as f:
        f.write('PORT = 45009')
    return path
