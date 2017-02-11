# -*- coding: utf-8 -*-
"""
Helper functions.
"""

from functools import reduce
import operator

import dateutil.parser
from dateutil import tz
from datetime import datetime
from .constants import DATE_FORMAT


def decode_datetime(value, to_utc=True):
    """Decode a datetime string.

    :param to_utc: Whether to convert the timezone to UTC or not.
    """
    if not value:
        raise ValueError("value parameter cannot be empty")

    dt = dateutil.parser.parse(value)
    if to_utc:
        utc = tz.gettz("UTC")
        dt = dt.astimezone(utc)
    return dt


def decode_date(value):
    """Decode a date string."""
    # We cannot convert the datetime to utc, as the
    # starts_at is based on a Swedish datetime
    return datetime.strptime(value, DATE_FORMAT).date()


def getfromdict(datadict, maplist):
    """Get an item from a dict, based on a list of keys."""
    return reduce(operator.getitem, maplist, datadict)


def setindict(datadict, maplist, value):
    """Set an item in a dict, based on a list of keys."""
    getfromdict(datadict, maplist[:-1])[maplist[-1]] = value
