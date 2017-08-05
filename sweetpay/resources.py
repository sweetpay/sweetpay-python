from .constants import SUBSCRIPTION, CHECKOUT_SESSION, CREDITCHECK
from .base import BaseResource, operation


class SubscriptionV1(BaseResource):
    """The subscription resource."""

    namespace = SUBSCRIPTION

    @property
    def stage_url(self):
        """Return the stage URL."""
        return "https://api.stage.kriita.com/subscription/v1"

    @property
    def production_url(self):
        """Return the production URL."""
        return "https://api.kriita.com/subscription/v1"

    @operation
    def create(self, **params):
        """Create a subscription."""
        url = self.build_url("create")
        return self.api_call(url, "POST", **params)

    @operation
    def query(self, subscription_id):
        """Query a subscription for information."""
        url = self.build_url(str(subscription_id), "query")
        return self.api_call(url, "GET")

    @operation
    def update(self, subscription_id, **params):
        """Update a subscription."""
        url = self.build_url(str(subscription_id), "update")
        return self.api_call(url, "POST", **params)

    @operation
    def search(self, **params):
        """Search for subscriptions."""
        url = self.build_url("search")
        return self.api_call(url, "POST", **params)

    @operation
    def list_log(self, subscription_id):
        """List all of the log entries."""
        url = self.build_url(str(subscription_id), "log")
        return self.api_call(url, "GET")

    @operation
    def regret(self, subscription_id):
        """Regret a subscription."""
        url = self.build_url(str(subscription_id), "regret")
        return self.api_call(url, "POST")


class CreditcheckV2(BaseResource):
    """The creditcheck resource."""

    namespace = CREDITCHECK

    @property
    def stage_url(self):
        """Return the stage URL."""
        return "https://api.stage.kriita.com/creditcheck/v2"

    @property
    def production_url(self):
        """Return the production URL."""
        return "https://api.kriita.com/creditcheck/v2"

    @operation
    def create(self, **params):
        url = self.build_url("check")
        return self.api_call(url, "POST", **params)

    @operation
    def search(self, **params):
        url = self.build_url("search")
        return self.api_call(url, "POST", **params)


class CheckoutSessionV1(BaseResource):
    """The checkout session resource."""

    namespace = CHECKOUT_SESSION

    @property
    def stage_url(self):
        """Return the stage URL."""
        return "https://checkout.stage.paylevo.com/v1"

    @property
    def production_url(self):
        """Return the production URL."""
        return "https://checkout.paylevo.com/v1"

    @operation
    def create(self, **params):
        """Create a checkout session"""
        url = self.build_url("session", "create")
        return self.api_call(url, "POST", **params)
