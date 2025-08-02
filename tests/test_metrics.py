"""Tests for metrics creation and management."""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest
from prometheus_client import Counter, Gauge, Histogram, Info

from unifi_protect_exporter.core.metrics import (
    MetricsManager,
    create_api_request_counter,
    create_api_request_duration_histogram,
    create_collector_duration_histogram,
    create_collector_error_counter,
    metrics_manager,
)


class TestMetricsManager:
    """Test MetricsManager functionality."""
    
    def test_init_with_default_namespace(self) -> None:
        """Test initialization with default namespace."""
        manager = MetricsManager()
        assert manager.namespace == "unifi_protect"
        assert manager._prometheus_metrics == {}
        assert manager._otel_metrics == {}
    
    def test_init_with_custom_namespace(self) -> None:
        """Test initialization with custom namespace."""
        manager = MetricsManager(namespace="custom")
        assert manager.namespace == "custom"
    
    def test_create_gauge(self) -> None:
        """Test creating a gauge metric."""
        manager = MetricsManager()
        
        gauge = manager.create_gauge(
            "camera_online",
            "Camera online status",
            labels=["camera_id", "camera_name"],
            unit="boolean",
        )
        
        assert isinstance(gauge, Gauge)
        assert "unifi_protect_camera_online" in manager._prometheus_metrics
        
        # Creating again should return same instance
        gauge2 = manager.create_gauge(
            "camera_online",
            "Camera online status",
            labels=["camera_id", "camera_name"],
        )
        assert gauge == gauge2
    
    def test_create_counter(self) -> None:
        """Test creating a counter metric."""
        manager = MetricsManager()
        
        counter = manager.create_counter(
            "motion_events_total",
            "Total motion events",
            labels=["camera_id"],
            unit="events",
        )
        
        assert isinstance(counter, Counter)
        assert "unifi_protect_motion_events_total" in manager._prometheus_metrics
    
    def test_create_histogram(self) -> None:
        """Test creating a histogram metric."""
        manager = MetricsManager()
        
        histogram = manager.create_histogram(
            "api_duration_seconds",
            "API request duration",
            labels=["endpoint"],
            buckets=[0.1, 0.5, 1.0, 5.0],
            unit="seconds",
        )
        
        assert isinstance(histogram, Histogram)
        assert "unifi_protect_api_duration_seconds" in manager._prometheus_metrics
    
    def test_create_histogram_default_buckets(self) -> None:
        """Test creating histogram with default buckets."""
        manager = MetricsManager()
        
        histogram = manager.create_histogram(
            "request_size_bytes",
            "Request size",
            labels=["method"],
        )
        
        assert isinstance(histogram, Histogram)
    
    def test_create_info(self) -> None:
        """Test creating an info metric."""
        manager = MetricsManager()
        
        info = manager.create_info(
            "system_info",
            "System information",
            labels=["nvr_id", "nvr_name", "version"],
        )
        
        assert isinstance(info, Info)
        assert "unifi_protect_system_info" in manager._prometheus_metrics
    
    def test_get_metric(self) -> None:
        """Test retrieving a metric by name."""
        manager = MetricsManager()
        
        # Create a metric
        gauge = manager.create_gauge("test_metric", "Test metric")
        
        # Get it back
        retrieved = manager.get_metric("test_metric")
        assert retrieved == gauge
        
        # Non-existent metric should return None
        assert manager.get_metric("non_existent") is None
    
    @patch("unifi_protect_exporter.core.metrics.metrics.get_meter")
    def test_create_otel_gauge(self, mock_get_meter: Mock) -> None:
        """Test creating OpenTelemetry gauge."""
        mock_meter = MagicMock()
        mock_get_meter.return_value = mock_meter
        
        manager = MetricsManager()
        
        def callback(options):
            return []
        
        manager.create_otel_gauge(
            "camera_count",
            callback,
            description="Number of cameras",
            unit="cameras",
        )
        
        mock_meter.create_observable_gauge.assert_called_once_with(
            name="unifi_protect.camera_count",
            callbacks=[callback],
            description="Number of cameras",
            unit="cameras",
        )
        
        assert "unifi_protect.camera_count" in manager._otel_metrics
    
    @patch("unifi_protect_exporter.core.metrics.metrics.get_meter")
    def test_create_otel_counter(self, mock_get_meter: Mock) -> None:
        """Test creating OpenTelemetry counter."""
        mock_meter = MagicMock()
        mock_get_meter.return_value = mock_meter
        
        manager = MetricsManager()
        
        def callback(options):
            return []
        
        manager.create_otel_counter(
            "events_total",
            callback,
            description="Total events",
            unit="events",
        )
        
        mock_meter.create_observable_counter.assert_called_once_with(
            name="unifi_protect.events_total",
            callbacks=[callback],
            description="Total events",
            unit="events",
        )


class TestConvenienceFunctions:
    """Test convenience functions for common metrics."""
    
    def test_create_collector_duration_histogram(self) -> None:
        """Test creating collector duration histogram."""
        histogram = create_collector_duration_histogram("SystemCollector")
        
        assert isinstance(histogram, Histogram)
        # Should use global metrics manager
        assert metrics_manager.get_metric("collector_duration_seconds") == histogram
    
    def test_create_collector_error_counter(self) -> None:
        """Test creating collector error counter."""
        counter = create_collector_error_counter("SystemCollector")
        
        assert isinstance(counter, Counter)
        assert metrics_manager.get_metric("collector_errors_total") == counter
    
    def test_create_api_request_counter(self) -> None:
        """Test creating API request counter."""
        counter = create_api_request_counter()
        
        assert isinstance(counter, Counter)
        assert metrics_manager.get_metric("api_requests_total") == counter
    
    def test_create_api_request_duration_histogram(self) -> None:
        """Test creating API request duration histogram."""
        histogram = create_api_request_duration_histogram()
        
        assert isinstance(histogram, Histogram)
        assert metrics_manager.get_metric("api_request_duration_seconds") == histogram


class TestMetricLabels:
    """Test metric label handling."""
    
    def test_gauge_with_labels(self) -> None:
        """Test gauge metric with labels."""
        manager = MetricsManager()
        
        gauge = manager.create_gauge(
            "camera_fps",
            "Camera frames per second",
            labels=["camera_id", "camera_name", "stream"],
        )
        
        # Set value with labels
        gauge.labels(
            camera_id="cam123",
            camera_name="Front Door",
            stream="high",
        ).set(30.0)
        
        # Labels should work
        assert gauge.labels(
            camera_id="cam123",
            camera_name="Front Door",
            stream="high",
        )._value.get() == 30.0
    
    def test_counter_increment_with_labels(self) -> None:
        """Test counter increment with labels."""
        manager = MetricsManager()
        
        counter = manager.create_counter(
            "api_errors",
            "API errors",
            labels=["endpoint", "error_type"],
        )
        
        # Increment with labels
        counter.labels(endpoint="/cameras", error_type="timeout").inc()
        counter.labels(endpoint="/cameras", error_type="timeout").inc(2)
        
        # Check value
        assert counter.labels(
            endpoint="/cameras",
            error_type="timeout",
        )._value.get() == 3
    
    def test_histogram_observe_with_labels(self) -> None:
        """Test histogram observation with labels."""
        manager = MetricsManager()
        
        histogram = manager.create_histogram(
            "request_duration",
            "Request duration",
            labels=["method", "endpoint"],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0],
        )
        
        # Observe values
        histogram.labels(method="GET", endpoint="/api/cameras").observe(0.25)
        histogram.labels(method="GET", endpoint="/api/cameras").observe(0.75)
        histogram.labels(method="GET", endpoint="/api/cameras").observe(1.5)
        
        # Check that observations were recorded
        metric = histogram.labels(method="GET", endpoint="/api/cameras")
        assert metric._sum.get() == 2.5  # 0.25 + 0.75 + 1.5
        assert metric._count.get() == 3


class TestGlobalMetricsManager:
    """Test the global metrics manager instance."""
    
    def test_global_instance_exists(self) -> None:
        """Test that global metrics_manager exists."""
        assert metrics_manager is not None
        assert isinstance(metrics_manager, MetricsManager)
        assert metrics_manager.namespace == "unifi_protect"
    
    def test_global_instance_functionality(self) -> None:
        """Test that global instance works properly."""
        # Create a metric using global instance
        gauge = metrics_manager.create_gauge(
            "test_global",
            "Test global metric",
        )
        
        assert isinstance(gauge, Gauge)
        assert metrics_manager.get_metric("test_global") == gauge