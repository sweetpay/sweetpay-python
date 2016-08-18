# -*- coding: utf-8 -*-


class SweetpayError(Exception):

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

    def __init__(self, msg, data, response, code, status):
        Exception.__init__(self, msg)
        self.data = data
        self.response = response
        self.code = code
        self.status = status


class BadDataError(SweetpayError):
    pass


class InvalidParameterError(SweetpayError):
    pass


class InternalServerError(SweetpayError):
    pass


class UnauthorizedError(SweetpayError):
    pass


class NotFoundError(SweetpayError):
    pass


class UnderMaintenanceError(SweetpayError):
    pass


class RequestError(SweetpayError):

    # This is a link to the requests exception that triggered
    # this error. Check this attribute if you want to see what kind
    # of request error occurred (e.g. a timeout).
    exc = None

    def __init__(self, *args, exc=None, **kwargs):
        SweetpayError.__init__(self, *args, **kwargs)
        self.exc = exc


class TimeoutError(RequestError):
    pass
