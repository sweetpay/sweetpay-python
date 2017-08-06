"""All base classes are defined in this file."""
import os
import json
import datetime
from contextlib import contextmanager
from decimal import Decimal

import requests

from unittest.mock import Mock
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from .utils import logger
from .errors import SweetpayError, BadDataError, InvalidParameterError, \
    InternalServerError, UnderMaintenanceError, UnauthorizedError, \
    NotFoundError, TimeoutError, RequestError, MethodNotAllowedError, \
    FailureStatusError, ProxyError
from .constants import DATE_FORMAT, OK_STATUS


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
        return super(SweetpayJSONEncoder, self).default(obj)


class ResponseClass:
    """The response class returning response data from API calls."""

    def __init__(self, response, code, data):
        """Init the class.

        :param response: The requests response object.
        :param code: The HTTP status code.
        :param data: The JSON decoded data.
        """
        self.response = response
        self.code = code
        self.data = data

    def __repr__(self):
        return (
            "<ResponseClass: code={0}, response={1}, data={2}>".format(
                self.code, self.response, self.data))


class SweetpayConnector:
    """The base class used to create API clients."""

    def __init__(self, api_token, stage, timeout, max_retries=None):
        """Initialize the checkout client used to talk to the checkout API.

        :param api_token: Same as `SweetpayClient`.
        :param stage: Same as `SweetpayClient`.
        :param timeout: Same as `SweetpayClient`.
        :param headers: Optional. A dictionary of headers to update the
                        session headers with.
        :param max_retries: Optional. Set the amount of max retries of
                            requests to the API. Defaults to no retries.
        """
        self.api_token = api_token
        self.stage = stage
        self.timeout = timeout
        self.logger = logger
        self.session = Session()

        # Configure max retries if passed
        if max_retries:
            retries = Retry(total=max_retries)
            adapter = HTTPAdapter(max_retries=retries)
            self.session.mount("https://", adapter)

        self.session.headers = self.create_headers()

    def create_headers(self):
        """Return headers to use in each request."""
        return {
            "Authorization": self.api_token, "Content-Type": "application/json",
            "Accept": "application/json", "User-Agent": "Python-SDK"
        }

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

        # We want the method to be in upper-case for comparison reasons.
        method = method.upper()

        # Set default values for the request args and kwargs.
        reqkwargs = {"timeout": self.timeout}

        # Encode the data
        reqkwargs["data"] = self.encode_data(method, params)

        # Pre process the request data.
        reqkwargs = self.pre_process_request(method, url, reqkwargs)

        # Send the actual request
        self.logger.info(
            "Sending request with method=%s to url=%s", method, url)
        resp = self.send_request(method, url, reqkwargs)

        # Try to decode the response
        data = self.decode_data(resp.text)

        # Post process the request.
        respcls = ResponseClass(resp, resp.status_code, data)
        respcls = self.post_process_request(respcls)
        return respcls

    def send_request(self, method, url, reqkwargs):
        """Send a request to the server.

        :param method: The HTTP method to use.
        :param url: The URL to send the request to.
        :param reqkwargs: The keyword arguments to pass to the
            request function.
        """
        try:
            # Send the actual request
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
        logger.info(
            "Sent request to url=%s and method=%s, "
            "received status_code=%d", url, method, resp.status_code)
        return resp

    def encode_data(self, method, params):
        """Encode the request data.

        :param method: The HTTP method.
        :param params: The data to encode, if any.
        """
        if method == "GET":
            return None
        elif method == "POST":
            if params:
                # Encode the data to JSON
                data = self.get_json_encoder().encode(params)
            else:
                # Use an empty body
                data = {}
            return data
        else:
            raise ValueError(
                "Only GET and POST requests are allowed, not "
                "method=%s".format(method))

    def decode_data(self, rawdata):
        """Decode the response returned from the server.

        This would be the place to decode JSON.

        :param rawdata: The raw data to decode.
        :return: The response data.
        """
        try:
            return json.loads(rawdata)
        except (TypeError, ValueError):
            logger.error("Could not deserialize JSON data=%s", rawdata)
            return rawdata

    def pre_process_request(self, method, url, reqkwargs):
        """Pre process the request.

        :param method: The method used. Can not be modified.
        :param url: The URL to send the request to. Can not be modified.
        :param reqkwargs: The keyword arguments to send to the
            underlying `requests` call. `data` will be present, but
            it's value and type may not be assumed.
        :return: The reqkwargs to give to the underyling `requests` call.
        """
        return reqkwargs

    def post_process_request(self, respcls):
        """Process the ResponseClass directly after the request was made.

        If you override this method, it is recommended that you call
        super() first and then do your own post processing..

        :param respcls: The ResponseClass to post process.
        :return: The data returned from the server.
        """
        # Now it's time to extract the status.
        return respcls

    def get_json_encoder(self):
        """Return an instance of the encoder to use for encoding request data.

        This method may be overwritten to provide your own encoder.
        """
        return SweetpayJSONEncoder()

    def __repr__(self):
        return "<{0}: stage={1}>".format(type(self).__name__, self.stage)


class BaseResource(object):
    """The base resource used to create API resources."""
    namespace = None

    def __init__(self, stage, connector, *connector_args, **connector_kwargs):
        self.stage = stage
        self.client = connector(
            *connector_args, stage=stage, **connector_kwargs)

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

    def api_call(self, url, method, **params):
        """Make an API call.

        If an exception isn't raised, the operation was successful.

        :param method: The method on the client to use.
        :param params: The params to pass to the client method.
        :return: A `ResponseClass` instance.
        """

        # Make the actual API call.
        respcls = self.client.make_request(url, method, params)

        # The last thing we do is to check for errors. If an error
        # was found, raise an exception. If no error was found, a
        # dictionary of the response data will be returned.
        return self.check_for_errors(
            code=respcls.code, data=respcls.data, response=respcls.response)

    @classmethod
    def check_for_errors(cls, code, data, response):
        """Inspect a response for errors.

        This method must raise relevant exceptions or return some
        sort of data to the user. The default implementation is
        to raise exceptions based on the code/status, or return
        the ResponseClass if all is well.

        :param code: The HTTP code returned from the server.
        :param data: The data returned from the server.
        :param response: The actual response returned from the server.
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
        :raise SweetpayError: If no other handler was found.
        :return: A dictionary representing the data from the server.
        """

        # The standard kwargs to send to the exception when raised
        exc_kwargs = {
            "code": code, "response": response, "data": data
        }

        # Hacky workaround to get a status
        try:
            status = data["status"]
        except (KeyError, TypeError):
            status = None
        exc_kwargs["status"] = status

        # Check if the response was successful.
        if code == 200:
            # If all OK, return the JSON data.
            if status == OK_STATUS:
                return data
            exc = FailureStatusError
            msg = (
                "The passed status={0} is not the OK_STATUS={1}, "
                "meaning that the requested operation did not "
                "succeed".format(status, OK_STATUS))
        else:
            # Start checking for errors
            if code == 400:
                exc = BadDataError
                msg = (
                    "The data passed to the server contained bad data. "
                    "This most likely means that you missed to send some "
                    "parameters")
            elif code == 401:
                exc = UnauthorizedError
                msg = "The passed API token was invalid"
            elif code == 404:
                exc = NotFoundError
                msg = "The resource you were looking for couldn't be found"
            elif code == 405:
                # We usually shouldn't get here unless there is something
                # wrong with the API client
                exc = MethodNotAllowedError
                msg = "The specified method is not allowed on this endpoint"
            elif code == 422:
                exc = InvalidParameterError
                msg = (
                    "You passed in an invalid parameter or missed a "
                    "parameter".format(data))
            elif code == 500:
                exc = InternalServerError
                msg = "An internal server occurred"
            elif code == 502:
                exc = ProxyError
                msg = (
                    "A proxy error occurred. Note that if you tried to create "
                    "a new resource, it is possible that it was created, "
                    "even though this error occurred")
            elif code == 503:
                exc = UnderMaintenanceError
                msg = (
                    "The server is currently under maintenance and can't "
                    "be contacted")
            else:
                # Something else happened, just throw a general error.
                exc = SweetpayError
                msg = "Something went wrong in the request"
        # Raise the actual exception. We do this at the end because
        # we want to be completely sure that the exc_kwargs are
        # actually passed in.
        raise exc(msg, **exc_kwargs)

    def __repr__(self):
        return "<{0}: namespace={1}>".format(
            type(self).__name__, self.namespace)


def mock_manager(func):
    """Wrapper that returns a contextmanager for mocking API calls."""
    # The mock which gets set when in mocking mode.
    func._mock = None

    @contextmanager
    def manager(*args, **kwargs):
        # Setup context: Set the mock when the this context is invoked.
        func._mock = Mock(*args, **kwargs)

        # Return the mock for the context
        yield func._mock

        # Teardown context: Remove the mock
        func._mock = None

    return manager


def operation(func):
    """Decorator that should be set for all API operations."""
    def inner(self, *args, **kwargs):
        # Call the mock if we are in mock mode.
        if func._mock:
            # We do not include self in the call, since that will
            # make the mock's assert helpers act crazy.
            return func._mock(*args, **kwargs)
        # If we are not mocking, call the actual underlying function.
        return func(self, *args, **kwargs)

    # Create a mock manager.
    inner.mock = mock_manager(func)

    # We set this shortcut to the function to simplify testing.
    inner._func = func
    return inner
