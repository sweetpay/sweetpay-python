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

    def test_mock_is_added(self, client):
        with client.subscription.create.mock() as mock:
            assert mock() == client.subscription.create()

    def test_mock_called(self, client):
        with client.subscription.create.mock() as mock:
            client.subscription.create(1, test=2)
            assert mock.assert_called_once_with(1, test=2)

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

    def test_mock_is_removed(self, client):
        # Setup and execute
        with client.subscription.create.mock() as mock:
            client.subscription.create()
        # Verify
        assert client.subscription.create() != mock

    def test_mock_only_affects_one_operation(self, client):
        with client.subscription.create.mock() as mock:
            client.subscription.regret(242)
        mock.assert_not_called()
