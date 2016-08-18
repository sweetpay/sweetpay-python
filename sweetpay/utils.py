# -*- coding: utf-8 -*-

import json
import datetime
import logging
import os
from collections import namedtuple

from decimal import Decimal

import requests
from marshmallow import Schema
from requests import Session

from .errors import SweetpayError, BadDataError, InvalidParameterError, \
    InternalServerError, UnderMaintenanceError, UnauthorizedError, \
    NotFoundError, TimeoutError, RequestError

ResponseClass = namedtuple("ResponseClass",
                           ["response", "code", "data", "status"])


class BaseResource(object):
    """The base resource."""
    CLIENT_CLS = None
    api_token = None
    stage = None
    version = None
    timeout = None

    @classmethod
    def get_client(cls):
        if not cls.api_token or not cls.stage:
            raise ValueError("You must set an API token and decide whether "
                             "to use the stage environment or not before "
                             "using the SDK. Have a look at "
                             "`sweetpay.configure`")
        return cls.CLIENT_CLS(cls.api_token, cls.stage, cls.version)


def configure(api_token, stage, version=None, timeout=None):
    """Configure the API with global variables

    :param api_token: The API token provided by SweetPay.
    :param stage: A boolean indicating whether to use the stage
                  or production environment.
    :param version: An integer or string indicating which version
                    of the API to use. For example: 1
    :param timeout: The request timeout, defaults to
    :return: None
    """
    # We accomplish this by just setting some global variables
    # on the BaseResource
    BaseResource.api_token = api_token
    BaseResource.stage = stage
    BaseResource.version = version
    BaseResource.timeout = timeout


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

    def __init__(self, api_token, stage, version=None, timeout=None):
        """Initialize the checkout client used to talk to the checkout API.

        :param api_token: The authorization token to set in the
               Authorization header.
        :param stage: A boolean indicating if the stage server should
               be used or not. If set to False, the live server will be used.
        :param version: The version number of the API, defaults to 1.
        :param timeout: The request timeout. Defaults to 15 seconds.
        """
        self.stage = stage
        self.version = version or 1
        self.api_token = api_token
        self.timeout = timeout or 15

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
        :raise BadDataError: If the HTTP status code is 400
        :raise InvalidParameterError: If the HTTP status code is 422
        :raise InternalServerError: If an internal server error occurred
                                    at Sweetpay.
        :raise UnauthorizedError: If the API token was invalid.
        :raise NotFoundError: If the requested resource couldn't be found.
        :raise UnderMaintenanceError: If the server is currently
                                      under maintenance.
        :raise TimeoutError: If a request timeout occurred.
        :raise RequestError: If an unhandled request error occurred.
        :return: Return a dictionary with the keys "response",
                "status_code", "data" and "raw_data".
        """

        logger = self.logger

        # We want the method to be in lower-case for easier handling.
        method = method.lower()

        # Set default values for the request args and kwargs.
        reqargs = [url]
        reqkwargs = {"timeout": self.timeout}

        # Handle the method types appropriately
        if method == "get":
            logger.info("Sending request with method=GET to url=%s", url)
        elif method == "post":
            # TODO: Catch exception
            to_dump = reqschema().dump(params).data
            # Encode the data to JSON
            reqdata = SweetpayJSONEncoder().encode(to_dump)
            # Log the progress
            logger.info("Sending request with method=POST to url=%s and "
                        "parameters=%s", url, reqdata)
            # Set data as a kwarg to the request function
            reqkwargs["data"] = reqdata
        else:
            raise ValueError("Only GET and POST requests are allowed, "
                             "not method=%s", method)

        # Send the actual response
        response_func = getattr(self.session, method)
        try:
            resp = response_func(*reqargs, **reqkwargs)
        except requests.Timeout as e:
            # If the request timed out.
            raise TimeoutError("The request timed out", code=None, status=None,
                               respone=None, exc=e)
        except requests.RequestException as e:
            # If another request error occurred.
            raise RequestError("Could not send a request to the server",
                               code=None, status=None, response=None,
                               exc=e)
        # Shortcut to status code
        code = resp.status_code
        logger.info("With url=%s and method=%s, received status_code=%d "
                    "and body=%s", resp.status_code, url, method, resp.text)

        try:
            # Try to decode the (hopefully) JSON response
            data = resp.json()
        except (TypeError, ValueError):
            logger.error("Could not deserialize JSON for request "
                         "to url=%s, response=%s", url, resp.text)
            data = None
            status = None
        else:
            # TODO: Remove hack
            # We do this because the API sometimes return a string
            # as the data, and a string obviously can't have a status.
            if isinstance(data, dict):
                # Let's deserialize the data to Python objects.
                data = respschema.load(data).data

                # Now it's time to extract the status. If no status was
                # passed, an error will be raised as that shouldn't
                # be possible.
                try:
                    status = data["status"]
                except KeyError:
                    # We throw a general error here as this isn't
                    # supposed to happen.
                    raise SweetpayError("No status was passed from Sweetpay, "
                                        "even though the JSON was valid. This "
                                        "is most likely an error "
                                        "in Sweetpay's API", code=code,
                                        status=None, data=data, response=resp)
            else:
                status = None

        # Check if the response was successful.
        if code == 200:
            # Return a response class
            return ResponseClass(response=resp, code=resp.status_code,
                                 data=data, status=status)

        # The standard kwargs to send to the exception when raised
        exc_kwargs = {"code": code, "response": resp, "status": status,
                      "data": data}
        # Bad Data
        if code == 400:
            raise BadDataError("The data passed to the server "
                               "contained bad data. This most likely means "
                               "that you missed to send some parameters, "
                               "response data={0}".format(data),
                               **exc_kwargs)
        # Unauthorized
        elif code == 401:
            raise UnauthorizedError("The passed API token was invalid",
                                    **exc_kwargs)
        # Not Found
        elif code == 404:
            raise NotFoundError("The resource you were looking for couldn't "
                                "be found", **exc_kwargs)
        # Unprocessable Entity
        elif code == 422:
            raise InvalidParameterError("You passed in an invalid "
                                        "parameter or missed a parameter"
                                        "parameter, response data={0}".format(data),
                                        **exc_kwargs)
        # Internal Server Error
        elif code == 500:
            raise InternalServerError("An internal server occurred",
                                      **exc_kwargs)
        # Under Maintenance
        elif code == 503:
            raise UnderMaintenanceError("The server is currently under"
                                        "maintenance and can't be contacted",
                                        **exc_kwargs)
        # Something else happened, just throw a general error.
        else:
            raise SweetpayError("Something went wrong in the request",
                                **exc_kwargs)

    def __repr__(self):
        return u"<{0}: stage={1}, version={2}>".format(type(self).__name__,
                                                       self.stage,
                                                       self.version)
