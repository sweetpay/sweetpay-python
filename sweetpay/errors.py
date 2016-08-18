# -*- coding: utf-8 -*-


class SweetpayError(Exception):
    def __init__(self, msg, data, response, code, status):
        SweetpayError.__init__(self, msg)
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


class InvalidJSONError(SweetpayError):
    pass
