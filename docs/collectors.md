# Collector Reference

This page provides a comprehensive reference of all metric collectors in the UniFi Protect Exporter.

!!! summary "Collector Overview"
    🏗️ **Total Collectors:** TBD
    📋 **Registered Collectors:** TBD
    🔗 **Coordinators with Sub-collectors:** TBD

## 🏛️ Architecture Overview

The collector system is organized in a hierarchical pattern:

### Update Tiers

Collectors are organized into three update tiers based on data volatility:

| Tier | Interval | Purpose | Examples |
|------|----------|---------|----------|
| 🚀 **FAST** | 60s | Real-time status, critical metrics | Motion events, camera status |
| ⚡ **MEDIUM** | 300s | Regular metrics, performance data | Camera metrics, recording stats |
| 🐌 **SLOW** | 900s | Infrequent data, configuration | System configuration, device info |

### Collector Types

| Type | Description | Registration |
|------|-------------|--------------|
| **Main Collectors** | Top-level collectors with `@register_collector` | Automatic |
| **Coordinator Collectors** | Manage multiple sub-collectors | Automatic |
| **Sub-collectors** | Specialized collectors for specific metrics | Manual |
| **Device Collectors** | Device-type specific (cameras, sensors) | Manual |

## 🧭 Quick Navigation

### By Update Tier

??? abstract "🚀 FAST Tier (TBD collectors)"

    - Motion event collectors (planned)
    - Real-time camera status (planned)

??? abstract "⚡ MEDIUM Tier (TBD collectors)"

    - Camera metrics collector (planned)
    - Recording statistics collector (planned)
    - System health collector (planned)

??? abstract "🐌 SLOW Tier (TBD collectors)"

    - Configuration collector (planned)
    - Device information collector (planned)

## 📋 Planned Collectors

### CameraCollector

!!! info "Collector Information"
    **Purpose:** Collector for camera-level metrics.
    **Update Tier:** MEDIUM (300s)
    **Status:** Planned

#### 📊 Metrics to be Collected

- Camera online/offline status
- Recording status
- Storage usage per camera
- Motion detection events
- Video quality metrics
- Network bandwidth usage

### SystemCollector

!!! info "Collector Information"
    **Purpose:** Collector for UniFi Protect system metrics.
    **Update Tier:** SLOW (900s)
    **Status:** Planned

#### 📊 Metrics to be Collected

- Total number of cameras
- System storage usage
- NVR CPU and memory usage
- System version information
- License information

### MotionEventCollector

!!! info "Collector Information"
    **Purpose:** Collector for motion detection events.
    **Update Tier:** FAST (60s)
    **Status:** Planned

#### 📊 Metrics to be Collected

- Motion events per camera
- Motion event duration
- Motion event zones
- Smart detection events (person, vehicle, etc.)

### RecordingCollector

!!! info "Collector Information"
    **Purpose:** Collector for recording statistics.
    **Update Tier:** MEDIUM (300s)
    **Status:** Planned

#### 📊 Metrics to be Collected

- Recording duration per camera
- Recording quality statistics
- Recording gaps/failures
- Storage usage trends

## 📚 Usage Guide

!!! tip "Understanding Collector Hierarchy"
    - **Main Collectors** are registered with `@register_collector()` and run automatically
    - **Coordinator Collectors** manage multiple sub-collectors for related metrics
    - **Device Collectors** are specific to device types (cameras, sensors, etc.)
    - **Sub-collectors** are manually registered and called by their parent coordinators

!!! info "Update Tier Strategy"
    - **FAST (60s):** Critical metrics that change frequently (motion events, camera status)
    - **MEDIUM (300s):** Regular metrics with moderate change frequency (recording stats)
    - **SLOW (900s):** Stable metrics that change infrequently (configuration, system info)

!!! example "Adding a New Collector"
    ```python
    from ..core.collector import register_collector, MetricCollector, UpdateTier
    from ..core.constants.metrics_constants import MetricName
    from ..core.error_handling import with_error_handling

    @register_collector(UpdateTier.MEDIUM)
    class CameraCollector(MetricCollector):
        """Collector for UniFi Protect camera metrics."""

        def _initialize_metrics(self) -> None:
            self.camera_status = self._create_gauge(
                MetricName.CAMERA_STATUS,
                "Camera online status (1 = online, 0 = offline)"
            )

        @with_error_handling('Collect camera data')
        async def _collect_impl(self) -> None:
            # Collection logic here
            pass
    ```

For more information on metrics, see the [Metrics Reference](metrics/metrics.md).