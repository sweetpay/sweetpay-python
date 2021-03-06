"""
Define the configuration of all testing.
"""
import pytest

from sweetpay import Client


@pytest.fixture()
def creditcheck_version():
    return 2


@pytest.fixture()
def subscription_version():
    return 1


@pytest.fixture()
def checkout_session_version():
    return 1


@pytest.fixture()
def client(subscription_version, creditcheck_version, checkout_session_version):
    # TODO: Create merchant and token for testing
    return Client(
        "NNq7Rcnb8y8jGTsU", test=True, version={
            "subscription": subscription_version,
            "creditcheck": creditcheck_version,
            "checkout_session": checkout_session_version
        }, timeout=4)
