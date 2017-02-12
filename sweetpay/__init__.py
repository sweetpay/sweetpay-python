# -*- coding: utf-8 -*-
import logging

from .constants import LOGGER_NAME
from .checkout import CheckoutSession
from .subscription import Subscription
from .creditcheck import Creditcheck
from .base import BaseResource
from .utils import decode_datetime, decode_date, decode_attachment, \
    encode_attachment

logger = logging.Logger(LOGGER_NAME)


class SweetpayClient(object):
    _subscription = None
    _creditcheck = None
    _checkout_session = None

    def __init__(self, api_token, stage, version, timeout=15):
        """Configure the API with default values.

        :param api_token: The API token provided by SweetPay.
        :param stage: A boolean indicating whether to use the stage
                      or production environment.
        :param version: A mapping/dict indicating which versions of
                        the APIs to use.
        :param timeout: Optional. The request timeout, defaults to 15.
        """
        self.api_token = api_token
        self.stage = stage
        self.version = version
        self.timeout = timeout

    def _get_resource_arguments(self, namespace):
        return {
            "api_token": self.api_token, "stage": self.stage,
            "version": self.version[namespace], "timeout": self.timeout
        }

    @property
    def subscription(self):
        if not self._subscription:
            self._subscription = Subscription(
                **self._get_resource_arguments(Subscription.namespace))
        return self._subscription

    @property
    def creditcheck(self):
        if not self._creditcheck:
            self._creditcheck = Creditcheck(
                **self._get_resource_arguments(Creditcheck.namespace))
        return self._creditcheck

    @property
    def checkout_session(self):
        if not self._checkout_session:
            self._checkout_session = CheckoutSession(
                **self._get_resource_arguments(CheckoutSession.namespace))
        return self._checkout_session
