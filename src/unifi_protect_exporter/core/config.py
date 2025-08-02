"""Configuration management for UniFi Protect exporter."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .config_models import (
    APISettings,
    CameraSettings,
    CollectorSettings,
    LoggingSettings,
    MonitoringSettings,
    OTELSettings,
    ServerSettings,
    UniFiSettings,
    UpdateIntervals,
)


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_prefix="UNIFI_PROTECT_EXPORTER_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        str_strip_whitespace=True,
        validate_assignment=True,
        # Allow JSON parsing for complex fields
        json_parse_mode="lax",
    )

    # Sub-configurations
    unifi: UniFiSettings = Field(
        default_factory=UniFiSettings,
        description="UniFi Protect connection settings",
    )
    
    logging: LoggingSettings = Field(
        default_factory=LoggingSettings,
        description="Logging configuration",
    )
    
    api: APISettings = Field(
        default_factory=APISettings,
        description="API interaction settings",
    )
    
    update_intervals: UpdateIntervals = Field(
        default_factory=UpdateIntervals,
        description="Update interval configuration",
    )
    
    server: ServerSettings = Field(
        default_factory=ServerSettings,
        description="HTTP server configuration",
    )
    
    otel: OTELSettings = Field(
        default_factory=OTELSettings,
        description="OpenTelemetry configuration",
    )
    
    monitoring: MonitoringSettings = Field(
        default_factory=MonitoringSettings,
        description="Internal monitoring configuration",
    )
    
    collectors: CollectorSettings = Field(
        default_factory=CollectorSettings,
        description="Collector configuration",
    )
    
    cameras: CameraSettings = Field(
        default_factory=CameraSettings,
        description="Camera-specific settings",
    )

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization validation and setup."""
        super().model_post_init(__context)
        
        # Validate OTEL settings if enabled
        if self.otel.enabled and not self.otel.endpoint:
            msg = "OTEL endpoint must be provided when OTEL is enabled"
            raise ValueError(msg)

    @property
    def is_development(self) -> bool:
        """Check if running in development mode based on log level."""
        return self.logging.level == "DEBUG"

    def get_collector_interval(self, collector_name: str) -> int:
        """Get the update interval for a specific collector.

        Parameters
        ----------
        collector_name : str
            Name of the collector.

        Returns
        -------
        int
            Update interval in seconds.

        """
        # Map collectors to their update tiers
        fast_collectors = {"MotionCollector", "EventCollector"}
        slow_collectors = {"SystemCollector", "ConfigCollector"}
        
        if collector_name in fast_collectors:
            return self.update_intervals.fast
        elif collector_name in slow_collectors:
            return self.update_intervals.slow
        else:
            return self.update_intervals.medium

    def is_collector_enabled(self, collector_name: str) -> bool:
        """Check if a collector is enabled.

        Parameters
        ----------
        collector_name : str
            Name of the collector to check.

        Returns
        -------
        bool
            True if the collector is enabled, False otherwise.

        """
        # Check if explicitly disabled
        if collector_name in self.collectors.disable_collectors:
            return False
            
        # If enabled_collectors is None, all are enabled by default
        if self.collectors.enabled_collectors is None:
            return True
            
        # Otherwise, check if in enabled list
        return collector_name in self.collectors.enabled_collectors


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns
    -------
    Settings
        The application settings.

    """
    return Settings()


def get_version() -> str:
    """Get the application version from pyproject.toml.

    Returns
    -------
    str
        The application version.

    """
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[import-not-found]
    
    project_root = Path(__file__).parent.parent.parent.parent
    pyproject_path = project_root / "pyproject.toml"
    
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
        return data["project"]["version"]
    except Exception:
        return "0.0.0"