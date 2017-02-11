# -*- coding: utf-8 -*-
import json
from .base import BaseResource, BaseClient
from .utils import decode_datetime, decode_date

__all__ = ["Subscription"]


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


def deserialize_callback_data(data, is_json_str=False):
    """Deserialize callback data

    :param data: The actual data to deserialize.
    :param is_json_str: A boolean indicating if the the
                        passed data is a JSON or a Python object.
    """
    return json.loads(data)


class Subscription(BaseResource):
    """The subscription resource."""

    CLIENT_CLS = SubscriptionClient
    namespace = "subscription"

    @classmethod
    def create(cls, *args, **params):
        """Create a subscription."""
        return cls.make_request("create_subscription", *args, **params)

    @classmethod
    def query(cls, *args, **params):
        """Query a subscription for information."""
        return cls.make_request("query_subscription", *args, **params)

    @classmethod
    def update(cls, *args, **params):
        """Update a subscription."""
        return cls.make_request("update", *args, **params)

    @classmethod
    def search(cls, *args, **params):
        """Search for subscriptions."""
        return cls.make_request("search_subscriptions", *args, **params)

    @classmethod
    def list_log(cls, *args, **params):
        """List all of the log entries."""
        return cls.make_request("log_subscription", *args, **params)

    @classmethod
    def regret(cls, *args, **params):
        """Regret a subscription."""
        return cls.make_request("regret_subscription", *args, **params)


@Subscription.validates("payload", "startsAt")
def validate_starts_at(value):
    if value:
        return decode_date(value)
    return value


@Subscription.validates("payload", "createdAt")
def validate_payload_created_at(value):
    if value:
        return decode_datetime(value)
    return value


@Subscription.validates("payload")
def validate_payload_when_list(value):
    if isinstance(value, list):
        for sub in value:
            sub["startsAt"] = decode_datetime(sub["startsAt"])
            sub["createdAt"] = decode_datetime(sub["createdAt"])
    return value
