"""
Test the validator functionality.
"""
import pytest

from sweetpay import BaseResource
from sweetpay import validates


# TODO: May this interfere with other tests when removing the validators?

# We don't want any validators when starting to test.
def setup_module(module):
    BaseResource.clear_validators()


# We remove all validators when we are done with the test.
def teardown_function():
    BaseResource.clear_validators()


def test_validates(client):
    @validates("subscription", 1, ["test", "path"])
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
    @validates("subscription", 1, ["tough"])
    def somefunc(value):
        return "changed value"

    with client.subscription.mock_resource(
            data={"other_path": "the value"}, status="OK", code=200):
        resp = client.subscription.regret(242)
    assert resp.data == {"other_path": "the value"}


@pytest.mark.parametrize("retdata", [None, []])
def test_validates_with_invalid_type(client, retdata):
    @validates("subscription", 1, ["tough"])
    def somefunc(value):
        return "changed value"

    with client.subscription.mock_resource(
            data=retdata, status="OK", code=200):
        resp = client.subscription.regret(242)
    assert resp.data is retdata


def test_validates_with_empty_path(client):
    @validates("subscription", 1, [])
    def somefunc(value):
        assert value == {"hej": "du"}

    with client.subscription.mock_resource(
            data={"hej": "du"}, status="OK", code=200):
        client.subscription.regret(242)


@pytest.mark.parametrize(
    "namespace,version", [("invalid", 1), ("subscription", 10)])
def test_validates_with_invalid_namespace_and_version(namespace, version):
    with pytest.raises(ValueError):
        @validates(namespace, version, ["payload"])
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
