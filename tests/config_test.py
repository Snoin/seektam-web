from seektam.config import load_config
from seektam.web.app import app


def test_invalid_cfg_file(fx_invalid_cfg_file):
    try:
        load_config(fx_invalid_cfg_file)
    except SystemExit:
        assert True
    else:
        assert False


def test_py_cfg_file(fx_py_cfg_file, fx_flask_client):
    try:
        load_config(fx_py_cfg_file)
    except SystemExit:
        assert False
    else:
        assert app.config['PORT'] == 45009
