"""Helper functions."""
import json
from base64 import b64decode, b64encode
from functools import reduce
import operator

import dateutil.parser
from dateutil import tz
from datetime import datetime
from .constants import DATE_FORMAT


def decode_datetime(value, to_utc=True):
    """Decode a datetime string.

    :param value: The string to convert into a datetime.
    :param to_utc: Whether to convert the timezone to UTC or not.
    :raise ValueError: If the passed value is invalid, for
                       example if it is empty.
    :return: A `datetime.datetime` object.
    """
    if not value:
        raise ValueError("value parameter cannot be empty")

    dt = dateutil.parser.parse(value)
    if to_utc:
        # Make sure that it doesn't fail when the datetime is naive
        if dt.tzinfo is not None:
            utc = tz.gettz("UTC")
            dt = dt.astimezone(utc)
    return dt


def decode_date(value):
    """Decode a date string.

    :param value: The string to convert into a date.
    :return: A `datetime.date` object.
    """
    # We cannot convert the datetime to utc, as the
    # starts_at is based on a Swedish datetime
    return datetime.strptime(value, DATE_FORMAT).date()


def getfromdict(datadict, maplist):
    """Get an item from a dict, based on a list of keys."""
    return reduce(operator.getitem, maplist, datadict)


def setindict(datadict, maplist, value):
    """Set an item in a dict, based on a list of keys."""
    getfromdict(datadict, maplist[:-1])[maplist[-1]] = value


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
