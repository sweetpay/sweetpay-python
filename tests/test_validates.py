"""
Test the validator functionality.
"""
import pytest

from sweetpay import BaseResource
from sweetpay import validates


def setup_module(module):
    BaseResource.clear_validators()


def teardown_function():
    BaseResource.clear_validators()


# TODO: Clear validators on startup and teardown

def test_validates(client):
    @validates("subscription", ["test", "path"])
    def somefunc(value):
        return "changed value"
    with client.subscription.mock_resource(
            data={"test": {"path": "the value"}}, status="OK", code=200):
        resp = client.subscription.regret(242)
    assert resp.data["test"]["path"] == "changed value"

    # Make sure that it isn't set on other stuff
    with client.creditcheck.mock_resource(
            data={"test": {"path": "the value"}}, status="OK", code=200):
        other_resp = client.creditcheck.create(hej="du")
    assert other_resp.data["test"]["path"] != "changed value"


def test_validates_with_path_not_found(client):
    @validates("subscription", ["tough"])
    def somefunc(value):
        return "changed value"

    with client.subscription.mock_resource(
            data={"other_path": "the value"}, status="OK", code=200):
        resp = client.subscription.regret(242)
    assert resp.data == {"other_path": "the value"}


@pytest.mark.parametrize("retdata", [None, []])
def test_validates_with_invalid_type(client, retdata):
    @validates("subscription", ["tough"])
    def somefunc(value):
        return "changed value"

    with client.subscription.mock_resource(
            data=retdata, status="OK", code=200):
        resp = client.subscription.regret(242)
    assert resp.data is retdata


def test_validates_with_empty_path(client):
    @validates("subscription", [])
    def somefunc(value):
        assert value == {"hej": "du"}

    with client.subscription.mock_resource(
            data={"hej": "du"}, status="OK", code=200):
        client.subscription.regret(242)


def test_validates_with_invalid_namespace():
    with pytest.raises(ValueError):
        @validates("invalid", ["payload"])
        def somefunc(value):
            pass


def test_validates_on_all(client):
    @validates(["root", "yo"])
    def somefunc(value):
        return "changed value"

    with client.subscription.mock_resource(
            data={"root": {"yo": "the value"}}, status="OK", code=200):
        resp = client.subscription.regret(242)
    assert resp.data["root"]["yo"] == "changed value"

    # Make sure that it isn't set on other stuff
    with client.creditcheck.mock_resource(
            data={"root": {"yo": "the value"}}, status="OK", code=200):
        other_resp = client.creditcheck.create(hej="du")
    assert other_resp.data["root"]["yo"] == "changed value"
