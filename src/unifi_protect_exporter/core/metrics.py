"""Metrics creation and management for UniFi Protect exporter."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from opentelemetry import metrics
from opentelemetry.metrics import CallbackOptions, Observation
from prometheus_client import Counter, Gauge, Histogram, Info

from .logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

logger = get_logger(__name__)


class MetricsManager:
    """Manages both Prometheus and OpenTelemetry metrics."""

    def __init__(self, namespace: str = "unifi_protect") -> None:
        """Initialize metrics manager.

        Parameters
        ----------
        namespace : str, optional
            Metric namespace prefix, by default "unifi_protect".

        """
        self.namespace = namespace
        self._prometheus_metrics: dict[str, Any] = {}
        self._otel_metrics: dict[str, Any] = {}
        self._meter = metrics.get_meter(__name__)
        
        logger.debug("Initialized MetricsManager", namespace=namespace)

    def create_gauge(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
        *,
        unit: str = "",
    ) -> Gauge:
        """Create a gauge metric.

        Parameters
        ----------
        name : str
            Metric name.
        description : str
            Metric description.
        labels : list[str] | None, optional
            Label names, by default None.
        unit : str, optional
            Unit of measurement, by default "".

        Returns
        -------
        Gauge
            Prometheus gauge metric.

        """
        labels = labels or []
        full_name = f"{self.namespace}_{name}"
        
        if full_name not in self._prometheus_metrics:
            gauge = Gauge(
                full_name,
                description,
                labelnames=labels,
                namespace="",  # Already included in full_name
            )
            self._prometheus_metrics[full_name] = gauge
            logger.debug(
                "Created gauge metric",
                name=full_name,
                labels=labels,
                unit=unit,
            )
        
        return self._prometheus_metrics[full_name]

    def create_counter(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
        *,
        unit: str = "",
    ) -> Counter:
        """Create a counter metric.

        Parameters
        ----------
        name : str
            Metric name.
        description : str
            Metric description.
        labels : list[str] | None, optional
            Label names, by default None.
        unit : str, optional
            Unit of measurement, by default "".

        Returns
        -------
        Counter
            Prometheus counter metric.

        """
        labels = labels or []
        full_name = f"{self.namespace}_{name}"
        
        if full_name not in self._prometheus_metrics:
            counter = Counter(
                full_name,
                description,
                labelnames=labels,
                namespace="",  # Already included in full_name
            )
            self._prometheus_metrics[full_name] = counter
            logger.debug(
                "Created counter metric",
                name=full_name,
                labels=labels,
                unit=unit,
            )
        
        return self._prometheus_metrics[full_name]

    def create_histogram(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
        buckets: list[float] | None = None,
        *,
        unit: str = "",
    ) -> Histogram:
        """Create a histogram metric.

        Parameters
        ----------
        name : str
            Metric name.
        description : str
            Metric description.
        labels : list[str] | None, optional
            Label names, by default None.
        buckets : list[float] | None, optional
            Histogram buckets, by default None.
        unit : str, optional
            Unit of measurement, by default "".

        Returns
        -------
        Histogram
            Prometheus histogram metric.

        """
        labels = labels or []
        full_name = f"{self.namespace}_{name}"
        
        if full_name not in self._prometheus_metrics:
            histogram = Histogram(
                full_name,
                description,
                labelnames=labels,
                buckets=buckets or Histogram.DEFAULT_BUCKETS,
                namespace="",  # Already included in full_name
            )
            self._prometheus_metrics[full_name] = histogram
            logger.debug(
                "Created histogram metric",
                name=full_name,
                labels=labels,
                buckets=buckets,
                unit=unit,
            )
        
        return self._prometheus_metrics[full_name]

    def create_info(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
    ) -> Info:
        """Create an info metric.

        Parameters
        ----------
        name : str
            Metric name.
        description : str
            Metric description.
        labels : list[str] | None, optional
            Label names, by default None.

        Returns
        -------
        Info
            Prometheus info metric.

        """
        labels = labels or []
        full_name = f"{self.namespace}_{name}"
        
        if full_name not in self._prometheus_metrics:
            info = Info(
                full_name,
                description,
                labelnames=labels,
                namespace="",  # Already included in full_name
            )
            self._prometheus_metrics[full_name] = info
            logger.debug(
                "Created info metric",
                name=full_name,
                labels=labels,
            )
        
        return self._prometheus_metrics[full_name]

    def create_otel_gauge(
        self,
        name: str,
        callback: Callable[[CallbackOptions], Iterable[Observation]],
        description: str = "",
        unit: str = "",
    ) -> None:
        """Create an OpenTelemetry observable gauge.

        Parameters
        ----------
        name : str
            Metric name.
        callback : Callable
            Callback function to generate observations.
        description : str, optional
            Metric description, by default "".
        unit : str, optional
            Unit of measurement, by default "".

        """
        full_name = f"{self.namespace}.{name}"
        
        if full_name not in self._otel_metrics:
            gauge = self._meter.create_observable_gauge(
                name=full_name,
                callbacks=[callback],
                description=description,
                unit=unit,
            )
            self._otel_metrics[full_name] = gauge
            logger.debug(
                "Created OTEL gauge metric",
                name=full_name,
                unit=unit,
            )

    def create_otel_counter(
        self,
        name: str,
        callback: Callable[[CallbackOptions], Iterable[Observation]],
        description: str = "",
        unit: str = "",
    ) -> None:
        """Create an OpenTelemetry observable counter.

        Parameters
        ----------
        name : str
            Metric name.
        callback : Callable
            Callback function to generate observations.
        description : str, optional
            Metric description, by default "".
        unit : str, optional
            Unit of measurement, by default "".

        """
        full_name = f"{self.namespace}.{name}"
        
        if full_name not in self._otel_metrics:
            counter = self._meter.create_observable_counter(
                name=full_name,
                callbacks=[callback],
                description=description,
                unit=unit,
            )
            self._otel_metrics[full_name] = counter
            logger.debug(
                "Created OTEL counter metric",
                name=full_name,
                unit=unit,
            )

    def get_metric(self, name: str) -> Any:
        """Get a metric by name.

        Parameters
        ----------
        name : str
            Metric name (without namespace prefix).

        Returns
        -------
        Any
            The metric object or None if not found.

        """
        full_name = f"{self.namespace}_{name}"
        return self._prometheus_metrics.get(full_name)


# Global metrics manager instance
metrics_manager = MetricsManager()


# Convenience functions for common metrics
def create_collector_duration_histogram(collector_name: str) -> Histogram:
    """Create a histogram for collector duration.

    Parameters
    ----------
    collector_name : str
        Name of the collector.

    Returns
    -------
    Histogram
        Duration histogram for the collector.

    """
    return metrics_manager.create_histogram(
        "collector_duration_seconds",
        "Time spent collecting metrics",
        labels=["collector"],
        unit="seconds",
    )


def create_collector_error_counter(collector_name: str) -> Counter:
    """Create a counter for collector errors.

    Parameters
    ----------
    collector_name : str
        Name of the collector.

    Returns
    -------
    Counter
        Error counter for the collector.

    """
    return metrics_manager.create_counter(
        "collector_errors_total",
        "Total number of errors during collection",
        labels=["collector", "error_category"],
        unit="errors",
    )


def create_api_request_counter() -> Counter:
    """Create a counter for API requests.

    Returns
    -------
    Counter
        API request counter.

    """
    return metrics_manager.create_counter(
        "api_requests_total",
        "Total number of API requests",
        labels=["endpoint", "status"],
        unit="requests",
    )


def create_api_request_duration_histogram() -> Histogram:
    """Create a histogram for API request duration.

    Returns
    -------
    Histogram
        API request duration histogram.

    """
    return metrics_manager.create_histogram(
        "api_request_duration_seconds",
        "API request duration",
        labels=["endpoint"],
        unit="seconds",
    )