""":mod:`seektam.cli` --- Command-line interfaces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from click import command, echo

__all__ = 'main',


@command()
def main():
    echo('hello seektam!')
