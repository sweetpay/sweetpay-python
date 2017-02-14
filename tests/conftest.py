"""
Define the configuration of all testing.
"""
import pytest

from sweetpay import SweetpayClient


@pytest.fixture()
def client():
    # TODO: Create merchant and token for testing
    return SweetpayClient(
        "paylevo", True,
        {"subscription": 1, "creditcheck": 2, "checkout_session": 1}, 4)
