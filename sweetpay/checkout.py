# -*- coding: utf-8 -*-
from .base import BaseClient, BaseResource

__all__ = ["CheckoutSession"]


class CheckoutClient(BaseClient):
    """The client used to connect to the checkout API"""

    @property
    def stage_url(self):
        """Return the stage URL."""
        return "https://checkout.stage.paylevo.com"

    @property
    def production_url(self):
        """Return the production URL."""
        return "https://checkout.paylevo.com"

    def create_session(self, **params):
        """Create a checkout session.

        :param params: The parameters to pass on to the session.
        :returns: Return a dictionary with the keys "response",
                "status_code", "data" and "raw_data".
        """
        url = self.build_url("session", "create")
        return self.make_request(url, "POST", params)


class CheckoutSession(BaseResource):
    """The checkout session resource."""

    CLIENT_CLS = CheckoutClient
    namespace = "checkout"

    def create(self, *args, **params):
        """Create a checkout session"""
        return self.make_request("create_session", *args, **params)
