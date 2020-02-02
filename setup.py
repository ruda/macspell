# -*- coding: utf-8 -*-

from io import open
from os import path
from setuptools import setup

import macspell

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="macspell",
    version=macspell.__version__,
    license="MIT",
    platforms=["Darwin"],
    description="MacSpell spell checker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rudá Moura",
    author_email="ruda.moura@gmail.com",
    url="http://ruda.github.io/macspell/",
    keywords="spell checker ispell",
    packages=["macspell"],
    install_requires=["pyobjc-framework-Cocoa"],
    entry_points={
        "console_scripts": ["macspell=macspell.cmd:main"],
    },
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Environment :: MacOS X",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
    ]
)
