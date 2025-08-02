"""Tests for error handling utilities."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

from unifi_protect_exporter.core.error_handling import (
    APINotAvailableError,
    CollectorError,
    DataValidationError,
    ErrorCategory,
    validate_response_format,
    with_error_handling,
)


class TestErrorCategories:
    """Test error category enum values."""

    def test_error_category_values(self) -> None:
        """Test that error category enum has expected values."""
        assert ErrorCategory.API_RATE_LIMIT == "rate_limit"
        assert ErrorCategory.API_CLIENT_ERROR == "client_error"
        assert ErrorCategory.API_SERVER_ERROR == "server_error"
        assert ErrorCategory.API_NOT_AVAILABLE == "not_available"
        assert ErrorCategory.TIMEOUT == "timeout"
        assert ErrorCategory.PARSING == "parsing"
        assert ErrorCategory.VALIDATION == "validation"
        assert ErrorCategory.CONNECTION == "connection"
        assert ErrorCategory.AUTHENTICATION == "authentication"


class TestCollectorErrors:
    """Test custom exception classes."""

    def test_collector_error_initialization(self) -> None:
        """Test CollectorError initialization."""
        error = CollectorError(
            "Test error",
            ErrorCategory.API_CLIENT_ERROR,
            {"request_id": "123", "status_code": 400},
        )
        assert str(error) == "Test error"
        assert error.category == ErrorCategory.API_CLIENT_ERROR
        assert error.context == {"request_id": "123", "status_code": 400}

    def test_collector_error_default_values(self) -> None:
        """Test CollectorError with default values."""
        error = CollectorError("Test error", ErrorCategory.VALIDATION)
        assert error.category == ErrorCategory.VALIDATION
        assert error.context == {}

    def test_api_not_available_error(self) -> None:
        """Test APINotAvailableError."""
        error = APINotAvailableError(
            "/api/v1/organizations/123/devices",
            {"org_id": "123"},
        )
        assert "API endpoint '/api/v1/organizations/123/devices' not available" in str(error)
        assert error.category == ErrorCategory.API_NOT_AVAILABLE
        assert error.context == {"org_id": "123"}

    def test_data_validation_error(self) -> None:
        """Test DataValidationError."""
        error = DataValidationError(
            "Expected list, got dict",
            {"response_type": "dict", "endpoint": "/devices"},
        )
        assert str(error) == "Expected list, got dict"
        assert error.category == ErrorCategory.VALIDATION
        assert error.context == {"response_type": "dict", "endpoint": "/devices"}


class TestWithErrorHandlingDecorator:
    """Test the with_error_handling decorator."""

    @pytest.mark.asyncio
    async def test_successful_operation(self) -> None:
        """Test decorator with successful operation."""

        @with_error_handling(operation="Test operation")
        async def successful_operation() -> str:
            return "success"

        result = await successful_operation()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_error_handling_continue_on_error(self) -> None:
        """Test decorator continues on error when configured."""

        @with_error_handling(operation="Test operation", continue_on_error=True)
        async def failing_operation() -> str:
            raise ValueError("Test error")

        result = await failing_operation()
        assert result is None

    @pytest.mark.asyncio
    async def test_error_handling_reraise(self) -> None:
        """Test decorator re-raises when continue_on_error=False."""

        @with_error_handling(operation="Test operation", continue_on_error=False)
        async def failing_operation() -> str:
            raise ValueError("Test error")

        with pytest.raises(CollectorError) as exc_info:
            await failing_operation()

        assert "Error during Test operation: Test error" in str(exc_info.value)
        assert exc_info.value.category == ErrorCategory.API_CLIENT_ERROR

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self) -> None:
        """Test timeout error handling."""

        @with_error_handling(operation="Test operation", continue_on_error=True)
        async def timeout_operation() -> str:
            raise TimeoutError("Operation timed out")

        result = await timeout_operation()
        assert result is None

    @pytest.mark.asyncio
    async def test_categorized_error_handling(self) -> None:
        """Test error handling with specific category."""

        @with_error_handling(
            operation="API call",
            continue_on_error=False,
            error_category=ErrorCategory.API_SERVER_ERROR,
        )
        async def api_operation() -> str:
            raise Exception("500 Internal Server Error")

        with pytest.raises(CollectorError) as exc_info:
            await api_operation()

        assert exc_info.value.category == ErrorCategory.API_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_404_error_special_handling(self) -> None:
        """Test 404 errors are handled specially."""

        @with_error_handling(operation="Fetch resource", continue_on_error=True)
        async def not_found_operation() -> str:
            raise Exception("404 Not Found")

        result = await not_found_operation()
        assert result is None

    @pytest.mark.asyncio
    async def test_collector_context_extraction(self) -> None:
        """Test context extraction from collector instance."""

        class MockCollector:
            update_tier = MagicMock(value="MEDIUM")

            @with_error_handling(operation="Collect metrics", continue_on_error=True)
            async def collect(self) -> str:
                return "collected"

        collector = MockCollector()
        result = await collector.collect()
        assert result == "collected"

    @pytest.mark.asyncio
    async def test_error_tracking_integration(self) -> None:
        """Test error tracking when collector has _track_error method."""

        class MockCollector:
            def __init__(self) -> None:
                self._track_error = Mock()

            @with_error_handling(operation="Collect", continue_on_error=True)
            async def collect(self) -> str:
                raise ValueError("Test error")

        collector = MockCollector()
        await collector.collect()
        collector._track_error.assert_called_once_with(ErrorCategory.API_CLIENT_ERROR)


class TestValidateResponseFormat:
    """Test response format validation."""

    def test_validate_list_response(self) -> None:
        """Test validating list responses."""
        response = [{"id": 1}, {"id": 2}]
        result = validate_response_format(response, list, "Fetch items")
        assert result == response

    def test_validate_dict_response(self) -> None:
        """Test validating dict responses."""
        response = {"status": "ok", "count": 5}
        result = validate_response_format(response, dict, "Get status")
        assert result == response

    def test_validate_list_with_allow_none(self) -> None:
        """Test validating None response when allowed."""
        response = None
        result = validate_response_format(response, list, "Fetch items", allow_none=True)
        assert result is None

    def test_validate_invalid_type(self) -> None:
        """Test validation fails for wrong type."""
        response = {"id": 1}
        with pytest.raises(DataValidationError) as exc_info:
            validate_response_format(response, list, "Fetch list")

        assert "Expected list, got dict" in str(exc_info.value)
        assert exc_info.value.context["response_type"] == "dict"

    def test_validate_none_when_not_allowed(self) -> None:
        """Test validation fails for None when not allowed."""
        response = None
        with pytest.raises(DataValidationError) as exc_info:
            validate_response_format(response, list, "Fetch items")

        assert "returned None when list was expected" in str(exc_info.value)


class TestDecoratorReturnTypes:
    """Test decorator preserves proper return types."""

    @pytest.mark.asyncio
    async def test_return_type_preservation(self) -> None:
        """Test decorator preserves return type annotations."""

        @with_error_handling(operation="Test", continue_on_error=True)
        async def typed_function() -> list[dict[str, Any]]:
            return [{"key": "value"}]

        result = await typed_function()
        assert result == [{"key": "value"}]

    @pytest.mark.asyncio
    async def test_none_return_on_error(self) -> None:
        """Test decorator returns None on error when configured."""

        @with_error_handling(operation="Test", continue_on_error=True)
        async def failing_typed_function() -> list[dict[str, Any]]:
            raise ValueError("Error")

        result = await failing_typed_function()
        assert result is None


class TestErrorHandlingIntegration:
    """Test error handling integration scenarios."""

    @pytest.mark.asyncio
    async def test_nested_error_handling(self) -> None:
        """Test nested error handling decorators."""

        @with_error_handling(operation="Outer", continue_on_error=True)
        async def outer_function() -> str | None:
            return await inner_function()

        @with_error_handling(operation="Inner", continue_on_error=False)
        async def inner_function() -> str:
            raise ValueError("Inner error")

        result = await outer_function()
        assert result is None

    @pytest.mark.asyncio
    @patch("unifi_protect_exporter.core.error_handling.logger")
    async def test_logging_behavior(self, mock_logger: Mock) -> None:
        """Test logging behavior in error handling."""

        @with_error_handling(operation="Test operation", continue_on_error=True)
        async def operation_with_error() -> None:
            raise ValueError("Test error")

        await operation_with_error()

        # Verify error was logged
        mock_logger.exception.assert_called_once()
        call_args = mock_logger.exception.call_args
        assert "Error during Test operation" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_performance_timing(self) -> None:
        """Test operation timing in error handling."""

        @with_error_handling(operation="Timed operation", continue_on_error=True)
        async def slow_operation() -> None:
            await asyncio.sleep(0.1)
            raise ValueError("Error after delay")

        start_time = asyncio.get_event_loop().time()
        await slow_operation()
        duration = asyncio.get_event_loop().time() - start_time

        # Operation should have taken at least 0.1 seconds
        assert duration >= 0.1
