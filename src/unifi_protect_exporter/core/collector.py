"""Base collector class for UniFi Protect metrics."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from opentelemetry import trace

from .error_handling import ErrorCategory
from .logging import get_logger
from .metrics import (
    create_collector_duration_histogram,
    create_collector_error_counter,
)

if TYPE_CHECKING:
    from ..api.client import AsyncUniFiProtectClient
    from .config import Settings

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)


class BaseCollector(ABC):
    """Base class for all metric collectors.

    This class provides common functionality for metric collection including:
    - Error tracking and reporting
    - Collection duration monitoring
    - Automatic registration
    - Configuration management

    """

    # Class variable to track all collector subclasses
    _collectors: ClassVar[list[type[BaseCollector]]] = []
    
    # Collector metadata
    name: ClassVar[str] = ""
    description: ClassVar[str] = ""
    
    def __init__(
        self,
        client: AsyncUniFiProtectClient,
        settings: Settings,
    ) -> None:
        """Initialize the base collector.

        Parameters
        ----------
        client : AsyncUniFiProtectClient
            The UniFi Protect API client.
        settings : Settings
            Application settings.

        """
        self.client = client
        self.settings = settings
        self._last_update: float = 0
        self._consecutive_failures: int = 0
        self._total_collections: int = 0
        self._last_error: Exception | None = None
        
        # Initialize monitoring metrics
        self._duration_histogram = create_collector_duration_histogram(self.name)
        self._error_counter = create_collector_error_counter(self.name)
        
        logger.debug(
            "Initialized collector",
            collector=self.name,
            description=self.description,
        )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Register collector subclasses automatically."""
        super().__init_subclass__(**kwargs)
        if cls.name:  # Only register if name is set
            BaseCollector._collectors.append(cls)
            logger.debug(
                "Registered collector",
                collector=cls.name,
                class_name=cls.__name__,
            )

    @classmethod
    def get_all_collectors(cls) -> list[type[BaseCollector]]:
        """Get all registered collector classes.

        Returns
        -------
        list[type[BaseCollector]]
            List of all collector classes.

        """
        return cls._collectors.copy()

    @abstractmethod
    async def collect(self) -> None:
        """Collect metrics from the UniFi Protect API.

        This method must be implemented by all subclasses.

        """

    async def update(self) -> None:
        """Update metrics with error handling and monitoring.

        This method wraps the collect() method with:
        - Duration tracking
        - Error handling
        - Consecutive failure tracking
        - OpenTelemetry tracing

        """
        with tracer.start_as_current_span(f"collector.{self.name}") as span:
            span.set_attribute("collector.name", self.name)
            start_time = time.time()
            
            try:
                logger.debug(
                    "Starting metric collection",
                    collector=self.name,
                    last_update=self._last_update,
                )
                
                await self.collect()
                
                # Update success metrics
                duration = time.time() - start_time
                self._duration_histogram.labels(collector=self.name).observe(duration)
                self._last_update = time.time()
                self._consecutive_failures = 0
                self._total_collections += 1
                self._last_error = None
                
                span.set_attribute("collector.success", True)
                span.set_attribute("collector.duration", duration)
                
                logger.debug(
                    "Completed metric collection",
                    collector=self.name,
                    duration=duration,
                    total_collections=self._total_collections,
                )
                
            except Exception as e:
                duration = time.time() - start_time
                self._consecutive_failures += 1
                self._last_error = e
                
                # Determine error category
                error_category = ErrorCategory.API_CLIENT_ERROR
                if hasattr(e, "category"):
                    error_category = e.category
                
                # Track error
                self._error_counter.labels(
                    collector=self.name,
                    error_category=error_category.value,
                ).inc()
                
                span.set_attribute("collector.success", False)
                span.set_attribute("collector.error", str(e))
                span.set_attribute("collector.error_category", error_category.value)
                span.set_attribute("collector.consecutive_failures", self._consecutive_failures)
                
                logger.error(
                    "Error during metric collection",
                    collector=self.name,
                    error=str(e),
                    error_type=type(e).__name__,
                    consecutive_failures=self._consecutive_failures,
                    duration=duration,
                    exc_info=True,
                )
                
                # Re-raise if we've hit the failure threshold
                if self._consecutive_failures >= self.settings.monitoring.max_consecutive_failures:
                    logger.error(
                        "Collector has exceeded maximum consecutive failures",
                        collector=self.name,
                        max_failures=self.settings.monitoring.max_consecutive_failures,
                    )
                    raise

    def _track_error(self, category: ErrorCategory) -> None:
        """Track an error for monitoring.

        Parameters
        ----------
        category : ErrorCategory
            The error category.

        """
        self._error_counter.labels(
            collector=self.name,
            error_category=category.value,
        ).inc()

    @property
    def update_interval(self) -> int:
        """Get the update interval for this collector.

        Returns
        -------
        int
            Update interval in seconds.

        """
        return self.settings.get_collector_interval(self.name)

    @property
    def is_enabled(self) -> bool:
        """Check if this collector is enabled.

        Returns
        -------
        bool
            True if the collector is enabled, False otherwise.

        """
        return self.settings.is_collector_enabled(self.name)

    @property
    def time_since_update(self) -> float:
        """Get time since last successful update.

        Returns
        -------
        float
            Time in seconds since last update.

        """
        if self._last_update == 0:
            return float("inf")
        return time.time() - self._last_update

    @property
    def is_healthy(self) -> bool:
        """Check if the collector is healthy.

        Returns
        -------
        bool
            True if the collector is healthy, False otherwise.

        """
        return (
            self._consecutive_failures < self.settings.monitoring.max_consecutive_failures
            and self._last_error is None
        )

    def get_status(self) -> dict[str, Any]:
        """Get collector status information.

        Returns
        -------
        dict[str, Any]
            Status information including health, last update, and error details.

        """
        return {
            "name": self.name,
            "enabled": self.is_enabled,
            "healthy": self.is_healthy,
            "last_update": self._last_update,
            "time_since_update": self.time_since_update,
            "consecutive_failures": self._consecutive_failures,
            "total_collections": self._total_collections,
            "update_interval": self.update_interval,
            "last_error": str(self._last_error) if self._last_error else None,
        }


def get_enabled_collectors(
    client: AsyncUniFiProtectClient,
    settings: Settings,
) -> list[BaseCollector]:
    """Get instances of all enabled collectors.

    Parameters
    ----------
    client : AsyncUniFiProtectClient
        The UniFi Protect API client.
    settings : Settings
        Application settings.

    Returns
    -------
    list[BaseCollector]
        List of enabled collector instances.

    """
    collectors = []
    
    for collector_class in BaseCollector.get_all_collectors():
        if settings.is_collector_enabled(collector_class.name):
            try:
                collector = collector_class(client, settings)
                collectors.append(collector)
                logger.info(
                    "Enabled collector",
                    collector=collector_class.name,
                    update_interval=collector.update_interval,
                )
            except Exception:
                logger.exception(
                    "Failed to initialize collector",
                    collector=collector_class.name,
                )
    
    return collectors