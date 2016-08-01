import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="sweetpay",
    version="0.1",
    author="David Buresund",
    author_email="david.buresund@paylevo.com",
    description="A library to talk with the Sweetpay API",
    license="Apache 2",
    keywords="sweetpay checkout payment",
    url="http://packages.python.org/sweetpay",
    packages=["sweetpay"],
    install_requires=["marshmallow==2.9.0", "requests==2.10.0"],
    long_description="Coming soon",# read('README'),
)
