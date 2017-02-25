class SweetpayError(Exception):
    """The base Sweetpay exception. Raised for ambiguous scenarios,
    when no other exception type fits.
    """

    # The JSON decoded data from the server. None if the JSON
    # couldn't be decoded.
    data = None

    # The requests response object returned from the server.
    # None if the request failed.
    response = None

    # The HTTP status code as an integer. None if the request failed.
    code = None

    # The status extracted from the payload. None if the JSON
    # couldn't be decoded or if no status for some reason wasn't
    # returned from the server.
    status = None

    # This is a link to the requests exception that triggered
    # this error. Check this attribute if you want to see what kind
    # of request error occurred (e.g. a timeout).
    exc = None

    def __init__(self, msg=None, data=None, response=None, code=None,
                 status=None, exc=None):
        super(SweetpayError, self).__init__(self, msg)
        self.data = data
        self.response = response
        self.code = code
        self.status = status
        self.exc = exc

    @property
    def request_sent(self):
        """Return a boolean to indicate if a request was sent to the server.

        This will for example be False in the case of timeouts."""
        return self.response is not None

    @property
    def is_json(self):
        """Return a boolean to indicate if the resp data is JSON."""
        return self.data is not None


class FailureStatusError(SweetpayError):
    """Raised when the status from the server isn't OK.

    When this status is returned, it means that the
    request did not succeed with the intended operation.
    """


class ProxyError(SweetpayError):
    """When a proxy error occurs, i.e. we get a HTTP status code of 502."""


class BadDataError(SweetpayError):
    """If bad data was passed to the server"""


class InvalidParameterError(SweetpayError):
    """If bad data was passed to the server"""


class InternalServerError(SweetpayError):
    """Raised if an internal server error occurred."""


class UnauthorizedError(SweetpayError):
    """Raised if you configured an invalid API token or are forbidden to
    access an API.
    """


class NotFoundError(SweetpayError):
    """Raised if the resource you were looking for couldn't be found.

    Will also be raised when the API can't find an API endpoint.
    """


class MethodNotAllowedError(SweetpayError):
    """Raised when a method such as POST is not allowed for an API endpoint."""


class UnderMaintenanceError(SweetpayError):
    """Raised if the server is under maintenance"""


class RequestError(SweetpayError):
    """The base exception to bubble `requests.RequestException`"""


class TimeoutError(RequestError):
    """Raised when a timeout occurs"""
