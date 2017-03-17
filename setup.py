# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="macspell",
    version="2017",
    license="BSD",
    platforms=["Darwin"],
    description="MacSpell spell checker",
    long_description="MacSpell is a spell checker designed on Cocoa's spell-checking facilities",
    author="Rudá Moura",
    author_email="ruda.moura@gmail.com",
    url="http://ruda.github.io/macspell/",
    keywords="spell checker ispell",
    scripts=["macspell.py"],
    classifiers = [
        "Programming Language :: Python", 
        "License :: OSI Approved :: BSD License",
        "Environment :: MacOS X",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
    ]
)
