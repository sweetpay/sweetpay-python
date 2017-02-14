# -*- coding: utf-8 -*-
import uuid

from .constants import SUBSCRIPTION
from .base import BaseResource, BaseClient


class SubscriptionClient(BaseClient):
    """The client used to connect to the checkout API"""

    @property
    def stage_url(self):
        """Return the stage URL."""
        return "https://api.stage.kriita.com/subscription"

    @property
    def production_url(self):
        """Return the production URL."""
        return "https://api.kriita.com/subscription"

    def create_subscription(self, **params):
        """Create a subscription."""
        url = self.build_url("create")
        return self.make_request(url, "POST", params)

    def regret_subscription(self, subscription_id):
        """Regret a subscription."""
        url = self.build_url(str(subscription_id), "regret")
        return self.make_request(url, "POST")

    def update_subscription(self, subscription_id, **params):
        """Update a subscription."""
        url = self.build_url(str(subscription_id), "update")
        return self.make_request(url, "POST", params)

    def query_subscription(self, subscription_id):
        """Query a subscription."""
        url = self.build_url(str(subscription_id), "query")
        return self.make_request(url, "GET")

    def search_subscriptions(self, **params):
        """Search for subscriptions."""
        url = self.build_url("search")
        return self.make_request(url, "POST", params)

    def log_subscription(self, subscription_id):
        url = self.build_url(str(subscription_id), "log")
        return self.make_request(url, "GET")


class SubscriptionV1(BaseResource):
    """The subscription resource."""

    CLIENT_CLS = SubscriptionClient
    namespace = SUBSCRIPTION

    def create(self, *args, **params):
        """Create a subscription."""
        return self.make_request("create_subscription", *args, **params)

    def query(self, *args, **params):
        """Query a subscription for information."""
        return self.make_request("query_subscription", *args, **params)

    def update(self, *args, **params):
        """Update a subscription."""
        return self.make_request("update_subscription", *args, **params)

    def search(self, *args, **params):
        """Search for subscriptions."""
        return self.make_request("search_subscriptions", *args, **params)

    def list_log(self, *args, **params):
        """List all of the log entries."""
        return self.make_request("log_subscription", *args, **params)

    def regret(self, *args, **params):
        """Regret a subscription."""
        return self.make_request("regret_subscription", *args, **params)
