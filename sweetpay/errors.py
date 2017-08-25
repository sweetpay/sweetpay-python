from restbase.base import RESTBaseException


class SweetpayError(RESTBaseException):
    """The base Sweetpay exception. Raised for ambiguous scenarios,
    when no other exception type fits.
    """

    def __init__(self, *args, status=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = status


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
