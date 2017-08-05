"""Tests for all operations."""
import uuid
from datetime import date, datetime, timedelta

import pytest
from sweetpay.constants import TEST_CREDIT_SSN, TEST_NOCREDIT_SSN
from sweetpay.errors import FailureStatusError, BadDataError, NotFoundError
from uuid import uuid4

# The startsAt to use for subscription. It is important that 
# this isn't today's date, as that is what the subscription 
# API defaults to.
STARTS_AT = (datetime.utcnow() - timedelta(days=10)).date()


def assert_isdatetime(val):
    assert isinstance(val, datetime)


def assert_isdate(val):
    assert isinstance(val, date)


def assert_exc_status(excinfo, status):
    assert excinfo.value.status == status


def create_subscription(client, credit=True, **extra):
    ssn = TEST_CREDIT_SSN if credit else TEST_NOCREDIT_SSN
    return client.subscription.create(
        amount=10, currency="SEK", country="SE",  merchantId="sweetpay-demo",
        interval="MONTHLY", ssn=ssn, startsAt=STARTS_AT, maxExecutions=4,
        **extra)


def create_reservation(client, credit=True, **extra):
    ssn = TEST_CREDIT_SSN if credit else TEST_NOCREDIT_SSN
    return client.reservation.create(
        country="SE", billing={"email": "test@example.com"},
        merchantId="sweetpay-demo", customer={"ssn": ssn},
        executeAt=STARTS_AT, reservations={
            "transactions": [
                {"amount": {"amount": 101.0, "currency": "SEK"}}
            ]
        }, **extra)


def assert_subscription(payload, credit=True):
    assert payload["customer"]["address"]["country"] == "SE"
    assert payload["startsAt"] == STARTS_AT
    assert payload["amount"] == 10
    assert payload["currency"] == "SEK"
    assert payload["interval"] == "MONTHLY"
    assert payload["merchantId"] == "sweetpay-demo"
    assert payload["customer"]["ssn"] == TEST_CREDIT_SSN if credit else \
        TEST_NOCREDIT_SSN
    assert payload["maxExecutions"] == 4


def assert_reservation(payload, credit=True):
    assert len(payload) == 1
    reservation = payload[0]
    assert reservation["billing"]["email"] == "test@example.com"
    assert reservation["customer"]["ssn"] == TEST_CREDIT_SSN if credit else \
        TEST_NOCREDIT_SSN
    assert reservation["executeAt"] == STARTS_AT
    assert_isdatetime(reservation["createdAt"])


class TestSubscriptionV1Resource:
    def test_create(self, client):
        resp = create_subscription(client)
        data = resp.data
        payload = data["payload"]

        assert_isdatetime(data["createdAt"])
        assert_isdate(payload["startsAt"])
        assert_subscription(payload)

    def test_create_with_no_credit(self, client):
        with pytest.raises(FailureStatusError) as excinfo:
            create_subscription(client, credit=False)
        exc = excinfo.value
        assert exc.data
        assert "payload" not in exc.data  # Expecting no payload
        assert exc.status == "CUSTOMER_NOT_CREDIBLE"

    # TODO: Test with mock instead.
    # TODO: Move the test from here, as we are testing a
    #       hack not related to the subscription API
    def test_create_with_missing_amount(self, client):
        with pytest.raises(BadDataError) as excinfo:
            client.subscription.create(
                currency="SEK", interval="MONTHLY", ssn=TEST_CREDIT_SSN,
                merchantId="paylevo", country="SE")
        exc = excinfo.value
        assert exc.status == "Missing amount."
        assert exc.data is None

    def test_regret(self, client):
        resp = create_subscription(client)
        subscription_id = resp.data["payload"]["subscriptionId"]
        assert_subscription(resp.data["payload"])

        resp = client.subscription.regret(subscription_id)
        assert resp.data["payload"]["state"] == "REGRETTED"
        assert resp.data["payload"]["subscriptionId"] == subscription_id

        # It is not regrettable when it has been regretted
        with pytest.raises(FailureStatusError) as excinfo:
            client.subscription.regret(subscription_id)
        exc = excinfo.value
        assert exc.status == "NOT_MODIFIABLE"

    def test_search(self, client):
        # NOTE: merchantItemId should not be used as an identifier.
        # It is only used here like that here, because we can't search
        # on merchantOrderId/merchantSubscriptionId for the moment.

        # Use an identifier we can later find
        identifier = str(uuid4())
        resp = create_subscription(client, merchantItemId=identifier)
        assert_subscription(resp.data["payload"])
        assert resp.data["payload"]["merchantItemId"] == identifier

        resp = client.subscription.search(merchantItemId=identifier)
        payload = resp.data["payload"]
        assert len(payload) == 1

        subscription = payload[0]
        assert_isdatetime(subscription["createdAt"])
        assert_subscription(subscription)
        assert subscription["merchantItemId"] == identifier

    # TODO: Test with mock instead, this is an API test.
    def test_search_with_no_criteria(self, client):
        with pytest.raises(BadDataError) as excinfo:
            client.subscription.search()
        exc = excinfo.value
        # Invalid JSON because the server cannot parse an
        # empty JSON object for some reason. It is also
        # possible that requests isn't sending empty dicts.
        assert exc.status == "INVALID_JSON"

    def test_update(self, client):
        resp = create_subscription(client)
        assert_subscription(resp.data["payload"])
        subscription_id = resp.data["payload"]["subscriptionId"]

        resp = client.subscription.update(subscription_id, maxExecutions=2)
        assert resp.data["payload"]["subscriptionId"] == subscription_id
        assert resp.data["payload"]["maxExecutions"] == 2

    def test_query(self, client):
        resp = create_subscription(client)
        assert_subscription(resp.data["payload"])
        subscription_id = resp.data["payload"]["subscriptionId"]

        resp = client.subscription.query(subscription_id)
        assert resp.data["payload"]["subscriptionId"] == subscription_id

    # TODO: Test with mock instead, this is actually an API test.
    def test_query_with_nonexistent_resource(self, client):
        with pytest.raises(NotFoundError):
            client.subscription.query(10000)

    def test_list_log(self, client):
        subresp = create_subscription(client)
        subscription_id = subresp.data["payload"]["subscriptionId"]

        resp = client.subscription.list_log(subscription_id)
        payload = resp.data["payload"]
        assert len(payload) > 0
        assert_isdatetime(payload[0]["createdAt"])


class TestCheckoutSessionV1Resource:
    def test_create_session(self, client):
        resp = client.checkout_session.create(
            transactions=[{"amount": 100, "currency": "SEK"}],
            merchantId="paylevo-check",
            country="SE")
        assert isinstance(resp.data["payload"]["sessionId"], uuid.UUID)
        assert_isdatetime(resp.data["createdAt"])


class TestCreditCheckV2Resource:
    @pytest.mark.xfail
    def test_create_check(self, client):
        resp = client.creditcheck.create(ssn=TEST_CREDIT_SSN)
        assert "payload" in resp.data

    def test_search(self, client):
        resp = client.creditcheck.search(ssn=TEST_CREDIT_SSN)
        assert "payload" in resp.data


@pytest.mark.xfail
class TestReservationV2Resource:
    def test_create(self, client):
        resp = create_reservation(client)
        assert_reservation(payload=resp.data["payload"])

    def test_regret(self, client):
        resp = create_reservation(client)

        res_id = resp.data["payload"][0]["reservationId"]
        resp_2 = client.reservation.regret(res_id)
        assert resp_2.data["payload"]["state"] == "REGRETTED"
        assert resp_2.data["payload"]["reservationId"] == res_id


