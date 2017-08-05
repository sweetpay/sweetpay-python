"""Tests for all operations."""
from datetime import datetime, timedelta

import pytest
from sweetpay.constants import TEST_CREDIT_SSN, TEST_NOCREDIT_SSN
from sweetpay.errors import FailureStatusError, BadDataError, NotFoundError
from uuid import uuid4

# The startsAt to use for subscription. It is important that 
# this isn't today's date, as that is what the subscription 
# API defaults to. Also, the Sweetpay API does not allow the starstAt
# to be too far back in time, that's why we don't just hardcode it.
STARTS_AT = (datetime.utcnow() - timedelta(days=10)).date()


def create_subscription(client, credit=True, **extra):
    ssn = TEST_CREDIT_SSN if credit else TEST_NOCREDIT_SSN
    return client.subscription.create(
        amount={"amount": 10, "currency": "SEK"}, country="SE",  merchantId="sweetpay-demo",
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


class TestSubscriptionV1Resource:
    def test_create(self, client):
        # Execute
        data = create_subscription(client)
        
        # Verify
        assert_subscription(data["payload"])

    def test_create_with_no_credit(self, client):
        with pytest.raises(FailureStatusError) as excinfo:
            # Execute
            create_subscription(client, credit=False)
            
        # Verify
        exc = excinfo.value
        assert exc.data
        assert "payload" not in exc.data  # Expecting no payload
        assert exc.status == "CUSTOMER_NOT_CREDIBLE"

    # TODO: Test with mock instead.
    # TODO: Move the test from here, as we are testing a
    #       hack not related to the subscription API
    def test_create_with_missing_amount(self, client):
        with pytest.raises(BadDataError) as excinfo:
            # Execute
            client.subscription.create(
                currency="SEK", interval="MONTHLY", ssn=TEST_CREDIT_SSN,
                merchantId="paylevo", country="SE")

        # Verify
        exc = excinfo.value
        assert exc.status == "Missing amount."
        assert exc.data is None

    def test_regret(self, client):
        # Setup
        data = create_subscription(client)
        subscription_id = data["payload"]["subscriptionId"]

        # Execute
        data = client.subscription.regret(subscription_id)
        
        # Verify
        assert data["payload"]["state"] == "REGRETTED"
        assert data["payload"]["subscriptionId"] == subscription_id

    def test_search(self, client):
        # NOTE: merchantItemId should not be used as an identifier.
        # It is only used here like that here, because we can't search
        # on merchantOrderId/merchantSubscriptionId for the moment.

        # Use an identifier we can later find
        identifier = str(uuid4())
        create_subscription(client, merchantItemId=identifier)

        data = client.subscription.search(merchantItemId=identifier)
        payload = data["payload"]
        assert len(payload) == 1

        subscription = payload[0]
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
        # Setup
        data = create_subscription(client)
        subscription_id = data["payload"]["subscriptionId"]

        # Execute
        data = client.subscription.update(subscription_id, maxExecutions=2)

        # Verify
        assert data["payload"]["maxExecutions"] == 2

    def test_query(self, client):
        # Setup
        data = create_subscription(client)
        subscription_id = data["payload"]["subscriptionId"]

        # Execute
        data = client.subscription.query(subscription_id)

        # Verify
        assert data["payload"]["subscriptionId"] == subscription_id

    # TODO: Test with mock instead, this is actually an API test.
    def test_query_with_nonexistent_resource(self, client):
        with pytest.raises(NotFoundError):
            client.subscription.query(10000)

    def test_list_log(self, client):
        # Setup
        data = create_subscription(client)
        subscription_id = data["payload"]["subscriptionId"]

        # Execute
        data = client.subscription.list_log(subscription_id)

        # Verify
        payload = data["payload"]
        assert len(payload) > 0


class TestCheckoutSessionV1Resource:
    def test_create_session(self, client):
        data = client.checkout_session.create(
            transactions=[{"amount": 100, "currency": "SEK"}],
            merchantId="sweetpay-demo",
            country="SE")
        assert data


class TestCreditCheckV2Resource:
    @pytest.mark.xfail
    def test_create_check(self, client):
        data = client.creditcheck.create(ssn=TEST_CREDIT_SSN)
        assert "payload" in data

    def test_search(self, client):
        data = client.creditcheck.search(ssn=TEST_CREDIT_SSN)
        assert "payload" in data


@pytest.mark.xfail
class TestReservationV2Resource:
    def test_create(self, client):
        data = create_reservation(client)
        assert_reservation(payload=data["payload"])

    def test_regret(self, client):
        data = create_reservation(client)

        res_id = data["payload"][0]["reservationId"]
        resp_2 = client.reservation.regret(res_id)
        assert resp_2.data["payload"]["state"] == "REGRETTED"
        assert resp_2.data["payload"]["reservationId"] == res_id
