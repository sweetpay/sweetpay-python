"""
Copyright (C) 2015 David Buresund - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by David Buresund <david.buresund@gmail.com>, September 2015
"""
import json
import os
from requests import Session, RequestException
from marshmallow import Schema, fields, ValidationError
import datetime

__all__ = ["CheckoutClient", "RequestException", "ValidationError"]


class SweetpayJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        else:
            return super(SweetpayJSONEncoder, self).default(obj)


VALID_COUNTRIES = ["SE", "FI", "DE", "NO"]
VALID_CURRENCIES = ["SEK", "EUR", "USD"]
VALID_REDIRECT_TARGETS = ["CLOSE", "TOP", "ELSE"]
VALID_LANGUAGES = ["sv", "en", "de", "fi", "nb"]
VALID_PAYMENT_METHODS = ["INVOICE"]
VALID_INTERVALS = ["WEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"]


class TransactionSchema(Schema):
    currency = fields.String(
        validate=lambda cu: cu.upper() in VALID_CURRENCIES
    )
    amount = fields.Float()
    merchant_transaction_id = fields.String(dump_to="merchantTransactionId")
    merchant_item_id = fields.String(dump_to="merchantItemId")
    raw_amount = fields.Float(dump_to="rawAmount")
    number_of_items = fields.Float(dump_to="numberOfItems")
    item_unit = fields.String(dump_to="itemUnit")
    amount_per_item = fields.String(dump_to="amountPerItem")
    raw_amount_per_item = fields.String(dump_to="rawAmountPerItem")
    vat = fields.Float()
    executed_at = fields.Date(load_from="executedAt", load_only=True)
    comment = fields.String()


class SubscriptionSchema(Schema):
    currency = fields.String(
        validate=lambda cu: cu.upper() in VALID_CURRENCIES
    )
    amount = fields.Float()
    interval = fields.String(
        validate=lambda intr: intr.upper() in VALID_INTERVALS
    )
    starts_at = fields.Date(dump_to="startsAt")
    ends_at = fields.Date(dump_to="endsAt")
    max_executions = fields.Integer(dump_to="maxExecutions")
    execution_delay = fields.Integer(dump_to="executionDelay")

    merchant_subscription_id = fields.String(dump_to="merchantSubscriptionId")
    merchant_item_id = fields.String(dump_to="merchantItemId")
    number_of_items = fields.Float(dump_to="numberOfItems")
    item_unit = fields.String(dump_to="itemUnit")
    amount_per_item = fields.String(dump_to="amountPerItem")


class NameSchema(Schema):
    first = fields.String()
    last = fields.String()
    org = fields.String()


class AddressSchema(Schema):
    street = fields.String()
    zip = fields.String()
    city = fields.String()
    region = fields.String()
    # TODO: Remove duplicate code
    country = fields.String(validate=lambda x: x.upper() in VALID_COUNTRIES)
    care_of = fields.String(dump_to="careOf")


class CustomerSchema(Schema):
    phone = fields.String()
    ssn = fields.String()
    org = fields.String()
    email = fields.String()
    name = fields.Nested(NameSchema)
    address = fields.Nested(AddressSchema)


class PayloadSchema(Schema):
    url = fields.URL()
    session_id = fields.UUID(load_from="sessionId")
    status = fields.String()


class EnvelopeSchema(Schema):
    created_at = fields.DateTime(load_from="createdAt")
    status = fields.String()
    payload = fields.Nested(PayloadSchema)
    version = fields.String()


class CallbackPayloadSchema(Schema):
    session_id = fields.UUID(load_from="sessionId")
    merchant_session_id = fields.String(load_from="merchantSessionId")
    merchant_customer_id = fields.String(load_from="merchant_customer_id")
    merchant_order_id = fields.String(load_from="merchantOrderId")
    executed_at = fields.String(load_from="executedAt")
    status = fields.String()
    currency = fields.String()
    amount = fields.Float()
    reservation_id = fields.Integer(load_from="reservation_id")
    customer = fields.Nested(CustomerSchema)
    billing = fields.Nested(CustomerSchema)


class CallbackEnvelope(Schema):
    created_at = fields.DateTime(load_from="createdAt")
    sent_at = fields.DateTime(load_from="sentAt")
    callback_id = fields.Integer(load_from="callbackId")
    version = fields.String()
    event = fields.String()
    payload = fields.Nested(CallbackPayloadSchema)


class VerifyPurchaseReplySchema(Schema):
    comment = fields.String()
    status = fields.String()


class VerifyPurchaseBodySchema(Schema):
    session_id = fields.UUID()
    merchant_session_id = fields.String(load_from="merchantSessionId")
    merchant_customer_id = fields.String(load_from="merchantCustomerId")
    merchant_order_id = fields.String(load_from="merchantOrderId")
    executed_at = fields.Date(load_from="executedAt")
    status = fields.String()
    currency = fields.String()
    amount = fields.Float()
    reservation_id = fields.Integer(load_from="reservationId")
    customer = fields.Nested(CustomerSchema)
    billing = fields.Nested(CustomerSchema)


class CreateSessionRequestSchema(Schema):
    country = fields.String(
        validate=lambda x: x.upper() in VALID_COUNTRIES, required=True
    )
    merchant_id = fields.String(required=True, dump_to="merchantId")
    # TODO: Required if not subscriptions
    transactions = fields.Nested(TransactionSchema, many=True, required=True)
    subscriptions = fields.Nested(SubscriptionSchema, many=True, required=True)
    # TODO: Test for all camel to snake
    redirect_target = fields.String(
        validate=lambda rt: rt.upper() in VALID_REDIRECT_TARGETS,
        dump_to="redirectTarget"
    )
    redirect_on_failure_url = fields.URL(dump_to="redirectOnFailureUrl")
    redirect_on_success_url = fields.URL(dump_to="redirectOnSuccessUrl")
    callback_on_failure_url = fields.URL(dump_to="callbackOnFailureUrl")
    callback_on_success_url = fields.URL(dump_to="callbackOnSuccessUrl")

    verify_purchase_url = fields.URL(dump_to="verifyPurchaseUrl")
    merchant_terms_url = fields.URL(dump_to="merchantTermsUrl")

    language = fields.String(
        validate=lambda lang: lang.upper() in VALID_LANGUAGES
    )

    mechant_session_id = fields.String(dump_to="merchantSessionId")
    merchant_customer_id = fields.String(dump_to="merchantCustomerId")
    phone = fields.String()
    email = fields.String()

    billing_phone = fields.String(dump_to="billingPhone")
    billing_email = fields.String(dump_to="billingEmail")
    billing_name = fields.Nested(NameSchema, dump_to="billingName")
    billing_address = fields.Nested(AddressSchema, dump_to="billingAddress")

    delivery_phone = fields.String(dump_to="deliveryPhone")
    delivery_email = fields.String(dump_to="deliveryEmail")
    delivery_name = fields.Nested(NameSchema, dump_to="deliveryName")
    delivery_address = fields.Nested(AddressSchema, dump_to="deliveryAddress")

    merchant_order_id = fields.String(dump_to="merchantOrderId")

    payment_method = fields.String(
        validate=lambda pm: pm.upper() in VALID_PAYMENT_METHODS,
        dump_to="paymentMethod"
    )
    hold_execution = fields.Boolean(dump_to="holdExecution")


class CheckoutClient(object):

    def __init__(self, auth_token, stage, version=1):
        self.stage = stage
        self.version = version
        self.auth_token = auth_token
        self.session = Session()
        self.session.headers.update({
            "Authorization": auth_token, "Content-Type": "application/json",
            "Accept": "application/json", "User-Agent": "Python-SDK"
        })

    @property
    def url(self):
        if self.stage:
            return (
                "https://checkout.stage.paylevo.com/v{0}".format(self.version)
            )
        else:
            return (
                "https://checkout.paylevo.com/v{0}".format(self.version)
            )

    def build_url(self, *args):
        return os.path.join(self.url, *args)

    def create_session(self, **params):
        """Create a checkout session.

        :param params: The parameters to pass on to the marshmallow
                  deserialization, and then pass on to the server.
        :raises: marshmallow.ValidationError if a param is invalid,
                 requests.RequestException if the request fails.
        :returns: Return a dictionary with the keys "response",
                 "status_code", "data" and "raw_data".
        """
        try:
            dump_obj = CreateSessionRequestSchema(strict=True).dump(params)
        except ValidationError:
            raise
        else:
            data = SweetpayJSONEncoder().encode(dump_obj.data)

        try:
            resp = self.session.post(
                self.build_url("session", "create"), data=data
            )
        except RequestException:
            raise

        # Try to deserialize the response
        try:
            resp_json = resp.json()
        except (TypeError, ValueError):
            data = None
        else:
            data = EnvelopeSchema().load(resp_json).data
        return {
            "response": resp, "status_code": resp.status_code,
            "data": data, "raw_data": resp.text
        }
