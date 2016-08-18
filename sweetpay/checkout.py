"""
Copyright (C) 2015 David Buresund - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by David Buresund <david.buresund@gmail.com>, September 2015
"""
from marshmallow import fields
from .utils import BaseClient, BaseSchema, BaseResource

__all__ = ["CheckoutSession", "CheckoutClient"]


class TransactionSchema(BaseSchema):
    """The Schema representing the Transaction object"""
    currency = fields.String()
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


class SubscriptionSchema(BaseSchema):
    """The Schema representing the Subscription object"""
    currency = fields.String()
    amount = fields.Float()
    interval = fields.String()
    starts_at = fields.Date(dump_to="startsAt")
    ends_at = fields.Date(dump_to="endsAt")
    max_executions = fields.Integer(dump_to="maxExecutions")
    execution_delay = fields.Integer(dump_to="executionDelay")

    merchant_subscription_id = fields.String(dump_to="merchantSubscriptionId")
    merchant_item_id = fields.String(dump_to="merchantItemId")
    number_of_items = fields.Float(dump_to="numberOfItems")
    item_unit = fields.String(dump_to="itemUnit")
    amount_per_item = fields.String(dump_to="amountPerItem")


class NameSchema(BaseSchema):
    """The Schema representing the Name object"""
    first = fields.String()
    last = fields.String()
    org = fields.String()


class AddressSchema(BaseSchema):
    """The Schema representing the Address object"""
    street = fields.String()
    zip = fields.String()
    city = fields.String()
    region = fields.String()
    country = fields.String()
    care_of = fields.String(load_from="careOf")


class CustomerSchema(BaseSchema):
    """The Schema representing the Customer object"""
    phone = fields.String()
    ssn = fields.String()
    org = fields.String()
    email = fields.String()
    name = fields.Nested(NameSchema)
    address = fields.Nested(AddressSchema)


class PayloadSchema(BaseSchema):
    """The Schema representing the Payload object"""
    url = fields.URL()
    session_id = fields.UUID(load_from="sessionId")
    status = fields.String()


class EnvelopeSchema(BaseSchema):
    """The Schema representing the Envelope object"""
    created_at = fields.DateTime(load_from="createdAt")
    status = fields.String()
    payload = fields.Nested(PayloadSchema)
    version = fields.String()


class CallbackPayloadSchema(BaseSchema):
    """The Schema representing the CallbackPayload object"""
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


class CallbackEnvelope(BaseSchema):
    """The Schema representing the CallbackEnvelope object"""
    created_at = fields.DateTime(load_from="createdAt")
    sent_at = fields.DateTime(load_from="sentAt")
    callback_id = fields.Integer(load_from="callbackId")
    version = fields.String()
    event = fields.String()
    payload = fields.Nested(CallbackPayloadSchema)


class VerifyPurchaseReplySchema(BaseSchema):
    """The Schema representing the VerifyPurchaseReply object"""
    comment = fields.String()
    status = fields.String()


class VerifyPurchaseBodySchema(BaseSchema):
    """The Schema representing the VerifyPurchaseBody object"""
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


# TODO: Test for all camel to snake and vice versa.
class CreateSessionRequestSchema(BaseSchema):
    """The Schema representing the CreateSessionRequest object"""
    country = fields.String()
    merchant_id = fields.String(dump_to="merchantId")
    transactions = fields.Nested(TransactionSchema, many=True)
    subscriptions = fields.Nested(SubscriptionSchema, many=True)
    redirect_target = fields.String(dump_to="redirectTarget")
    redirect_on_failure_url = fields.URL(dump_to="redirectOnFailureUrl")
    redirect_on_success_url = fields.URL(dump_to="redirectOnSuccessUrl")
    callback_on_failure_url = fields.URL(dump_to="callbackOnFailureUrl")
    callback_on_success_url = fields.URL(dump_to="callbackOnSuccessUrl")

    verify_purchase_url = fields.URL(dump_to="verifyPurchaseUrl")
    merchant_terms_url = fields.URL(dump_to="merchantTermsUrl")

    language = fields.String()

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

    payment_method = fields.String(dump_to="paymentMethod")
    hold_execution = fields.Boolean(dump_to="holdExecution")


class CheckoutClient(BaseClient):
    """The client used to connect to the checkout API"""

    @property
    def url(self):
        """Return the stage or production URL, depending on the settings."""
        if self.stage:
            return self.stage_url
        else:
            return self.production_url

    @property
    def stage_url(self):
        """Return the stage URL."""
        return "https://checkout.stage.paylevo.com/v{0}".format(self.version)

    @property
    def production_url(self):
        """Return the production URL."""
        return "https://checkout.paylevo.com/v{0}".format(self.version)

    def create_session(self, **params):
        """Create a checkout session.

        :param params: The parameters to pass on to the marshmallow

                deserialization, and then pass on to the server.
        :raises: marshmallow.ValidationError if a param is invalid,
                requests.RequestException if the request fails.
        :returns: Return a dictionary with the keys "response",
                "status_code", "data" and "raw_data".
        """
        url = self.build_url("session", "create")
        return self.make_request(url, "POST", EnvelopeSchema(),
                                 CreateSessionRequestSchema, params)


class CheckoutSession(BaseResource):
    """The checkout session resource."""

    CLIENT_CLS = CheckoutClient

    @classmethod
    def create(cls, **params):
        return cls.get_client().create_session(**params)
