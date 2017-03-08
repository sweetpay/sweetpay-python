from setuptools import setup

__version__ = "0.2.2"

setup(
    name="sweetpay",
    version=__version__,
    author="David Buresund",
    author_email="david.buresund@gmail.com",
    description="A SDK to talk with the Sweetpay APIs",
    license="Apache 2",
    keywords=["sweetpay", "checkout", "payment"],
    url="https://github.com/sweetpay/sweetpay-python",
    download_url="https://github.com/sweetpay/sweetpay-"
                 "python/tarball/%s" % __version__,
    packages=["sweetpay"],
    install_requires=["requests==2.10.0", "python-dateutil==2.6.0"]
)
