# -*- coding: utf-8 -*-
"""
Helper functions and base classes.
"""

import json
import datetime
import logging
import os

from decimal import Decimal

import requests
from requests import Session

from .errors import SweetpayError, BadDataError, InvalidParameterError, \
    InternalServerError, UnderMaintenanceError, UnauthorizedError, \
    NotFoundError, TimeoutError, RequestError


class ResponseClass(object):
    """The response class returning response data from API calls."""

    def __init__(self, response, code, data, status):
        """Init the class.

        :param response: The requests response object.
        :param code: The HTTP status code.
        :param data: The JSON decoded data.
        :param status: The status from Paylevo.
        """
        super(ResponseClass, self).__init__()
        self.response = response
        self.code = code
        self.data = data
        self.status = status

    def __repr__(self):
        return u"<ResponseClass: code={0}, status={1}, " \
               u"response={2}, data=(...)>".format(self.code, self.status,
                                                   self.response)


class BaseResource(object):
    """The base resource."""
    CLIENT_CLS = None
    namespace = None

    api_token = None
    stage = None
    version = None
    timeout = None

    @classmethod
    def make_request(cls, cls_method, *args, **params):
        """Make request through the specified client's method.

        :param cls_method: The method from the client to use.
        :param api_token: An optional API token the caller can
                          specify to override the configured one.
        :param **params: The params to pass to the API endpoint.

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
        :return: A request object.
        """

        # TODO: Expand with stage and version?
        # The client to make the request with, pass in the API token.
        client = cls.get_client(params.pop("api_token", None))

        # Call the actual method. Note that this may raise an
        # AttributeErorr if the method doesn't exist, but we
        # let that bubble up. It may also raise a RequestError,
        # but as that is a subclass of SweetpayError we let that
        # bubble up as well.
        method_callable = getattr(client, cls_method)
        retval = method_callable(*args, **params)

        # Check if the response was successful. If so, just return the retval.
        if retval.code == 200:
            return retval

        # Set some shortcuts
        code = retval.code
        resp = retval.response
        status = retval.status
        data = retval.data

        # The standard kwargs to send to the exception when raised
        exc_kwargs = {
            "code": code, "response": resp, "status": status,
            "data": data
        }

        # Start checking for errors
        if code == 400:
            raise BadDataError(
                "The data passed to the server contained bad data. "
                "This most likely means that you missed to send some "
                "parameters, response data={0}".format(data), **exc_kwargs)
        elif code == 401:
            raise UnauthorizedError(
                "The passed API token was invalid", **exc_kwargs)
        elif code == 404:
            raise NotFoundError(
                "The resource you were looking for couldn't be found",
                **exc_kwargs)
        elif code == 422:
            raise InvalidParameterError(
                "You passed in an invalid parameter or missed a "
                "parameter, response data={0}".format(data), **exc_kwargs)
        elif code == 500:
            raise InternalServerError(
                "An internal server occurred", **exc_kwargs)
        elif code == 503:
            raise UnderMaintenanceError(
                "The server is currently under maintenance and can't "
                "be contacted", **exc_kwargs)
        else:
            # Something else happened, just throw a general error.
            raise SweetpayError(
                "Something went wrong in the request", **exc_kwargs)

    @classmethod
    def get_client(cls, api_token=None):
        """Return an instantiated client, based on the `CLIENT_CLS`.

        :param api_token: An optional api_token to override
                          the configured one.
        :return: An instantiated client.
        """
        if api_token is None:
            api_token = cls.api_token
        version = cls.version
        stage = cls.stage

        # Check if api_token and stage is set, if not, raise an error
        if api_token is None or stage is None:
            raise ValueError(
                "You must set an API token and decide whether to use "
                "the stage environment or not before using the "
                "SDK. Have a look at `sweetpay.configure`")

        # Get the version or nothing.
        try:
            version = version[cls.namespace]
        except KeyError:
            raise SweetpayError
        return cls.CLIENT_CLS(api_token, stage, version)


def configure(api_token, stage, version, timeout=None):
    """Configure the API with global variables.

    :param api_token: The API token provided by SweetPay.
    :param stage: A boolean indicating whether to use the stage
                  or production environment.
    :param version: A mapping/dict indicating which versions of
                    the APIs to use.
    :param timeout: The request timeout.
    :return: None
    """
    # We accomplish this by just setting some global variables
    # on the BaseResource
    BaseResource.api_token = api_token
    BaseResource.stage = stage
    BaseResource.version = version
    BaseResource.timeout = timeout


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

    def __init__(self, api_token, stage, version, timeout=None):
        """Initialize the checkout client used to talk to the checkout API.

        :param api_token: The authorization token to set in the
               Authorization header.
        :param stage: A boolean indicating if the stage server should
               be used or not. If set to False, the live server will be used.
        :param version: The version number of the API, defaults to 1.
        :param timeout: The request timeout. Defaults to 15 seconds.
        """
        self.stage = stage
        self.version = version
        self.api_token = api_token
        self.timeout = timeout or 15
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
        raise NotImplementedError(
            "No URL for the stage server has been specified")

    @property
    def production_url(self):
        """Return the production URL."""
        raise NotImplementedError(
            "No URL for the production server has been specified")

    @property
    def url(self):
        """Return the stage or production URL, depending on the settings."""
        if self.stage:
            url = self.stage_url
        else:
            url = self.production_url
        url = os.path.join(url, "v{0}".format(self.version))
        return url

    def build_url(self, *args):
        """Return a URL based on

        :param args: The arguments which will be used to build the path.
                For example: "path" and "to" creates the path "/path/to".
        :return: A complete URL as a string.
        """
        return os.path.join(self.url, *args)

    def make_request(self, url, method, params=None):
        """Make a request.

        :param params: The parameters to pass on to the marshmallow
                deserialization, and then pass on to the server.
        :param respschema: The schema to use for deserialization.
        :param params: The parameters passed by the client.
                       Should only be used when doing a POST request
        :param InvalidParameterError: T
        :raise TimeoutError: If a request timeout occurred.
        :raise RequestError: If an unhandled request error occurred.
        :return: Return a dictionary with the keys "response",
                "status_code", "data" and "raw_data".
        """

        logger = self.logger
        # We want the method to be in lower-case for easier handling.
        method = method.upper()

        # Set default values for the request args and kwargs.
        reqkwargs = {"timeout": self.timeout}

        # Handle the method types appropriately
        if method == "GET":
            logger.info("Sending request with method=GET to url=%s", url)
        elif method == "POST":
            if params:
                # Encode the data to JSON
                reqdata = SweetpayJSONEncoder().encode(params)
            else:
                # Use an empty body
                reqdata = ""
            logger.info(
                "Sending request with method=POST to url=%s and "
                "parameters=%s", url, reqdata)
            reqkwargs["data"] = reqdata
        else:
            raise ValueError(
                "Only GET and POST requests are allowed, not method=%s",
                method)

        # Send the actual response
        try:
            resp = self.session.request(method=method, url=url, **reqkwargs)
        except requests.Timeout as e:
            # If the request timed out.
            raise TimeoutError("The request timed out", code=None, status=None,
                               response=None, exc=e)
        except requests.RequestException as e:
            # If another request error occurred.
            raise RequestError(
                "Could not send a request to the server",
                code=None, status=None, response=None, exc=e)
        # Shortcut to status code
        logger.info(
            "With url=%s and method=%s, received "
            "status_code=%d and body=%s", resp.status_code, url, method,
            resp.text)

        try:
            # Try to decode the (hopefully) JSON response
            data = resp.json()
        except (TypeError, ValueError):
            logger.error(
                "Could not deserialize JSON for request "
                "to url=%s, response=%s", url, resp.text)
            data = None
            status = None
        else:

            # Now it's time to extract the status. If no status was
            # passed, an error will be raised as that shouldn't
            # be possible.
            try:
                status = data["status"]
            except KeyError:
                # No status was found
                status = None

        return ResponseClass(
            response=resp, code=resp.status_code, data=data, status=status)

    def __repr__(self):
        return u"<{0}: stage={1}, version={2}>".format(
            type(self).__name__, self.stage, self.version)
