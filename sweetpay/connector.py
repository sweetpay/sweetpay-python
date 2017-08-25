"""All base classes are defined in this file."""
import json
import datetime
from decimal import Decimal
import requests
from restbase import BaseConnector

from .utils import logger
from .errors import TimeoutError, RequestError
from .constants import DATE_FORMAT


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
        return super().default(obj)


class Connector(BaseConnector):
    """The base class used to create API clients."""

    def __init__(self, api_token, *args, **kwargs):
        """Initialize the checkout client used to talk to the checkout API.

        :param api_token: Same as `SweetpayClient`.
        :param args: The arguments to pass to BaseConnector.
        :param kwargs: The keyword arguments to pass to BaseConnector.
        """
        self.api_token = api_token
        super().__init__(*args, **kwargs)

    def create_headers(self):
        """Return headers to use in each request."""
        return {
            "Authorization": self.api_token, "Content-Type": "application/json",
            "Accept": "application/json", "User-Agent": "Python-SDK"
        }

    def send_request(self, method, url, reqkwargs):
        """Send a request to the server.

        :param method: The HTTP method to use.
        :param url: The URL to send the request to.
        :param reqkwargs: The keyword arguments to pass to the
            request function.
        """

        # We need to create the session on every request to
        # keep the library thread-safe.
        session = self.create_session()
        try:
            # Send the actual request
            resp = session.request(method=method, url=url, **reqkwargs)
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

    def get_json_encoder(self):
        """Return an instance of the encoder to use for encoding request data.

        This method may be overwritten to provide your own encoder.
        """
        return SweetpayJSONEncoder()
