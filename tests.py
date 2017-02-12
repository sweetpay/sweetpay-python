# -*- coding: utf-8 -*-
"""All tests for the sweetpay package.

These tests can be run with `make test`. But make sure that
you have installed everything in `requirements.txt.dev` first.
This can be accomplished by running `make setupdev`.  Note,
though, that this command assumes that you have `pip` installed
and can use it without root permissions.

Guidelines for writing tests:

Note that we do not make extensive (if any) use of mocks here.
This is because we want to verify that it really works against
the current version of the API. By making use of the real API
it also becomes easier to maintain. However, with that said,
mocks can of course be used in places where the communication
with the API isn't what is being tested.

pytest is king. It is forbidden to write tests with anything
else than pytest, but please feel free to use the patcher
or other helpers from the unittest library.

When writing new tests, always assume that the server is empty,
so that each test can run in whatever order and without prior
setup. This generally means that you need to create new resources
in every.

These tests were originally written while listening to the Weekend
Radio and, at times, Kyla La Grange - Cut Your Teeth on repeat.
"""

from datetime import date, datetime, timedelta

import pytest
from sweetpay import Subscription, CheckoutSession, Creditcheck, configure
from sweetpay.constants import OK_STATUS
from sweetpay.errors import FailureStatusError, BadDataError, NotFoundError, \
    InvalidParameterError
from uuid import uuid4

# TODO: Create specific merchant and token for testing
# Global configuration. NOTE: This is handy now, but will not work
# when we have support for several versions of the APIs. At least
# not when testing.
configure("paylevo", True, {"subscription": 1, "creditcheck": 2}, timeout=4)

# Just some test data
CREDIT_SSN = "19500101-0001"
NOCREDIT_SSN = "19500101-0007"

# The startsAt to use for subscription. It is important that 
# this isn't today's date, as that is what the subscription 
# API defaults to.
STARTS_AT = (datetime.utcnow() - timedelta(days=10)).date()


def assert_resp_ok(resp):
    assert resp.code == 200
    assert resp.status == OK_STATUS


def assert_isdatetime(val):
    assert isinstance(val, datetime)


def assert_isdate(val):
    assert isinstance(val, date)


def create_subscription(credit=True, **extra):
    return Subscription.create(
        amount=200, currency="SEK", country="SE",  merchantId="paylevo",
        interval="MONTHLY", ssn=CREDIT_SSN if credit else NOCREDIT_SSN,
        startsAt=STARTS_AT, maxExecutions=4, **extra)  # This row not mandatory


def assert_subscription(payload, credit=True):
    assert payload["customer"]["address"]["country"] == "SE"
    assert payload["startsAt"] == STARTS_AT
    assert payload["amount"] == 200
    assert payload["currency"] == "SEK"
    assert payload["interval"] == "MONTHLY"
    assert payload["merchantId"] == "paylevo"
    assert payload["customer"]["ssn"] == CREDIT_SSN if credit else NOCREDIT_SSN
    assert payload["maxExecutions"] == 4


class TestSubscriptionResource:
    def test_create(self):
        resp = create_subscription()
        assert_resp_ok(resp)
        data = resp.data
        payload = data["payload"]

        assert payload
        assert_isdatetime(data["createdAt"])
        assert_isdate(payload["startsAt"])
        assert_subscription(payload)

    def test_create_with_no_credit(self):
        with pytest.raises(FailureStatusError) as excinfo:
            create_subscription(credit=False)
        exc = excinfo.value
        assert exc.data
        assert "payload" not in exc.data  # Expecting empty payload
        assert exc.status == "CUSTOMER_NOT_CREDIBLE"

    # TODO: Test with mock instead.
    # TODO: Move the test from here, as we are testing a
    #       hack not related to the subscription API
    def test_create_with_missing_amount(self):
        with pytest.raises(BadDataError) as excinfo:
            Subscription.create(
                currency="SEK", interval="MONTHLY", ssn=CREDIT_SSN,
                merchantId="paylevo", country="SE")
        exc = excinfo.value
        assert exc.status == "Missing amount."
        assert exc.data is None

    def test_regret(self):
        resp = create_subscription()
        subscription_id = resp.data["payload"]["subscriptionId"]
        assert_subscription(resp.data["payload"])

        resp = Subscription.regret(subscription_id)
        assert resp.data["payload"]["state"] == "REGRETTED"
        assert resp.data["payload"]["subscriptionId"] == subscription_id

        # TODO: Should maybe be moved into its own test?
        # It is not regrettable when it has been regretted
        with pytest.raises(FailureStatusError) as excinfo:
            Subscription.regret(subscription_id)
        exc = excinfo.value
        assert exc.status == "NOT_MODIFIABLE"

    def test_search(self):
        # NOTE: merchantItemId should not be used as an identifier.
        # It is only used here like that here, because we can't search
        # on merchantOrderId/merchantSubscriptionId for the moment.

        # Use an identifier we can later find
        identifier = str(uuid4())
        resp = create_subscription(merchantItemId=identifier)
        assert_subscription(resp.data["payload"])
        assert resp.data["payload"]["merchantItemId"] == identifier

        resp = Subscription.search(merchantItemId=identifier)
        payload = resp.data["payload"]
        assert len(payload) == 1

        subscription = payload[0]
        assert_isdatetime(subscription["createdAt"])
        assert_subscription(subscription)
        assert subscription["merchantItemId"] == identifier

    def test_search_with_no_criteria(self):
        with pytest.raises(BadDataError) as excinfo:
            Subscription.search()
        exc = excinfo.value
        # Invalid JSON because the server can't parse an
        # empty JSON object for some reason. It is also
        # possible that requests isn't sending empty dicts.
        assert exc.status == "INVALID_JSON"

    def test_update(self):
        resp = create_subscription()
        assert_subscription(resp.data["payload"])
        subscription_id = resp.data["payload"]["subscriptionId"]

        resp = Subscription.update(subscription_id, maxExecutions=2)
        assert resp.data["payload"]["subscriptionId"] == subscription_id
        assert resp.data["payload"]["maxExecutions"] == 2

    def test_query(self):
        resp = create_subscription()
        assert_subscription(resp.data["payload"])
        subscription_id = resp.data["payload"]["subscriptionId"]

        resp = Subscription.query(subscription_id)
        assert resp.data["payload"]["subscriptionId"] == subscription_id

    def test_query_with_nonexistent_resource(self):
        with pytest.raises(NotFoundError):
            Subscription.query(10000)

    def test_list_log(self):
        subresp = create_subscription()
        subscription_id = subresp.data["payload"]["subscriptionId"]

        resp = Subscription.list_log(subscription_id)
        payload = resp.data["payload"]
        assert len(payload) > 0
        assert_isdatetime(payload[0]["createdAt"])
