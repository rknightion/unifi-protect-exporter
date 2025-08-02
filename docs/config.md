# Configuration Reference

This document provides a comprehensive reference for all configuration options available in the UniFi Protect Exporter.

## Overview

The exporter can be configured using environment variables.
All configuration is based on Pydantic models with built-in validation.

## Environment Variable Format

Configuration follows a hierarchical structure using environment variables:

- **All settings**: `UNIFI_PROTECT_EXPORTER_{SECTION}__{SETTING}`
- **Double underscore** (`__`) separates nested configuration levels

!!! example "Environment Variable Examples"
    ```bash
    # UniFi Protect API configuration
    export UNIFI_PROTECT_EXPORTER_UNIFI__HOST=192.168.1.100
    export UNIFI_PROTECT_EXPORTER_UNIFI__USERNAME=your_username
    export UNIFI_PROTECT_EXPORTER_UNIFI__PASSWORD=your_password
    
    # Logging configuration
    export UNIFI_PROTECT_EXPORTER_LOGGING__LEVEL=INFO
    
    # API settings
    export UNIFI_PROTECT_EXPORTER_API__TIMEOUT=30
    export UNIFI_PROTECT_EXPORTER_API__CONCURRENCY_LIMIT=5
    ```

## UniFi Protect Settings

Core UniFi Protect API configuration

| Environment Variable | Type | Default | Description |
|---------------------|------|---------|-------------|
| `UNIFI_PROTECT_EXPORTER_UNIFI__HOST` | `str` | `PydanticUndefined` | UniFi Protect NVR IP address or hostname |
| `UNIFI_PROTECT_EXPORTER_UNIFI__USERNAME` | `str` | `PydanticUndefined` | UniFi Protect username |
| `UNIFI_PROTECT_EXPORTER_UNIFI__PASSWORD` | `SecretStr` | `PydanticUndefined` | UniFi Protect password |
| `UNIFI_PROTECT_EXPORTER_UNIFI__PORT` | `int` | `443` | UniFi Protect API port |
| `UNIFI_PROTECT_EXPORTER_UNIFI__VERIFY_SSL` | `bool` | `False` | Verify SSL certificates (often self-signed) |

## Logging Settings

Logging configuration

| Environment Variable | Type | Default | Description |
|---------------------|------|---------|-------------|
| `UNIFI_PROTECT_EXPORTER_LOGGING__LEVEL` | `str` | `INFO` | Logging level |

## API Settings

Configuration for UniFi Protect API interactions

| Environment Variable | Type | Default | Description |
|---------------------|------|---------|-------------|
| `UNIFI_PROTECT_EXPORTER_API__MAX_RETRIES` | `int` | `3` | Maximum number of retries for API requests |
| `UNIFI_PROTECT_EXPORTER_API__TIMEOUT` | `int` | `30` | API request timeout in seconds |
| `UNIFI_PROTECT_EXPORTER_API__CONCURRENCY_LIMIT` | `int` | `5` | Maximum concurrent API requests |
| `UNIFI_PROTECT_EXPORTER_API__BATCH_SIZE` | `int` | `10` | Default batch size for API operations |
| `UNIFI_PROTECT_EXPORTER_API__BATCH_DELAY` | `float` | `0.5` | Delay between batches in seconds |
| `UNIFI_PROTECT_EXPORTER_API__RATE_LIMIT_RETRY_WAIT` | `int` | `5` | Wait time in seconds when rate limited |
| `UNIFI_PROTECT_EXPORTER_API__ACTION_BATCH_RETRY_WAIT` | `int` | `10` | Wait time for action batch retries |

## Update Intervals

Control how often different types of metrics are collected

| Environment Variable | Type | Default | Description |
|---------------------|------|---------|-------------|
| `UNIFI_PROTECT_EXPORTER_UPDATE_INTERVALS__FAST` | `int` | `60` | Interval for fast-moving data (motion events) in seconds |
| `UNIFI_PROTECT_EXPORTER_UPDATE_INTERVALS__MEDIUM` | `int` | `300` | Interval for medium-moving data (camera metrics) in seconds |
| `UNIFI_PROTECT_EXPORTER_UPDATE_INTERVALS__SLOW` | `int` | `900` | Interval for slow-moving data (configuration) in seconds |

## Server Settings

HTTP server configuration for the metrics endpoint

| Environment Variable | Type | Default | Description |
|---------------------|------|---------|-------------|
| `UNIFI_PROTECT_EXPORTER_SERVER__HOST` | `str` | `0.0.0.0` | Host to bind the exporter to |
| `UNIFI_PROTECT_EXPORTER_SERVER__PORT` | `int` | `9099` | Port to bind the exporter to |
| `UNIFI_PROTECT_EXPORTER_SERVER__PATH_PREFIX` | `str` | `` | URL path prefix for all endpoints |
| `UNIFI_PROTECT_EXPORTER_SERVER__ENABLE_HEALTH_CHECK` | `bool` | `True` | Enable /health endpoint |

## OpenTelemetry Settings

OpenTelemetry observability configuration

| Environment Variable | Type | Default | Description |
|---------------------|------|---------|-------------|
| `UNIFI_PROTECT_EXPORTER_OTEL__ENABLED` | `bool` | `False` | Enable OpenTelemetry export |
| `UNIFI_PROTECT_EXPORTER_OTEL__ENDPOINT` | `str | None` | `_(none)_` | OpenTelemetry collector endpoint |
| `UNIFI_PROTECT_EXPORTER_OTEL__SERVICE_NAME` | `str` | `unifi-protect-exporter` | Service name for OpenTelemetry |
| `UNIFI_PROTECT_EXPORTER_OTEL__EXPORT_INTERVAL` | `int` | `60` | Export interval for OpenTelemetry metrics |
| `UNIFI_PROTECT_EXPORTER_OTEL__RESOURCE_ATTRIBUTES` | `dict` | `PydanticUndefined` | Additional resource attributes for OpenTelemetry |

## Monitoring Settings

Internal monitoring and alerting configuration

| Environment Variable | Type | Default | Description |
|---------------------|------|---------|-------------|
| `UNIFI_PROTECT_EXPORTER_MONITORING__MAX_CONSECUTIVE_FAILURES` | `int` | `10` | Maximum consecutive failures before alerting |
| `UNIFI_PROTECT_EXPORTER_MONITORING__HISTOGRAM_BUCKETS` | `list` | `[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]` | Histogram buckets for collector duration metrics |

## Collector Settings

Enable/disable specific metric collectors

| Environment Variable | Type | Default | Description |
|---------------------|------|---------|-------------|
| `UNIFI_PROTECT_EXPORTER_COLLECTORS__ENABLED_COLLECTORS` | `set` | `PydanticUndefined` | Enabled collector names |
| `UNIFI_PROTECT_EXPORTER_COLLECTORS__DISABLE_COLLECTORS` | `set` | `PydanticUndefined` | Explicitly disabled collectors (overrides enabled) |
| `UNIFI_PROTECT_EXPORTER_COLLECTORS__COLLECTOR_TIMEOUT` | `int` | `120` | Timeout for individual collector runs in seconds |

## Camera Settings

Camera-specific settings

| Environment Variable | Type | Default | Description |
|---------------------|------|---------|-------------|
| `UNIFI_PROTECT_EXPORTER_CAMERAS__COLLECT_MOTION_EVENTS` | `bool` | `True` | Collect motion event metrics |
| `UNIFI_PROTECT_EXPORTER_CAMERAS__COLLECT_RECORDING_STATS` | `bool` | `True` | Collect recording statistics |
| `UNIFI_PROTECT_EXPORTER_CAMERAS__MAX_CAMERAS` | `int` | `1000` | Maximum cameras to track |