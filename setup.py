"""setup.py

Install rosmarus via setuptools.

Author:
    Figglewatts <me@figglewatts.co.uk>
"""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))


def get_repo_file_content(filename: str) -> str:
    with open(path.join(here, filename), encoding="utf-8") as f:
        return f.read()


setup(
    name="rosmarus",
    version="#{VERSION}#",
    description="Graphics?",
    long_description=get_repo_file_content("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/Figglewatts/rosmarus",
    author="Figglewatts",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.7",
    install_requires=[],  # TODO
)