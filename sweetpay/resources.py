from .constants import SUBSCRIPTION, CHECKOUT_SESSION, CREDITCHECK, OK_STATUS
from .errors import SweetpayError, BadDataError, InvalidParameterError, \
    InternalServerError, UnderMaintenanceError, UnauthorizedError, \
    NotFoundError, MethodNotAllowedError, FailureStatusError, ProxyError

from restbase import operation, BaseResource


class Resource(BaseResource):
    """The base resource used to create API resources."""
    namespace = None

    @classmethod
    def _check_for_errors(cls, code, data, response):
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


class SubscriptionV1(Resource):
    """The subscription resource."""

    namespace = SUBSCRIPTION

    _test_url = "https://api.stage.kriita.com/subscription/v1"
    _production_url = "https://api.kriita.com/subscription/v1"

    @operation
    def create(self, **params):
        """Create a subscription."""
        url = self._build_url("create")
        return self._api_call(url, "POST", params)

    @operation
    def query(self, subscription_id):
        """Query a subscription for information."""
        url = self._build_url(str(subscription_id), "query")
        return self._api_call(url, "GET")

    @operation
    def update(self, subscription_id, **params):
        """Update a subscription."""
        url = self._build_url(str(subscription_id), "update")
        return self._api_call(url, "POST", params)

    @operation
    def search(self, **params):
        """Search for subscriptions."""
        url = self._build_url("search")
        return self._api_call(url, "POST", params)

    @operation
    def list_log(self, subscription_id):
        """List all of the log entries."""
        url = self._build_url(str(subscription_id), "log")
        return self._api_call(url, "GET")

    @operation
    def regret(self, subscription_id):
        """Regret a subscription."""
        url = self._build_url(str(subscription_id), "regret")
        return self._api_call(url, "POST")


class CreditcheckV2(Resource):
    """The creditcheck resource."""

    namespace = CREDITCHECK

    _test_url = "https://api.stage.kriita.com/creditcheck/v2"
    _production_url = "https://api.kriita.com/creditcheck/v2"

    @operation
    def create(self, **params):
        url = self._build_url("check")
        return self._api_call(url, "POST", params)

    @operation
    def search(self, **params):
        url = self._build_url("search")
        return self._api_call(url, "POST", params)


class CheckoutSessionV1(Resource):
    """The checkout session resource."""

    namespace = CHECKOUT_SESSION

    _test_url = "https://checkout.stage.paylevo.com/v1"
    _production_url = "https://checkout.paylevo.com/v1"

    @operation
    def create(self, **params):
        """Create a checkout session"""
        url = self._build_url("session", "create")
        return self._api_call(url, "POST", params)
