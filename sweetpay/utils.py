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


class BaseSchema(Schema):
    # NOTE: This is a hack to include all passed fields
    @post_dump(pass_original=True)
    def include_all_fields(self, data, original_data):
        for key, val in original_data.items():
            if key not in self.fields:
                data[key] = val


class SweetpayJSONEncoder(json.JSONEncoder):
    """A custom JSON encoder to support datetime, date and timedelta."""
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        else:
            return super(SweetpayJSONEncoder, self).default(obj)


class BaseClient(object):
    """The super class used to create API clients."""

    def __init__(self, auth_token, stage, version=1):
        """Initialize the checkout client used to talk to the checkout API.

        :param auth_token: The authorization token to set in the
               Authorization header.
        :param stage: A boolean indicating if the stage server should
               be used or not. If set to False, the live server will be used.
        :param version: The version number of the API, defaults to 1.
        """
        self.stage = stage
        self.version = version
        self.auth_token = auth_token

        # Setup the logger
        self.logger = logging.getLogger("sweetpay-sdk")

        # The session
        self.session = Session()
        self.session.headers.update({
            "Authorization": auth_token, "Content-Type": "application/json",
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

    def make_request(self, url, method, respschema=None, reqschema=None,
                     params=None):
        """Make a request.

        :param params: The parameters to pass on to the marshmallow
                deserialization, and then pass on to the server.
        :param respschema: The schema to use for deserialization.
        :param reqschema:
        :param params:
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
            if reqschema:
                # Create the request parameters. May raise
                # a marshmallow.ValidationError
                dump_obj = reqschema(strict=True).dump(params)
                # Encode the request parameters to JSON.
                reqdata = SweetpayJSONEncoder().encode(dump_obj.data)
            else:
                # If no schema was passed, set the parameters.
                reqdata = params

            self.logger.info("Sending request with method=POST to url=%s and "
                             "parameters=%s", url, reqdata)
            resp = self.session.post(url, data=reqdata)

        try:
            # Try to deserialize the response
            data = resp.json()
        except (TypeError, ValueError):
            # Set the data to None if the JSON deserialization
            # failed.
            data = None
            logger.debug("Could not deserialize JSON for request to url=%s, "
                         "response=%s", url, resp.text)
        else:
            # If the deserialization succeeded.
            if respschema:
                data = respschema.load(data).data

        # Return a response
        return ResponseClass(response=resp, status_code=resp.status_code,
                             data=data)

    def __repr__(self):
        return u"<{0}: stage={1}, version={2}>".format(type(self).__name__,
                                                       self.stage,
                                                       self.version)
