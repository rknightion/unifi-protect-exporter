"""Logging configuration for UniFi Protect exporter."""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING, Any

import structlog
from structlog.types import Processor

if TYPE_CHECKING:
    from structlog.types import EventDict, WrappedLogger


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging for the application.

    Parameters
    ----------
    level : str, optional
        Logging level, by default "INFO".

    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )
    
    # Disable noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uiprotect").setLevel(logging.WARNING)
    
    # Configure structlog processors
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add appropriate renderer based on environment
    if sys.stderr.isatty():
        # Development mode - pretty console output
        processors.append(
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.RichTracebackFormatter(
                    show_locals=level == "DEBUG",
                ),
            )
        )
    else:
        # Production mode - JSON output
        processors.append(structlog.processors.JSONRenderer())
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> Any:
    """Get a structured logger instance.

    Parameters
    ----------
    name : str | None, optional
        Logger name, typically __name__, by default None.

    Returns
    -------
    Any
        Structured logger instance.

    """
    return structlog.get_logger(name)


class LogContext:
    """Context manager for adding temporary log context."""

    def __init__(self, logger: Any, **kwargs: Any) -> None:
        """Initialize the log context.

        Parameters
        ----------
        logger : Any
            The logger instance.
        **kwargs : Any
            Key-value pairs to add to the log context.

        """
        self.logger = logger
        self.context = kwargs

    def __enter__(self) -> LogContext:
        """Enter the context and bind the values."""
        self.logger = self.logger.bind(**self.context)
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit the context and unbind the values."""
        for key in self.context:
            self.logger = self.logger.unbind(key)


def add_global_context(**kwargs: Any) -> None:
    """Add global context that will be included in all log messages.

    Parameters
    ----------
    **kwargs : Any
        Key-value pairs to add to global context.

    """
    structlog.contextvars.bind_contextvars(**kwargs)