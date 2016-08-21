import json

from marshmallow import fields
from .utils import BaseClient, BaseSchema, BaseResource

__all__ = ["SubscriptionClient", "deserialize_callback_data", "Subscription"]


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
    care_of = fields.String(dump_to="careOf", load_from="careOf")


class CustomerSchema(BaseSchema):
    """The Schema representing the Customer object"""
    phone = fields.String()
    ssn = fields.String()
    org = fields.String()
    email = fields.String()
    name = fields.Nested(NameSchema)
    address = fields.Nested(AddressSchema)


class SubscriptionSchema(BaseSchema):
    """The Schema representing the Subscription object"""
    currency = fields.String()
    amount = fields.Decimal()
    state = fields.String()
    created_at = fields.DateTime(load_from="createdAt", load_only=True)

    nextExecutionAt = fields.Date(load_from="nextExecutionAt", load_only=True)
    last_execution_at = fields.Date(load_from="lastExecutionAt",
                                    load_only=True)
    executions = fields.Integer()
    merchant_id = fields.String(load_from="merchantId", load_only=True)

    interval = fields.String()
    starts_at = fields.Date(dump_to="startsAt", load_from="startsAt")
    ends_at = fields.Date(dump_to="endsAt", load_from="endsAt")
    max_executions = fields.Integer(dump_to="maxExecutions",
                                    load_from="maxExecutions")
    execution_delay = fields.Integer(dump_to="executionDelay",
                                     load_from="executionDelay")

    merchant_subscription_id = fields.String(dump_to="merchantSubscriptionId",
                                             load_from="merchantSubscriptionId"
                                             )
    merchant_item_id = fields.String(dump_to="merchantItemId",
                                     load_from="merchantItemId")
    number_of_items = fields.Float(dump_to="numberOfItems",
                                   load_from="numberOfItems")
    item_unit = fields.String(dump_to="itemUnit", load_from="itemUnit")
    amount_per_item = fields.String(dump_to="amountPerItem",
                                    load_from="itemUnit")

    subscription_id = fields.Integer(load_from="subscriptionId",
                                     dump_to="subscriptionId")
    billing = fields.Nested(CustomerSchema, load_only=True)
    customer = fields.Nested(CustomerSchema, load_only=True)


class LogSchema(BaseSchema):
    created_at = fields.DateTime(load_from="createdAt")
    event = fields.String()
    execution = fields.Integer()
    reservation_id = fields.Integer(load_from="reservationId")
    session_id = fields.UUID(load_from="sessionId")


class BaseEnvelopeSchema(BaseSchema):
    """The base schema representing the Envelope object"""
    created_at = fields.DateTime(load_from="createdAt")
    status = fields.String()
    payload = fields.Nested(SubscriptionSchema)
    version = fields.String()


class EnvelopeSchema(BaseEnvelopeSchema):
    """The Schema representing the Envelope object"""
    payload = fields.Nested(SubscriptionSchema)


class SearchEnvelopeSchema(BaseEnvelopeSchema):
    """The Schema representing the Envelope object"""
    payload = fields.Nested(SubscriptionSchema, many=True)


class LogEnvelopeSchema(BaseEnvelopeSchema):
    """The Schema representing the Envelope object"""
    payload = fields.Nested(LogSchema, many=True)


class CallbackEnvelope(BaseSchema):
    """The Schema representing the CallbackEnvelope object"""
    created_at = fields.DateTime(load_from="createdAt")
    sent_at = fields.DateTime(load_from="sentAt")
    callback_id = fields.Integer(load_from="callbackId")
    version = fields.String()
    event = fields.String()
    payload = fields.Nested(SubscriptionSchema)


class CreateSubscriptionRequestSchema(BaseSchema):
    """The Schema representing the CreateSessionRequest object"""
    country = fields.String()
    merchant_id = fields.String(dump_to="merchantId")
    language = fields.String()
    merchant_customer_id = fields.String(dump_to="merchantCustomerId")

    starts_at = fields.Date(dump_to="startsAt")
    ends_at = fields.Date(dump_to="endsAt")
    max_executions = fields.Integer(dump_to="maxExecutions")

    currency = fields.String()
    amount = fields.Decimal()

    comment = fields.String()
    vat = fields.Decimal()
    merchant_source = fields.String(dump_to="merchantSource")

    ssn = fields.String()
    org = fields.String()
    phone = fields.String()
    email = fields.String()
    name = fields.Nested(NameSchema)
    address = fields.Nested(AddressSchema)
    interval = fields.String()

    billing_phone = fields.String(dump_to="billingPhone")
    billing_email = fields.String(dump_to="billingEmail")
    billing_name = fields.Nested(NameSchema, dump_to="billingName")
    billing_address = fields.Nested(AddressSchema, dump_to="billingAddress")

    delivery_phone = fields.String(dump_to="deliveryPhone")
    delivery_email = fields.String(dump_to="deliveryEmail")
    delivery_name = fields.Nested(NameSchema, dump_to="deliveryName")
    delivery_address = fields.Nested(AddressSchema, dump_to="deliveryAddress")

    merchant_order_id = fields.String(dump_to="merchantOrderId")


class UpdateSubscriptionSchema(BaseSchema):
    starts_at = fields.Date(dump_to="startsAt")
    ends_at = fields.Date(dump_to="endsAt")
    max_executions = fields.Integer(dump_to="maxExecutions")


class SearchSubscriptionRequestSchema(BaseSchema):
    country = fields.String()
    merchant_id = fields.String(dump_to="merchantId")
    merchant_customer_id = fields.String(dump_to="merchantCustomerId")
    ssn = fields.String()
    org = fields.String()
    phone = fields.String()
    email = fields.String()
    name = fields.Nested(NameSchema)
    address = fields.Nested(AddressSchema)
    merchant_item_id = fields.String(dump_to="merchantItemId")
    subscription_state = fields.String(dump_to="subscriptionState")
    event = fields.String()
    until = fields.Date()
    from_ = fields.Date(attribute="from", dump_to="from")


class SubscriptionClient(BaseClient):
    """The client used to connect to the checkout API"""

    @property
    def stage_url(self):
        """Return the stage URL."""
        return "https://api.stage.kriita.com/subscription/" \
               "v{0}".format(self.version)

    @property
    def production_url(self):
        """Return the production URL."""
        return "https://api.kriita.com/subscription" \
               "/v{0}".format(self.version)

    def create_subscription(self, **params):
        """Create a subscription."""
        url = self.build_url("create")
        return self.make_request(url, "POST", EnvelopeSchema(),
                                 CreateSubscriptionRequestSchema, params)

    def regret_subscription(self, subscription_id):
        """Regret a subscription."""
        url = self.build_url(str(subscription_id), "regret")
        return self.make_request(url, "GET", EnvelopeSchema())

    def update_subscription(self, subscription_id, **params):
        """Update a subscription."""
        url = self.build_url(str(subscription_id), "update")
        return self.make_request(url, "POST", EnvelopeSchema(),
                                 UpdateSubscriptionSchema, params)

    def query_subscription(self, subscription_id):
        """Query a subscription."""
        url = self.build_url(str(subscription_id), "query")
        return self.make_request(url, "GET", EnvelopeSchema())

    def search_subscriptions(self, **params):
        """Search for subscriptions."""
        url = self.build_url("search")
        return self.make_request(url, "POST", SearchEnvelopeSchema(),
                                 SearchSubscriptionRequestSchema, params)

    def log_subscription(self, subscription_id):
        url = self.build_url(str(subscription_id), "log")
        return self.make_request(url, "GET", LogEnvelopeSchema())


def deserialize_callback_data(data, is_json_str=False):
    """Deserialize callback data

    :param data: The actual data to deserialize.
    :param is_json_str: A boolean indicating if the the
                        passed data is a JSON or a Python object.
    """
    if is_json_str:
        data = json.loads(data)
    return CallbackEnvelope().load(data).data


class Subscription(BaseResource):
    """The subscription resource."""

    CLIENT_CLS = SubscriptionClient

    @classmethod
    def create(cls, *args, **params):
        """Create a subscription."""
        return cls.make_request("create_subscription", *args, **params)

    @classmethod
    def query(cls, *args, **params):
        """Query a subscription for information."""
        return cls.make_request("query_subscription", *args, **params)

    @classmethod
    def update(cls, *args, **params):
        """Update a subscription."""
        return cls.make_request("update", *args, **params)

    @classmethod
    def search(cls, *args, **params):
        """Search for subscriptions."""
        return cls.make_request("search_subscriptions", *args, **params)

    @classmethod
    def list_log(cls, *args, **params):
        """List all of the log entries."""
        return cls.make_request("log_subscription", *args, **params)

    @classmethod
    def regret(cls, *args, **params):
        """Regret a subscription."""
        return cls.make_request("regret_subscription", *args, **params)
