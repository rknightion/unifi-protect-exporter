"""System-level metrics collector for UniFi Protect."""

from __future__ import annotations

from typing import TYPE_CHECKING

from prometheus_client import Gauge, Info

from ..core.collector import BaseCollector
from ..core.constants import MetricLabels, MetricNames
from ..core.error_handling import with_error_handling
from ..core.logging import get_logger
from ..core.metrics import metrics_manager

if TYPE_CHECKING:
    from ..api.client import AsyncUniFiProtectClient
    from ..core.config import Settings

logger = get_logger(__name__)


class SystemCollector(BaseCollector):
    """Collects system-level metrics from UniFi Protect.

    This collector gathers:
    - NVR system information and status
    - Camera and sensor counts
    - Storage usage and capacity
    - System uptime

    """

    name = "SystemCollector"
    description = "Collects system-level metrics from UniFi Protect NVR"

    def __init__(
        self,
        client: AsyncUniFiProtectClient,
        settings: Settings,
    ) -> None:
        """Initialize the system collector."""
        super().__init__(client, settings)
        
        # Create metrics
        self._system_info = self._create_system_info_metric()
        self._nvr_uptime = self._create_nvr_uptime_metric()
        self._camera_count = self._create_camera_count_metric()
        self._sensor_count = self._create_sensor_count_metric()
        self._storage_used = self._create_storage_used_metric()
        self._storage_total = self._create_storage_total_metric()
        self._storage_percentage = self._create_storage_percentage_metric()
        
        logger.info(
            "Initialized SystemCollector",
            update_interval=self.update_interval,
        )

    def _create_system_info_metric(self) -> Info:
        """Create system info metric."""
        return metrics_manager.create_info(
            MetricNames.SYSTEM_INFO.value,
            "UniFi Protect system information",
            labels=[
                MetricLabels.NVR_ID.value,
                MetricLabels.NVR_NAME.value,
                MetricLabels.NVR_VERSION.value,
                "host",
                "platform",
                "firmware_version",
            ],
        )

    def _create_nvr_uptime_metric(self) -> Gauge:
        """Create NVR uptime metric."""
        return metrics_manager.create_gauge(
            MetricNames.NVR_UPTIME_SECONDS.value,
            "NVR uptime in seconds",
            labels=[
                MetricLabels.NVR_ID.value,
                MetricLabels.NVR_NAME.value,
            ],
            unit="seconds",
        )

    def _create_camera_count_metric(self) -> Gauge:
        """Create camera count metric."""
        return metrics_manager.create_gauge(
            MetricNames.CAMERA_COUNT.value,
            "Total number of cameras in the system",
            labels=[
                MetricLabels.NVR_ID.value,
                MetricLabels.NVR_NAME.value,
            ],
            unit="cameras",
        )

    def _create_sensor_count_metric(self) -> Gauge:
        """Create sensor count metric."""
        return metrics_manager.create_gauge(
            MetricNames.SENSOR_COUNT.value,
            "Total number of sensors in the system",
            labels=[
                MetricLabels.NVR_ID.value,
                MetricLabels.NVR_NAME.value,
            ],
            unit="sensors",
        )

    def _create_storage_used_metric(self) -> Gauge:
        """Create storage used metric."""
        return metrics_manager.create_gauge(
            MetricNames.STORAGE_USED_BYTES.value,
            "Storage space used in bytes",
            labels=[
                MetricLabels.NVR_ID.value,
                MetricLabels.NVR_NAME.value,
                MetricLabels.STORAGE_TYPE.value,
                MetricLabels.STORAGE_PATH.value,
            ],
            unit="bytes",
        )

    def _create_storage_total_metric(self) -> Gauge:
        """Create storage total metric."""
        return metrics_manager.create_gauge(
            MetricNames.STORAGE_TOTAL_BYTES.value,
            "Total storage space in bytes",
            labels=[
                MetricLabels.NVR_ID.value,
                MetricLabels.NVR_NAME.value,
                MetricLabels.STORAGE_TYPE.value,
                MetricLabels.STORAGE_PATH.value,
            ],
            unit="bytes",
        )

    def _create_storage_percentage_metric(self) -> Gauge:
        """Create storage percentage metric."""
        return metrics_manager.create_gauge(
            MetricNames.STORAGE_USED_PERCENTAGE.value,
            "Storage space used as a percentage",
            labels=[
                MetricLabels.NVR_ID.value,
                MetricLabels.NVR_NAME.value,
                MetricLabels.STORAGE_TYPE.value,
                MetricLabels.STORAGE_PATH.value,
            ],
            unit="percent",
        )

    @with_error_handling("collect_system_metrics")
    async def collect(self) -> None:
        """Collect system metrics from UniFi Protect."""
        logger.debug("Collecting system metrics")
        
        # Get NVR information
        nvr = await self.client.get_nvr()
        
        # Get bootstrap data for counts
        bootstrap = await self.client.get_bootstrap()
        
        # Common labels
        nvr_labels = {
            MetricLabels.NVR_ID.value: nvr.id,
            MetricLabels.NVR_NAME.value: nvr.name,
        }
        
        # Update system info
        self._system_info.labels(
            **nvr_labels,
            nvr_version=nvr.version,
            host=nvr.host,
            platform=nvr.platform or "unknown",
            firmware_version=nvr.firmwareVersion or "unknown",
        ).info({
            "nvr_version": nvr.version,
            "host": nvr.host,
            "platform": nvr.platform or "unknown",
            "firmware_version": nvr.firmwareVersion or "unknown",
        })
        
        # Update uptime
        if nvr.uptime is not None:
            self._nvr_uptime.labels(**nvr_labels).set(nvr.uptime)
        
        # Update camera count
        camera_count = len(bootstrap.get("cameras", []))
        self._camera_count.labels(**nvr_labels).set(camera_count)
        logger.info(
            "Collected camera count",
            camera_count=camera_count,
            nvr_name=nvr.name,
        )
        
        # Update sensor count
        sensor_count = len(bootstrap.get("sensors", []))
        self._sensor_count.labels(**nvr_labels).set(sensor_count)
        
        # Update storage metrics
        if nvr.storage and hasattr(nvr.storage, "stats"):
            for storage_device in nvr.storage.stats.devices:
                storage_labels = {
                    **nvr_labels,
                    MetricLabels.STORAGE_TYPE.value: storage_device.type or "unknown",
                    MetricLabels.STORAGE_PATH.value: storage_device.path or "/",
                }
                
                if storage_device.used is not None:
                    self._storage_used.labels(**storage_labels).set(storage_device.used)
                
                if storage_device.size is not None:
                    self._storage_total.labels(**storage_labels).set(storage_device.size)
                
                # Calculate percentage
                if storage_device.used is not None and storage_device.size is not None and storage_device.size > 0:
                    percentage = (storage_device.used / storage_device.size) * 100
                    self._storage_percentage.labels(**storage_labels).set(percentage)
        
        logger.debug(
            "Successfully collected system metrics",
            camera_count=camera_count,
            sensor_count=sensor_count,
            nvr_name=nvr.name,
        )