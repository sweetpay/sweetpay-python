# -*- coding: utf-8 -*-
from .base import BaseClient, BaseResource

__all__ = ["Creditcheck"]


class CreditcheckClient(BaseClient):
    """The client used to connect to the creditcheck API"""

    @property
    def stage_url(self):
        """Return the stage URL."""
        return "https://api.stage.kriita.com/creditcheck"

    @property
    def production_url(self):
        """Return the production URL."""
        return "https://api.kriita.com/creditcheck"

    def make_check(self, **params):
        """Make a credit check.

        :param params: The parameters to pass on to the marshmallow
                deserialization, and then pass on to the server.
        :returns: Return a dictionary with the keys "response",
                "status_code", "data" and "raw_data".
        """
        url = self.build_url("check")
        return self.make_request(url, "POST", params)

    def search_checks(self, **params):
        url = self.build_url("search")
        return self.make_request(url, "POST", params)


class Creditcheck(BaseResource):
    """The creditcheck resource."""

    CLIENT_CLS = CreditcheckClient
    namespace = "creditcheck"

    @classmethod
    def create(cls, *args, **params):
        return cls.make_request("make_check", *args, **params)

    @classmethod
    def search(cls, *args, **params):
        return cls.make_request("search_checks", *args, **params)
