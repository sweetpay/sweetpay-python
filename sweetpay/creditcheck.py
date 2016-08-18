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


class LogEntrySchema(BaseSchema):
    created_at = fields.DateTime(load_from="createdAt")
    customer_id = fields.Integer(load_from="customerId")
    decision = fields.String()
    limit = fields.Decimal()
    session_id = fields.UUID(load_from="sessionId")


class CreditcheckSchema(BaseSchema):
    """The Schema representing the CreditCheck object"""
    credits = fields.List(fields.Nested(CreditSchema))
    log = fields.List(fields.Nested(LogEntrySchema))
    customer = fields.Nested(CustomerSchema)


class EnvelopeSchema(BaseSchema):
    """The Schema representing the Envelope object"""
    created_at = fields.DateTime(load_from="createdAt")
    status = fields.String()
    payload = fields.Nested(CreditcheckSchema)
    version = fields.String()


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
    def url(self):
        """Return the stage or production URL, depending on the settings."""
        if self.stage:
            return self.stage_url
        else:
            return self.production_url

    @property
    def stage_url(self):
        """Return the stage URL."""
        return "https://api.stage.kriita.com/creditcheck/v{0}".format(
            self.version)

    @property
    def production_url(self):
        """Return the production URL."""
        return "https://api.kriita.com/creditcheck/v{0}".format(self.version)

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
        url = self.build_url("log")
        return self.make_request(url, "POST", EnvelopeSchema(),
                                 CreditcheckSearchRequestSchema, params)


class Creditcheck(BaseResource):
    """The creditcheck resource."""

    CLIENT_CLS = CreditcheckClient

    @classmethod
    def create(cls, **params):
        return cls.get_client().make_check(**params)

    @classmethod
    def search(cls, **params):
        return cls.get_client().search_checks(**params)
