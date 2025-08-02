"""Error handling utilities for UniFi Protect exporter."""

from __future__ import annotations

import functools
from enum import Enum
from typing import TYPE_CHECKING, Any, TypeVar, cast

from .logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

logger = get_logger(__name__)

T = TypeVar("T")


class ErrorCategory(Enum):
    """Error categories for monitoring and alerting."""

    API_RATE_LIMIT = "rate_limit"
    API_CLIENT_ERROR = "client_error"
    API_SERVER_ERROR = "server_error"
    API_NOT_AVAILABLE = "not_available"
    TIMEOUT = "timeout"
    PARSING = "parsing"
    VALIDATION = "validation"
    CONNECTION = "connection"
    AUTHENTICATION = "authentication"


class CollectorError(Exception):
    """Base exception for collector errors."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        *,
        collector: str | None = None,
        **context: Any,
    ) -> None:
        """Initialize collector error with context.

        Parameters
        ----------
        message : str
            Error message.
        category : ErrorCategory
            Error category for monitoring.
        collector : str | None, optional
            Collector name, by default None.
        **context : Any
            Additional context for logging.

        """
        super().__init__(message)
        self.category = category
        self.collector = collector
        self.context = context


class APINotAvailableError(CollectorError):
    """Raised when an API endpoint is not available (404)."""

    def __init__(self, endpoint: str, **context: Any) -> None:
        """Initialize API not available error."""
        super().__init__(
            f"API endpoint not available: {endpoint}",
            ErrorCategory.API_NOT_AVAILABLE,
            endpoint=endpoint,
            **context,
        )


class AuthenticationError(CollectorError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", **context: Any) -> None:
        """Initialize authentication error."""
        super().__init__(
            message,
            ErrorCategory.AUTHENTICATION,
            **context,
        )


class DataValidationError(CollectorError):
    """Raised when API response data doesn't match expected format."""

    def __init__(self, message: str, **context: Any) -> None:
        """Initialize data validation error."""
        super().__init__(
            message,
            ErrorCategory.VALIDATION,
            **context,
        )


def with_error_handling(
    operation: str,
    *,
    continue_on_error: bool = False,
    error_category: ErrorCategory | None = None,
    default_return: Any = None,
) -> Callable[[Callable[..., Coroutine[Any, Any, T]]], Callable[..., Coroutine[Any, Any, T | None]]]:
    """Decorator for consistent error handling in async functions.

    Parameters
    ----------
    operation : str
        Description of the operation for logging.
    continue_on_error : bool, optional
        If True, return None on error instead of raising, by default False.
    error_category : ErrorCategory | None, optional
        Default error category if not determined from exception, by default None.
    default_return : Any, optional
        Value to return on error if continue_on_error is True, by default None.

    Returns
    -------
    Callable
        Decorated function.

    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T | None]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T | None:
            try:
                return await func(*args, **kwargs)
            except CollectorError:
                # Re-raise collector errors as they already have proper context
                raise
            except Exception as e:
                # Determine error category
                category = error_category
                if category is None:
                    if "timeout" in str(e).lower():
                        category = ErrorCategory.TIMEOUT
                    elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                        category = ErrorCategory.AUTHENTICATION
                    elif "connection" in str(e).lower():
                        category = ErrorCategory.CONNECTION
                    else:
                        category = ErrorCategory.API_CLIENT_ERROR
                
                # Extract collector name if available
                collector_name = None
                if args and hasattr(args[0], "__class__"):
                    collector_name = args[0].__class__.__name__
                
                # Log the error with context
                logger.error(
                    f"Error during {operation}",
                    operation=operation,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    error_category=category.value,
                    collector=collector_name,
                    continue_on_error=continue_on_error,
                    exc_info=True,
                )
                
                # Track error metric if collector has the method
                if args and hasattr(args[0], "_track_error"):
                    args[0]._track_error(category)
                
                if continue_on_error:
                    return cast(T | None, default_return)
                else:
                    # Wrap in CollectorError for consistent handling
                    raise CollectorError(
                        f"Error during {operation}: {e}",
                        category,
                        collector=collector_name,
                        original_error=str(e),
                        error_type=type(e).__name__,
                    ) from e
        
        return wrapper
    
    return decorator


def validate_response_format(
    response: Any,
    expected_type: type,
    operation: str,
    *,
    allow_none: bool = False,
) -> Any:
    """Validate API response format.

    Parameters
    ----------
    response : Any
        The response to validate.
    expected_type : type
        Expected type of the response.
    operation : str
        Operation name for error messages.
    allow_none : bool, optional
        Whether None is a valid response, by default False.

    Returns
    -------
    Any
        The validated response.

    Raises
    ------
    DataValidationError
        If response doesn't match expected format.

    """
    if response is None and allow_none:
        return response
    
    if response is None:
        raise DataValidationError(
            f"{operation} returned None when {expected_type.__name__} was expected",
            operation=operation,
        )
    
    if not isinstance(response, expected_type):
        raise DataValidationError(
            f"{operation} returned {type(response).__name__} when {expected_type.__name__} was expected",
            operation=operation,
            actual_type=type(response).__name__,
            expected_type=expected_type.__name__,
        )
    
    return response