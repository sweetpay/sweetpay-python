from marshmallow import fields

from .utils import BaseClient, BaseSchema, BaseResource

__all__ = ["Creditcheck", "CreditcheckClient"]


class NameSchema(BaseSchema):
    """The v representing the Name object"""
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
    care_of = fields.String(load_from="careOf", dump_to="careOf")


class CustomerSchema(BaseSchema):
    """The Schema representing the Customer object"""
    customer_id = fields.Integer(load_from="customerId")
    country = fields.String()

    phone = fields.String()
    ssn = fields.String()
    org = fields.String()
    email = fields.String()
    name = fields.Nested(NameSchema)
    address = fields.Nested(AddressSchema)

    merchant_customer_id = fields.String(load_from="merchantCustomerId")


class CreditSchema(BaseSchema):
    operator_id = fields.String(load_from="operatorId")
    currency = fields.String()
    credit_limit = fields.Decimal(load_from="creditLimit")
    debt = fields.Decimal()
    statuses = fields.List(fields.String())


class MoneySchema(BaseSchema):
    amount = fields.Decimal()
    currency = fields.String()


class LogEntrySchema(BaseSchema):
    operator_id = fields.String(load_from="operatorId")
    merchant_id = fields.String(load_from="merchantId")
    status = fields.String()

    created_at = fields.DateTime(load_from="createdAt")
    customer_id = fields.Integer(load_from="customerId")
    decision = fields.String()
    limit = fields.Nested(MoneySchema)
    session_id = fields.UUID(load_from="sessionId")


class CreditcheckSchema(BaseSchema):
    """The Schema representing the CreditCheck object"""
    credits = fields.List(fields.Nested(CreditSchema))
    log = fields.List(fields.Nested(LogEntrySchema))
    customer = fields.Nested(CustomerSchema)


class BaseEnvelopeSchema(BaseSchema):
    """The schema representing the base Envelope object"""
    status = fields.String()
    version = fields.String()


class EnvelopeSchema(BaseEnvelopeSchema):
    """The Schema representing the Envelope object"""
    payload = fields.Nested(CreditcheckSchema)


class SearchEnvelopeSchema(BaseEnvelopeSchema):
    """The Schema representing the Search Envelope object"""
    payload = fields.Nested(CreditcheckSchema, many=True)


class CreditcheckRequestSchema(BaseSchema):
    """The Schema representing the CreateSessionRequest object"""
    country = fields.String()
    language = fields.String()
    merchant_id = fields.String(dump_to="merchantId")
    mechant_session_id = fields.String(dump_to="merchantSessionId")
    merchant_customer_id = fields.String(dump_to="merchantCustomerId")

    ssn = fields.String()
    org = fields.String()
    phone = fields.String()
    email = fields.String()
    name = fields.Nested(NameSchema)
    address = fields.Nested(AddressSchema)

    currency = fields.String()
    amount = fields.Decimal()

    ignore_cache = fields.Boolean(dump_to="ignoreCache")


class CreditcheckSearchRequestSchema(BaseSchema):
    country = fields.String()
    operator_id = fields.String(dump_to="operatorId")

    merchant_id = fields.String(dump_to="merchantId")
    merchant_customer_id = fields.String(dump_to="merchantCustomerId")

    email = fields.String()
    phone = fields.String()
    ssn = fields.String()
    org = fields.String()
    name = fields.String()
    address = fields.String()

    decision = fields.String()
    from_ = fields.Date(attribute="from", dump_to="from")
    until = fields.Date()


class CreditcheckClient(BaseClient):
    """The client used to connect to the creditcheck API"""

    @property
    def stage_url(self):
        """Return the stage URL."""
        return "https://api.stage.kriita.com/creditcheck"

    @property
    def production_url(self):
        """Return the production URL."""
        return "https://api.kriita.com/creditcheck"

    def make_check(self, **params):
        """Make a credit check.

        :param params: The parameters to pass on to the marshmallow
                deserialization, and then pass on to the server.
        :raises: marshmallow.ValidationError if a param is invalid,
                requests.RequestException if the request fails.
        :returns: Return a dictionary with the keys "response",
                "status_code", "data" and "raw_data".
        """
        url = self.build_url("check")
        return self.make_request(url, "POST", EnvelopeSchema(),
                                 CreditcheckRequestSchema, params)

    def search_checks(self, **params):
        url = self.build_url("search")
        return self.make_request(url, "POST", SearchEnvelopeSchema(),
                                 CreditcheckSearchRequestSchema, params)


class Creditcheck(BaseResource):
    """The creditcheck resource."""

    CLIENT_CLS = CreditcheckClient
    namespace = "creditcheck"

    @classmethod
    def create(cls, *args, **params):
        return cls.make_request("make_check", *args, **params)

    @classmethod
    def search(cls, *args, **params):
        return cls.make_request("search_checks", *args, **params)
