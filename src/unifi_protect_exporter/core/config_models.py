"""Configuration models for UniFi Protect exporter."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel, Field, SecretStr, field_validator
from pydantic_settings import SettingsConfigDict


class UniFiSettings(BaseModel):
    """UniFi Protect connection settings."""

    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    host: Annotated[
        str,
        Field(
            description="UniFi Protect NVR IP address or hostname",
            examples=["192.168.1.100", "nvr.local"],
        ),
    ]
    
    port: Annotated[
        int,
        Field(
            default=443,
            description="UniFi Protect API port",
            ge=1,
            le=65535,
        ),
    ] = 443
    
    username: Annotated[
        str,
        Field(
            description="UniFi Protect username",
            min_length=1,
        ),
    ]
    
    password: Annotated[
        SecretStr,
        Field(
            description="UniFi Protect password",
            min_length=1,
        ),
    ]
    
    verify_ssl: Annotated[
        bool,
        Field(
            default=False,
            description="Verify SSL certificates (often self-signed)",
        ),
    ] = False


class LoggingSettings(BaseModel):
    """Logging configuration."""

    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    level: Annotated[
        str,
        Field(
            default="INFO",
            description="Logging level",
            pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        ),
    ] = "INFO"


class APISettings(BaseModel):
    """API interaction settings."""

    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    max_retries: Annotated[
        int,
        Field(
            default=3,
            description="Maximum number of retries for API requests",
            ge=0,
            le=10,
        ),
    ] = 3
    
    timeout: Annotated[
        int,
        Field(
            default=30,
            description="API request timeout in seconds",
            ge=5,
            le=300,
        ),
    ] = 30
    
    concurrency_limit: Annotated[
        int,
        Field(
            default=5,
            description="Maximum concurrent API requests",
            ge=1,
            le=20,
        ),
    ] = 5
    
    batch_size: Annotated[
        int,
        Field(
            default=10,
            description="Default batch size for API operations",
            ge=1,
            le=100,
        ),
    ] = 10
    
    batch_delay: Annotated[
        float,
        Field(
            default=0.5,
            description="Delay between batches in seconds",
            ge=0.0,
            le=10.0,
        ),
    ] = 0.5
    
    rate_limit_retry_wait: Annotated[
        int,
        Field(
            default=5,
            description="Wait time in seconds when rate limited",
            ge=1,
            le=60,
        ),
    ] = 5
    
    action_batch_retry_wait: Annotated[
        int,
        Field(
            default=10,
            description="Wait time for action batch retries",
            ge=1,
            le=60,
        ),
    ] = 10


class UpdateIntervals(BaseModel):
    """Update interval configuration for different data types."""

    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    fast: Annotated[
        int,
        Field(
            default=60,
            description="Interval for fast-moving data (motion events) in seconds",
            ge=30,
            le=300,
        ),
    ] = 60
    
    medium: Annotated[
        int,
        Field(
            default=300,
            description="Interval for medium-moving data (camera metrics) in seconds",
            ge=60,
            le=900,
        ),
    ] = 300
    
    slow: Annotated[
        int,
        Field(
            default=900,
            description="Interval for slow-moving data (configuration) in seconds",
            ge=300,
            le=3600,
        ),
    ] = 900


class ServerSettings(BaseModel):
    """HTTP server configuration."""

    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    host: Annotated[
        str,
        Field(
            default="0.0.0.0",
            description="Host to bind the exporter to",
        ),
    ] = "0.0.0.0"
    
    port: Annotated[
        int,
        Field(
            default=9099,
            description="Port to bind the exporter to",
            ge=1,
            le=65535,
        ),
    ] = 9099
    
    path_prefix: Annotated[
        str,
        Field(
            default="",
            description="URL path prefix for all endpoints",
            pattern="^(/[^/]+)*$",
        ),
    ] = ""
    
    enable_health_check: Annotated[
        bool,
        Field(
            default=True,
            description="Enable /health endpoint",
        ),
    ] = True


class OTELSettings(BaseModel):
    """OpenTelemetry configuration."""

    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    enabled: Annotated[
        bool,
        Field(
            default=False,
            description="Enable OpenTelemetry export",
        ),
    ] = False
    
    endpoint: Annotated[
        str | None,
        Field(
            default=None,
            description="OpenTelemetry collector endpoint",
            examples=["http://localhost:4317"],
        ),
    ] = None
    
    service_name: Annotated[
        str,
        Field(
            default="unifi-protect-exporter",
            description="Service name for OpenTelemetry",
        ),
    ] = "unifi-protect-exporter"
    
    export_interval: Annotated[
        int,
        Field(
            default=60,
            description="Export interval for OpenTelemetry metrics in seconds",
            ge=10,
            le=300,
        ),
    ] = 60
    
    resource_attributes: Annotated[
        dict[str, Any],
        Field(
            default_factory=dict,
            description="Additional resource attributes for OpenTelemetry",
        ),
    ] = Field(default_factory=dict)
    
    sampling_rate: Annotated[
        float,
        Field(
            default=0.1,
            description="Trace sampling rate (0.0-1.0)",
            ge=0.0,
            le=1.0,
        ),
    ] = 0.1


class MonitoringSettings(BaseModel):
    """Internal monitoring configuration."""

    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    max_consecutive_failures: Annotated[
        int,
        Field(
            default=10,
            description="Maximum consecutive failures before alerting",
            ge=1,
            le=100,
        ),
    ] = 10
    
    histogram_buckets: Annotated[
        list[float],
        Field(
            default=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
            description="Histogram buckets for collector duration metrics",
        ),
    ] = [0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]


class CollectorSettings(BaseModel):
    """Collector configuration."""

    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    enabled_collectors: Annotated[
        set[str] | None,
        Field(
            default=None,
            description="Enabled collector names (None means all enabled)",
        ),
    ] = None
    
    disable_collectors: Annotated[
        set[str],
        Field(
            default_factory=set,
            description="Explicitly disabled collectors (overrides enabled)",
        ),
    ] = Field(default_factory=set)
    
    collector_timeout: Annotated[
        int,
        Field(
            default=120,
            description="Timeout for individual collector runs in seconds",
            ge=30,
            le=600,
        ),
    ] = 120


class CameraSettings(BaseModel):
    """Camera-specific settings."""

    model_config = SettingsConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    collect_motion_events: Annotated[
        bool,
        Field(
            default=True,
            description="Collect motion event metrics",
        ),
    ] = True
    
    collect_recording_stats: Annotated[
        bool,
        Field(
            default=True,
            description="Collect recording statistics",
        ),
    ] = True
    
    max_cameras: Annotated[
        int,
        Field(
            default=1000,
            description="Maximum cameras to track",
            ge=1,
            le=10000,
        ),
    ] = 1000