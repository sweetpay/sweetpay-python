"""Helper functions."""
import json
import logging
from base64 import b64decode, b64encode

from datetime import datetime
from .constants import DATE_FORMAT, LOGGER_NAME

logger = logging.Logger(LOGGER_NAME)


def decode_date(value):
    """Decode a date string.

    :param value: The string to convert into a date.
    :return: A `datetime.date` object.
    """
    # We cannot convert the datetime to utc, as the
    # starts_at is based on a Swedish datetime
    return datetime.strptime(value, DATE_FORMAT).date()


def encode_attachment(attachment):
    """Helper function to encode a Python object to a b64 encoded value.

    This function is supposed to work as a helper, if you feel
    like specifying a JSON object as an attachment, when
    creating for example a subscription.

    :param attachment: The python value to encode.
    :return: A b64 encoded object as a string.
    """
    return b64encode(json.dumps(attachment).encode()).decode()


def decode_attachment(attachment):
    """Helper function to decode an attachment from b64 to a Python object.

    :param attachment: The b64 encoded value to decode as a string.
    :return: A Python object of the decoded attachment.
    """
    return json.loads(b64decode(attachment).decode())
