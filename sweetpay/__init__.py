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


def configure(api_token, stage, version, timeout=15):
    """Configure the API with default values.

    :param api_token: The API token provided by SweetPay.
    :param stage: A boolean indicating whether to use the stage
                  or production environment.
    :param version: A mapping/dict indicating which versions of
                    the APIs to use.
    :param timeout: The request timeout, defaults to 15.

    """
    BaseResource.api_token = api_token
    BaseResource.stage = stage
    BaseResource.version = version
    BaseResource.timeout = timeout
