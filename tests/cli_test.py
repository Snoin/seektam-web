# -*- coding: utf-8 -*-

from seektam.cli import shell


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
