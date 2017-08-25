"""
Tests for all base functionality.
"""

import pytest

from sweetpay import Resource
from sweetpay.errors import FailureStatusError, BadDataError, \
    UnauthorizedError, NotFoundError, MethodNotAllowedError, \
    InvalidParameterError, InternalServerError, ProxyError, \
    UnderMaintenanceError, SweetpayError


@pytest.fixture()
def resource():
    return Resource


class TestCheckForErrors:

    def test_ok(self, resource):
        # Execute
        data = resource._check_for_errors(200, {"status": "OK"}, None)

        # Verify
        assert data == {"status": "OK"}

    def test_failure_status(self, resource):
        # Verify
        with pytest.raises(FailureStatusError):
            # Execute
            resource._check_for_errors(200, {"status": "NOT_ENOUGH_CREDIT"}, None)

    def test_bad_data(self, resource):
        # Verify
        with pytest.raises(BadDataError):
            # Execute
            resource._check_for_errors(400, None, None)

    def test_unauthorized(self, resource):
        # Verify
        with pytest.raises(UnauthorizedError):
            # Execute
            resource._check_for_errors(401, None, None)

    def test_not_found(self, resource):
        # Verify
        with pytest.raises(NotFoundError):
            # Execute
            resource._check_for_errors(404, None, None)

    def test_method_not_allowed(self, resource):
        # Verify
        with pytest.raises(MethodNotAllowedError):
            # Execute
            resource._check_for_errors(405, None, None)

    def test_invalid_parameter(self, resource):
        # Verify
        with pytest.raises(InvalidParameterError):
            # Execute
            resource._check_for_errors(422, None, None)

    def test_internal_server_error(self, resource):
        # Verify
        with pytest.raises(InternalServerError):
            # Execute
            resource._check_for_errors(500, None, None)

    def test_proxy_error(self, resource):
        # Verify
        with pytest.raises(ProxyError):
            # Execute
            resource._check_for_errors(502, None, None)

    def test_under_maintenance(self, resource):
        # Verify
        with pytest.raises(UnderMaintenanceError):
            # Execute
            resource._check_for_errors(503, None, None)

    def test_general_exception(self, resource):
        # Verify
        with pytest.raises(SweetpayError):
            # Execute
            resource._check_for_errors(505, None, None)

    @pytest.mark.parametrize("data", [None, 123, "123", {}])
    def test_error_when_no_status(self, resource, data):
        # Execute
        with pytest.raises(FailureStatusError) as excinfo:
            resource._check_for_errors(200, data, None)

        # Verify
        exc = excinfo.value
        assert exc.status is None

    def test_error_with_status(self, resource):
        # Execute
        with pytest.raises(FailureStatusError) as excinfo:
            resource._check_for_errors(200, {"status": "SOME_STATUS"}, None)

        # Verify
        exc = excinfo.value
        assert exc.status == "SOME_STATUS"

    def test_error_with_code(self, resource):
        # Execute
        with pytest.raises(FailureStatusError) as excinfo:
            resource._check_for_errors(200, None, None)

        # Verify
        exc = excinfo.value
        assert exc.code == 200

    def test_error_with_response(self, resource):
        # Setup: Doesn't matter what the response object is, since
        # we don't use it
        response = object()

        # Execute
        with pytest.raises(FailureStatusError) as excinfo:
            resource._check_for_errors(200, None, response)

        # Verify
        exc = excinfo.value
        assert exc.response is response
