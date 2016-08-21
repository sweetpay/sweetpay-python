# -*- coding: utf-8 -*-


class SweetpayError(Exception):
    """The base Sweetpay exception."""

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

    def __init__(self, msg, data=None, response=None, code=None,
                 status=None, exc=None):
        super(SweetpayError, self).__init__(self, msg)
        self.data = data
        self.response = response
        self.code = code
        self.status = status
        self.exc = exc


class BadDataError(SweetpayError):
    """If bad data was passed to the server"""


class InvalidParameterError(SweetpayError):
    pass


class InternalServerError(SweetpayError):
    """Raised if an internal server error occurred."""


class UnauthorizedError(SweetpayError):
    """Raised if you configured an invalid API token or are forbidden to
    access an API"""


class NotFoundError(SweetpayError):
    """Raised if the resource you were looking for couldn't be found."""


class UnderMaintenanceError(SweetpayError):
    """Raised if the server is under maintenance"""


class RequestError(SweetpayError):
    """The base exception to bubble requests.RequestException"""


class TimeoutError(RequestError):
    """Raised when a timeout occurs"""


# This is cast instead of TypeError because we want to include the
# data from marshmallow.
class InvalidArgumentError(SweetpayError):
    """An invalid parameter was passed."""
