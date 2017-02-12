import os
from setuptools import setup

__version__ = "0.2"


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="sweetpay",
    version=__version__,
    author="David Buresund",
    author_email="david.buresund@paylevo.com",
    description="A SDK to talk with the Sweetpay APIs (alpha version)",
    license="Apache 2",
    keywords="sweetpay checkout payment",
    url="https://github.com/sweetpay/sweetpay-python",
    download_url="https://github.com/sweetpay/sweetpay-"
                 "python/tarball/%s" % __version__,
    packages=["sweetpay"],
    install_requires=["requests==2.10.0", "python-dateutil-2.6.0"]
)
