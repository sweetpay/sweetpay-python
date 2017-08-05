"""Test the supported mock interface."""
from unittest.mock import Mock

import pytest

from sweetpay.resources import SubscriptionV1
from sweetpay.base import ResponseClass
from sweetpay.errors import NotFoundError


class TestMocking:
    """Test the mocking feature of the library.

    Note that you should only use `client.subscription` to test this,
    or you should rewrite the code. You decide.
    """

    def test_no_mock_when_not_mocking(self, client):
        assert not client.subscription.create._func._mock

    def test_mock_when_mocking(self, client):
        with client.subscription.create.mock() as mock:
            assert client.subscription.create._func._mock is mock

    def test_mock_removed_after_mocking(self, client):
        with client.subscription.create.mock():
            pass
        assert not client.subscription.create._func._mock

    def test_mock_is_isolated_to_one_method(self, client):
        with client.subscription.create.mock():
            assert not client.subscription.search._func._mock

    def test_mock_called(self, client):
        with client.subscription.create.mock() as mock:
            client.subscription.create(1, test=2)
        mock.assert_called_once_with(1, test=2)

    def test_return_value(self, client):
        # Setup
        with client.subscription.create.mock(return_value={"status": "OK"}):
            # Execute
            data = client.subscription.create()
        # Verify
        assert data == {"status": "OK"}

    def test_with_exception(self, client):
        # Setup
        exc = NotFoundError()
        with client.subscription.regret.mock(side_effect=exc):
            # Verify
            with pytest.raises(NotFoundError):
                # Execute
                client.subscription.regret(242)
