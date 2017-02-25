"""
Tests for all base functionality.
"""

import pytest


class TestCheckForErrors:

    @pytest.mark.xfail
    def test_check_for_errors(self):
        raise NotImplementedError


@pytest.mark.xfail
def test_version_support():
    raise NotImplementedError
