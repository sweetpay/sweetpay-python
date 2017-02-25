import logging
import uuid
from functools import wraps

from . import errors
from .constants import LOGGER_NAME, SUBSCRIPTION, CREDITCHECK, CHECKOUT_SESSION
from .resources import SubscriptionV1, CreditcheckV2, CheckoutSessionV1
from .base import BaseResource
from .utils import decode_datetime, decode_date, decode_attachment, \
    encode_attachment

__all__ = [
    "logger", "SweetpayClient", "validates", "LOGGER_NAME",
    "SUBSCRIPTION", "CREDITCHECK", "CHECKOUT_SESSION", "errors",
    "decode_date", "decode_datetime", "decode_attachment",
    "encode_attachment", "clear_validators", "register_default_validators"
]

logger = logging.Logger(LOGGER_NAME)


class SweetpayClient(object):
    """The developer-interface for the API.

    Create an instance of this class to gain access to the SDK."""

    _RESOURCE_MAPPER = {
        (SubscriptionV1.namespace, 1): SubscriptionV1,
        (CreditcheckV2.namespace, 2): CreditcheckV2,
        (CheckoutSessionV1.namespace, 1): CheckoutSessionV1,
        (None, None): BaseResource
    }

    def __init__(self, api_token, stage, version, timeout=15,
                 use_validators=True):
        """Configure the API with default values.

        :param api_token: The API token provided by SweetPay.
        :param stage: A boolean indicating whether to use the stage
                      or production environment.
        :param version: A mapping/dict indicating which versions of
                        the APIs to use.
        :param timeout: Optional. The request timeout, defaults to 15.
        :param use_validators: Optional. Whether to use the validator
                               functionality. Defaults to `True`.
        """
        self.api_token = api_token
        self.stage = stage
        self.version = version
        self.timeout = timeout
        self.use_validators = use_validators

        # Create the resources.
        for namespace, version in version.items():
            resource_cls = self._get_resource_cls(namespace, version)
            resource = resource_cls(**self._get_resource_arguments(namespace))
            setattr(self, namespace, resource)

    @classmethod
    def _get_resource_cls(cls, namespace, version):
        try:
            return cls._RESOURCE_MAPPER[(namespace, version)]
        except KeyError:
            raise ValueError(
                "No resource with the namespace={0} and "
                "version={1}".format(namespace, version))

    def _get_resource_arguments(self, namespace):
        return {
            "api_token": self.api_token, "stage": self.stage,
            "version": self.version[namespace], "timeout": self.timeout,
            "use_validators": self.use_validators
        }


def validates(*args):
    """Decorator to use for adding validating resources.

    :param args: If supplying only 1 argument, supply the path
                 as the argument. This will add the validator
                 for all resources.
                 If supplying 3 arguments, supply the resource
                 as the first argument, the version as the second argument
                 and the path as the third argument. This will add the
                 validator for the specified resource only.
    """
    # Validate arguments. We do this as we want to allow both
    # one or two.
    if len(args) == 1:
        key = (None, None)
        path = args[0]
    elif len(args) == 3:
        key = (args[0], args[1])
        path = args[2]
    else:
        raise TypeError("Too few or many arguments passed, expecting 1 or 3")

    # Get the resource
    resource = SweetpayClient._get_resource_cls(*key)

    def outer(func):
        # Set the validator on the resource
        resource.validates(*path)(func)
        @wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)
        return inner
    return outer


def register_default_validators():
    """Register the default out-of-the-box validators."""

    @validates(["createdAt"])
    def validate_created_at(value):
        if value:
            return decode_datetime(value)
        return value

    @validates("subscription", 1, ["payload", "startsAt"])
    def validate_starts_at(value):
        if value:
            return decode_date(value)
        return value

    @validates("subscription", 1, ["payload", "createdAt"])
    def validate_payload_created_at(value):
        if value:
            return decode_datetime(value)
        return value

    @validates("subscription", 1, ["payload", "nextExecutionAt"])
    def validate_payload_next_execution_at(value):
        if value:
            return decode_datetime(value)
        return value

    @validates("subscription", 1, ["payload", "lastExecutionAt"])
    def validate_payload_last_execution_at(value):
        if value:
            return decode_datetime(value)
        return value

    @validates("subscription", 1, ["payload"])
    def validate_payload_when_list(value):
        if isinstance(value, list):
            for data in value:
                # We make a check here as to not break anything if
                # the API changes.
                if "createdAt" in data:
                    data["createdAt"] = decode_datetime(data["createdAt"])

                # Check whether we are listing log data or subscriptions
                if "startsAt" in data:
                    # We are handling subscriptions
                    data["startsAt"] = decode_date(data["startsAt"])
                if "lastExecutionAt" in data:
                    # We are handling subscriptions
                    data["lastExecutionAt"] = decode_date(
                        data["lastExecutionAt"])
                if "nextExecutionAt" in data:
                    # We are handling subscriptions
                    data["nextExecutionAt"] = decode_date(
                        data["nextExecutionAt"])

                if "sessionId" in data:
                    # We are handling log data.
                    data["sessionId"] = uuid.UUID(data["sessionId"])
        return value

    @validates("checkout_session", 1, ["payload", "sessionId"])
    def validate_starts_at(value):
        if value:
            return uuid.UUID(value)
        return value

    @validates("creditcheck", 2, ["payload"])
    def validate_payload_when_list(value):
        if isinstance(value, list):
            for data in value:
                # Convert all log entries
                for log in data.get("log", []):
                    if "createdAt" in log:
                        log["createdAt"] = decode_datetime(log["createdAt"])
                    if "sessionId" in log:
                        # We are handling log data.
                        log["sessionId"] = uuid.UUID(log["sessionId"])
        return value


def clear_validators():
    """Remove all registered validators."""
    BaseResource.clear_validators()


# Register default validators.
register_default_validators()
