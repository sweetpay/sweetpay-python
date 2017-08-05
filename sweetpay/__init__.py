import logging

from . import errors
from .constants import SUBSCRIPTION, CREDITCHECK, CHECKOUT_SESSION
from .resources import SubscriptionV1, CreditcheckV2, CheckoutSessionV1
from .base import BaseResource, SweetpayConnector
from .utils import decode_datetime, decode_date, decode_attachment, \
    encode_attachment

__all__ = [
    "logger", "SweetpayClient", "SUBSCRIPTION", "CREDITCHECK",
    "CHECKOUT_SESSION", "errors", "decode_date", "decode_datetime",
    "decode_attachment", "encode_attachment",
]


class SweetpayClient:
    """The developer-interface for the API.

    Create an instance of this class to gain access to the SDK."""

    _RESOURCE_MAPPER = {
        (SubscriptionV1.namespace, 1): SubscriptionV1,
        (CreditcheckV2.namespace, 2): CreditcheckV2,
        (CheckoutSessionV1.namespace, 1): CheckoutSessionV1,
        (None, None): BaseResource
    }

    def __init__(self, api_token, stage, version, timeout=15, connector=None):
        """Configure the API with default values.

        :param api_token: The API token provided by SweetPay.
        :param stage: A boolean indicating whether to use the stage
                      or production environment.
        :param version: A mapping/dict indicating which versions of
                        the APIs to use.
        :param timeout: Optional. The request timeout, defaults to 15.
        :param connector: The connector to use for contacting the API.
            Defaults to SweetpayConnector.
        """
        self.api_token = api_token
        self.stage = stage
        self.version = version
        self.timeout = timeout
        self.connector = connector or SweetpayConnector

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
            "connector": self.connector
        }
