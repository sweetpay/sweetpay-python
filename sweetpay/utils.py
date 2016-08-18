# -*- coding: utf-8 -*-

import json
import datetime
import logging
import os
from collections import namedtuple

from decimal import Decimal

from marshmallow import Schema
from marshmallow import ValidationError
from marshmallow import post_dump
from requests import Session

ResponseClass = namedtuple("ResponseClass",
                           ["response", "status_code", "data"])


class BaseResource(object):
    """The base resource."""
    CLIENT_CLS = None
    api_token = None
    stage = None
    version = None

    @classmethod
    def get_client(cls):
        if not cls.api_token or not cls.stage:
            raise ValueError("You must set an API token and decide whether "
                             "to use the stage environment or not before "
                             "using the SDK. Have a look at "
                             "`sweetpay.configure`")
        return cls.CLIENT_CLS(cls.api_token, cls.stage, cls.version)


def configure(api_token, stage, version=None):
    """Configure the API with global variables

    :param api_token: The API token provided by SweetPay.
    :param stage: A boolean indicating whether to use the stage
                  or production environment.
    :param version: An integer or string indicating which version
                    of the API to use. For example: 1
    :return: None
    """
    # We accomplish this by just setting some global variables
    # on the BaseResource
    BaseResource.api_token = api_token
    BaseResource.stage = stage
    BaseResource.version = version


class BaseSchema(Schema):
    """The base marshmallow schema"""
    pass


class SweetpayJSONEncoder(json.JSONEncoder):
    """A custom JSON encoder to support custom types."""
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        # Convert decimals to strings in order for it to
        # be money safe.
        elif isinstance(obj, Decimal):
            return str(obj)
        else:
            return super(SweetpayJSONEncoder, self).default(obj)


class BaseClient(object):
    """The super class used to create API clients."""

    def __init__(self, api_token, stage, version=None):
        """Initialize the checkout client used to talk to the checkout API.

        :param api_token: The authorization token to set in the
               Authorization header.
        :param stage: A boolean indicating if the stage server should
               be used or not. If set to False, the live server will be used.
        :param version: The version number of the API, defaults to 1.
        """
        self.stage = stage
        self.version = version or 1
        self.api_token = api_token

        # Setup the logger
        self.logger = logging.getLogger("sweetpay-sdk")

        # The session
        self.session = Session()
        self.session.headers.update({
            "Authorization": api_token, "Content-Type": "application/json",
            "Accept": "application/json", "User-Agent": "Python-SDK"
        })

    @property
    def stage_url(self):
        """Return the stage URL."""
        raise NotImplementedError("No URL for the stage server has "
                                  "been specified")

    @property
    def production_url(self):
        """Return the production URL."""
        raise NotImplementedError("No URL for the production server has "
                                  "been specified")

    @property
    def url(self):
        """Return the stage or production URL, depending on the settings."""
        if self.stage:
            return self.stage_url
        else:
            return self.production_url

    def build_url(self, *args):
        """Return a URL based on

        :param args: The arguments which will be used to build the path.
                For example: "path" and "to" creates the path "/path/to".
        :return: A complete URL as a string.
        """
        return os.path.join(self.url, *args)

    def make_request(self, url, method, respschema, reqschema=None,
                     params=None):
        """Make a request.

        :param params: The parameters to pass on to the marshmallow
                deserialization, and then pass on to the server.
        :param respschema: The schema to use for deserialization.
        :param params: The parameters passed by the client.
        :raises: marshmallow.ValidationError if a param is invalid,
                requests.RequestException if the request fails.
        :returns: Return a dictionary with the keys "response",
                "status_code", "data" and "raw_data".
        """

        logger = self.logger

        if method == "GET":
            logger.info("Sending request with method=GET to url=%s", url)
            resp = self.session.get(url)
        else:
            # TODO: Catch exception
            to_dump = reqschema().dump(params).data
            reqdata = SweetpayJSONEncoder().encode(to_dump)
            logger.info("Sending request with method=POST to url=%s and "
                        "parameters=%s", url, reqdata)
            resp = self.session.post(url, data=reqdata)
        try:
            # Try to deserialize the response
            data = resp.json()
        except (TypeError, ValueError):
            # Set the data to None if the JSON deserialization
            # failed.
            data = None
            logger.error("Could not deserialize JSON for request "
                         "to url=%s, response=%s", url, resp.text)
        else:
            # If the deserialization succeeded.
            if respschema:
                data = respschema.load(data).data

        # Return a response
        return ResponseClass(response=resp, status_code=resp.status_code,
                             data=data)

    def _params_to_camel(self, params):
        converted = {}
        for key, val in params.items():
            converted_key = to_camel(key)
            if isinstance(val, dict):
                converted[converted_key] = self._params_to_camel(val)
            else:
                converted[converted_key] = val
        return converted

    def __repr__(self):
        return u"<{0}: stage={1}, version={2}>".format(type(self).__name__,
                                                       self.stage,
                                                       self.version)


# TODO: Needs testing.
def to_snake(cc):
    """Convert a camel case string to snake case.

    :param cc: The string to convert.
    :return: A string in snake case.
    """
    n = []
    for x in cc:
        if x.isupper():
            n.append("_")
            x = x.lower()
        n.append(x)
    if n[0] == "_":
        n = n[1:]
    return "".join(n)


# TODO: Needs testing.
def to_camel(sc):
    """Convert a snake case string to camel case.

    :param sc: The string to convert.
    :return: A string in camel case.
    """
    n = []
    len_sc = len(sc)
    i = 0
    while i < len_sc:
        x = sc[i]
        if x == "_":
            i += 1
            if i < len_sc:
                n.append(sc[i].upper())
            else:
                break
        else:
            n.append(x)
        i += 1
    return "".join(n)
