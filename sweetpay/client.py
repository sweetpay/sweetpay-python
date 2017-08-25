from restbase import BaseClient

from sweetpay import CheckoutSessionV1, CreditcheckV2, SubscriptionV1, Connector


class Client(BaseClient):
    """The developer-interface for the API.

    Create an instance of this class to gain access to the SDK."""

    RESOURCE_MAPPER = {
        (SubscriptionV1.namespace, 1): SubscriptionV1,
        (CreditcheckV2.namespace, 2): CreditcheckV2,
        (CheckoutSessionV1.namespace, 1): CheckoutSessionV1
    }

    DEFAULT_CONNECTOR = Connector
    DEFAULT_TIMEOUT = 15

    def __init__(self, api_token, *args, **kwargs):
        """Configure the API with default values.

        :param api_token: The API token provided by SweetPay.
        :param args: Passed to restbase.BaseClient.
        :param kwargs: Passed to restbase.BaseClient.
        """
        self.api_token = api_token
        super().__init__(*args, **kwargs)

    def _get_resource_arguments(self):
        kwargs = super()._get_resource_arguments()
        kwargs.update({"api_token": self.api_token})
        return kwargs
