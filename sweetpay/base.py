"""All base classes are defined in this file."""
import logging
import os
import json
import datetime
from contextlib import contextmanager
from decimal import Decimal
from itertools import chain

import requests
from collections import defaultdict
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3 import Retry

from .utils import setindict, getfromdict, decode_datetime
from .errors import SweetpayError, BadDataError, InvalidParameterError, \
    InternalServerError, UnderMaintenanceError, UnauthorizedError, \
    NotFoundError, TimeoutError, RequestError, MethodNotAllowedError, \
    FailureStatusError, ProxyError
from .constants import DATE_FORMAT, LOGGER_NAME, OK_STATUS


class SweetpayJSONEncoder(json.JSONEncoder):
    """A custom JSON encoder to support custom types."""
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.strftime(DATE_FORMAT)
        elif isinstance(obj, Decimal):
            # String, as we want it money safe.
            return str(obj)
        else:
            return super(SweetpayJSONEncoder, self).default(obj)


class ResponseClass:
    """The response class returning response data from API calls."""

    def __init__(self, response, code, data, status):
        """Init the class.

        :param response: The requests response object.
        :param code: The HTTP status code.
        :param data: The JSON decoded data.
        :param status: The status from Paylevo.
        """
        super().__init__()
        self.response = response
        self.code = code
        self.data = data
        self.status = status

    @property
    def status_ok(self):
        return self.status == OK_STATUS

    def __repr__(self):
        return (
            "<ResponseClass: code={0}, status={1}, "
            "response={2}, data=(...)>".format(
                self.code, self.status, self.response))


class SweetpayConnector:
    """The base class used to create API clients."""

    def __init__(self, api_token, stage, version, timeout, headers=None,
                 max_retries=None):
        """Initialize the checkout client used to talk to the checkout API.

        :param api_token: Same as `SweetpayClient`.
        :param stage: Same as `SweetpayClient`.
        :param version: Same as `SweetpayClient`.
        :param timeout: Same as `SweetpayClient`.
        :param headers: Optional. A dictionary of headers to update the
                        session headers with.
        :param max_retries: Optional. Set the amount of max retries of
                            requests to the API. Defaults to no retries.
        """
        self.api_token = api_token
        self.stage = stage
        self.version = version
        self.timeout = timeout
        self.logger = logging.getLogger(LOGGER_NAME)

        self.session = Session()
        self.session.headers.update({
            "Authorization": api_token, "Content-Type": "application/json",
            "Accept": "application/json", "User-Agent": "Python-SDK"
        })
        self.session.headers.update(headers or {})

        # Configure max retries if passed
        if max_retries:
            retries = Retry(total=max_retries)
            adapter = HTTPAdapter(max_retries=retries)
            self.session.mount("https://", adapter)

    def make_request(self, url, method, params=None):
        """Make a request to a passed URL.

        :param url: The URL to send the request to.
        :param method: The method to use. Should be GET or POST.
        :param params: The parameters passed by the client.
                       Should only be used when doing a POST request
        :raise ValueError: If an incorrect `method` is passed.
        :raise TimeoutError: If a request timeout occurred.
        :raise RequestError: If an unhandled request error occurred.
        :return: Return a `ResponseClass` instance.
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
                reqdata = {}
            logger.info(
                "Sending request with method=POST to url=%s and "
                "parameters=%s", url, reqdata)
            reqkwargs["data"] = reqdata
        else:
            raise ValueError(
                "Only GET and POST requests are allowed, not method=%s", method)

        try:
            # Send the actual response
            resp = self.session.request(method=method, url=url, **reqkwargs)
        except requests.Timeout as e:
            # If the request timed out.
            raise TimeoutError(
                "The request timed out", code=None, status=None,
                response=None, exc=e)
        except requests.RequestException as e:
            # If another request error occurred.
            raise RequestError(
                "Could not send a request to the server, inspect "
                "the `exc` attribute to see the underlying "
                "`requests` exception", code=None, status=None,
                response=None, exc=e)
        else:
            logger.info(
                "Sent request to url=%s and method=%s, received "
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

        return ResponseClass(
            response=resp, code=resp.status_code, data=data, status=None)

    def __repr__(self):
        return "<{0}: stage={1}, version={2}>".format(
            type(self).__name__, self.stage, self.version)


class BaseResource(object):
    """The base resource used to create API resources."""
    namespace = None

    # The validators.
    _validators = defaultdict(list)

    def __init__(
            self, use_validators, stage, *connector_args, **connector_kwargs):
        self.client = SweetpayConnector(
            *connector_args, stage=stage, **connector_kwargs)
        self.stage = stage
        self.mockdata = None
        self.mockexc = None
        self.use_validators = use_validators

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
        """Return the stage or production URL, based on the current context."""
        if self.stage:
            url = self.stage_url
        else:
            url = self.production_url
        return url

    def build_url(self, *args):
        """Return a URL based on the `url` and a provided path.

        :param args: The arguments which will be used to build the path.
                For example: "path" and "to" creates the path "/path/to".
        :return: A complete URL as a string.
        """
        return os.path.join(self.url, *args)

    def make_request(self, url, method, **params):
        """Make a request through the specified client's method.

        If an exception isn't raised, the operation was successful.

        :param method: The method on the client to use.
        :param params: The params to pass to the client method.
        :return: A `ResponseClass` instance.
        """

        # Check if we are in mocking mode or not.
        if self.is_mocked:
            if self.mockexc:
                raise self.mockexc
            else:
                respcls = ResponseClass(**self.mockdata)
        else:
            # Call the actual method. Note that this may raise an
            # AttributeError if the method doesn't exist, but we
            # let that bubble up. It may also raise a RequestError,
            # but as that is a subclass of SweetpayError we let that
            # bubble up as well.
            respcls = self.client.make_request(url, method, params)

            # Post process the request.
            respcls = self.post_request(respcls)

        # If data is existent, we assume data is a dict, and try
        # to validate all fields.
        if respcls.data and self.use_validators:
            respcls.data = self.validate_data(respcls.data)
        return self.check_for_errors(respcls)

    def post_request(self, resp):
        if isinstance(resp.data, str):
            # Sometimes a string is returned, which passes the JSON
            # validation for whatever reason. If that happens,
            # we set the status to that string as a hacky workaround.
            status = resp.data
            resp.data = None
        else:
            # Now it's time to extract the status. If no status was passed,
            # we just set the status to None.
            try:
                status = resp.data["status"]
            except (KeyError, TypeError):
                # No status was found
                status = None

        resp.status = status
        return resp

    @classmethod
    def clear_validators(cls):
        cls._validators = defaultdict(list)

    @classmethod
    def check_for_errors(cls, respcls):
        """Inspect a response for errors.

        This method must raise relevant exceptions or return some
        sort of data to the user. The default implementation is
        to raise exceptions based on the code/status, or return
        the ResponseClass if all is well.

        :param respcls: An instance of a ResponseClass.
        :raise BadDataError: If the HTTP status code is 400.
        :raise InvalidParameterError: If the HTTP status code is 422.
        :raise InternalServerError: If an internal server error occurred
                                    at Sweetpay.
        :raise UnauthorizedError: If the API token was invalid.
        :raise NotFoundError: If the requested resource couldn't be found.
        :raise UnderMaintenanceError: If the server is currently
                                      under maintenance.
        :raise FailureStatusError: If the status isn't OK.
        :raise ProxyError: If a proxy error occurred.
        :raise TimeoutError: If a request timeout occurred.
        :raise RequestError: If an unhandled request error occurred.
        :return: A `ResponseClass` instance.
        """
        # Set some shortcuts
        code = respcls.code
        status = respcls.status
        data = respcls.data

        # The standard kwargs to send to the exception when raised
        exc_kwargs = {
            "code": code, "response": respcls.response, "status": status,
            "data": data
        }

        # Check if the response was successful.
        if code == 200:
            if respcls.status_ok:
                # If all OK, return the response.
                return respcls
            else:
                raise FailureStatusError(
                    "The passed status={0} is not the OK_STATUS={1}, "
                    "meaning that the requested operation did not "
                    "succeed".format(status, OK_STATUS), **exc_kwargs)

        # TODO: Is this really how we should do it?
        # Hacky workaround set the status from the error.
        if status is None and hasattr(data, "get"):
            status = data.get("error", None)
            exc_kwargs["status"] = status

        # Start checking for errors
        if code == 400:
            raise BadDataError(
                "The data passed to the server contained bad data. "
                "This most likely means that you missed to send some "
                "parameters, response data={0}, "
                "status={1}".format(data, status), **exc_kwargs)
        elif code == 401:
            raise UnauthorizedError(
                "The passed API token was invalid", **exc_kwargs)
        elif code == 404:
            raise NotFoundError(
                "The resource you were looking for couldn't be found",
                **exc_kwargs)
        elif code == 405:
            # We usually shouldn't get here unless there is something
            # wrong with the API client
            raise MethodNotAllowedError(
                "The specified method is not allowed on this endpoint",
                **exc_kwargs)
        elif code == 422:
            raise InvalidParameterError(
                "You passed in an invalid parameter or missed a "
                "parameter, response data={0}".format(data), **exc_kwargs)
        elif code == 500:
            raise InternalServerError(
                "An internal server occurred", **exc_kwargs)
        elif code == 502:
            raise ProxyError(
                "A proxy error occurred. Note that if you tried to create "
                "a new resource, it is possible that it was created, "
                "even though this error occurred.", **exc_kwargs)
        elif code == 503:
            raise UnderMaintenanceError(
                "The server is currently under maintenance and can't "
                "be contacted", **exc_kwargs)
        else:
            # Something else happened, just throw a general error.
            raise SweetpayError(
                "Something went wrong in the request", **exc_kwargs)

    @classmethod
    def validate_data(cls, data):
        """Validate data response data from the server.

        This function assumed that data is a valid response
        from the server.
        """
        # Iterate through both the current iterators, and the
        # base resources iterator. Note that we assume that
        # the BaseResource is always subclassed here.
        # We can ignore keyerrors as _validators is a defaultdict(list).
        validators = chain(cls._validators[cls], cls._validators[BaseResource])
        for processor in validators:
            path = processor._dictpath
            try:
                value = getfromdict(data, path)
            except (KeyError, TypeError):
                # If no value found, we screw it and continue.
                # A KeyError and TypeError are possible, depending
                # on the structure of the response
                continue
            else:
                # Validate the field and set the new value
                validatesled = processor(value)
                # If path is empty, we will just set a new
                # data variable.
                if not path:
                    data = validatesled
                else:
                    setindict(data, path, validatesled)
        return data

    @classmethod
    def validates(cls, *args):
        """A decorator function used to validates response data.

        :param args: The path (as a list of strings and/or integers)
                     to the value to validates.
        """
        def outer(func):
            # Set the validator on the class
            func._dictpath = args
            cls._validators[cls].append(func)
            def inner(*args, **kwargs):
                # Call the decorated function
                return func(*args, **kwargs)
            return inner
        return outer

    @property
    def is_mocked(self):
        """Return a value to indicate whether the resource is mocked or not."""
        return self.mockexc is not None or self.mockdata is not None

    @contextmanager
    def mock_resource(self, raises=None, code=None, data=None, response=None,
                      status=None):
        """Mock all of the resource's operations.

        This is meant to be used for testing.
        """
        self.mockexc = raises
        self.mockdata = {
            "code": code, "data": data, "response": response, "status": status
        }
        yield
        self.mockdata = None
        self.mockexc = None

    def __repr__(self):
        return "<{0}: namespace={1}>".format(
            type(self).__name__, self.namespace)


def _operation(func):
    """Mark a method or function as an operation."""
    # TODO: Set mock function
    # TODO: Set validator?
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    raise NotImplementedError
