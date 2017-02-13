# -*- coding: utf-8 -*-
import logging
from functools import wraps

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

    def _get_resource_arguments(self, namespace):
        return {
            "api_token": self.api_token, "stage": self.stage,
            "version": self.version[namespace], "timeout": self.timeout,
            "use_validators": self.use_validators
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


# TODO: Move into SweetpayClient and remove hardcoded properties
RESOURCE_MAPPER = {
    Subscription.namespace: Subscription,
    Creditcheck.namespace: Creditcheck,
    CheckoutSession.namespace: CheckoutSession,
    None: BaseResource
}
def validates(*args):
    """Decorator to use for adding validating resources.

    :param args: If supplying only 1 argument, supply the path
                 as the argument. This will add the validator
                 for all resources.
                 If supplying 2 arguments, supply the resource's
                 namespace as the first argument and the path as
                 the second argument. This will add the validator
                 for the specified resource only.
    """
    # Validate arguments. We do this as we want to allow both
    # one or two.
    if len(args) == 1:
        key = None
        path = args[0]
    elif len(args) == 2:
        key = args[0]
        path = args[1]
    else:
        raise TypeError("Too few or many arguments passed, expecting 1 or 2")

    # Get the resource from the mapper
    try:
        resource = RESOURCE_MAPPER[key]
    except KeyError:
        raise ValueError("No resource with namespace={0}".format(key))

    def outer(func):
        # Set the validator on the resource
        resource.validates(*path)(func)
        @wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)
        return inner
    return outer
