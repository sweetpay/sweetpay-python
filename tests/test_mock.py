"""
Test the supported mock interface.
"""
from unittest.mock import Mock

import pytest


from sweetpay.base import ResponseClass
from sweetpay.errors import NotFoundError
from sweetpay.subscription import SubscriptionClient


class TestMocking:
    """Test the mocking feature of the library.

    Note that you should only use `client.subscription` to test this,
    or you should rewrite the code. You decide.
    """

    def assert_resp(self, resp):
        assert resp.data == {"status": "OK"}
        assert resp.code == 200
        assert resp.status == "OK"
        assert resp.response == 123

    def assert_removed_mock(self, client, monkeypatch):
        """Ensure sure that the mock was actually removed."""
        mock_create = Mock(
            return_value=ResponseClass(
                code=200, status="OK", data=None, response=None))
        monkeypatch.setattr(
            SubscriptionClient, "create_subscription", mock_create)
        client.subscription.create(amount=203)
        mock_create.called_once_with(amount=203)

    def test_all_operations_with_return_value(self, client, monkeypatch):
        assert client.subscription.is_mocked is False
        with client.subscription.mock_all_operations(
                data={"status": "OK"}, code=200, status="OK", response=123):
            assert client.subscription.is_mocked is True
            resp = client.subscription.regret(242)
            self.assert_resp(resp)
            resp = client.subscription.create(amount=303)
            self.assert_resp(resp)

        assert client.subscription.is_mocked is False
        self.assert_removed_mock(client, monkeypatch)

    def test_all_operations_with_exception(self, client, monkeypatch):
        exc = NotFoundError()
        assert client.subscription.is_mocked is False

        with client.subscription.mock_all_operations(raises=exc), \
                pytest.raises(NotFoundError) as excinfo:
            assert client.subscription.is_mocked is True
            client.subscription.regret(242)
            client.subscription.create(amount=242)

        assert client.subscription.is_mocked is False
        assert excinfo.value is exc
        self.assert_removed_mock(client, monkeypatch)
