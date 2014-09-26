from __future__ import print_function

import os.path

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


def readme():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
            return f.read()
    except (IOError, OSError):
        return ''


install_requires = {
    # Module 'seektam.db'
    'cssselect >= 0.9.1',
    'lxml >= 3.4.0',
    'requests >= 2.4.1',
    # Entity classes
    'SQLAlchemy >= 0.9.0',
    'alembic >= 0.6.0',
    # Configuration
    'PyYAML >= 3.10',
    # Web
    'Flask >= 0.10',
    'Werkzeug >= 0.9',
    # CLI
    'click >= 3.3',
    }


tests_require = {
    'pytest >= 2.5.0',
    'lxml >= 3.4.0',
    'cssselect >= 0.9.1',
    }

docs_require = {
    'Sphinx >= 1.2',
    }


cmdclass = {}


setup(
    name='Seektam-web',
    description='스노인의 서비스 Seektam의 웹 프로그램',
    long_description=readme(),
    author='LeafDev',
    url='http://seektam.kr/',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'docs': docs_require,
        'tests': tests_require
    },
    entry_points='''
        [console_scripts]
        seektam = seektam.cli:main
    ''',
    cmdclass=cmdclass,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Documentation',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
    ]
)
