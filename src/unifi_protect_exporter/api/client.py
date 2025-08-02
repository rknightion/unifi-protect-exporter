"""UniFi Protect API client wrapper with async support."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

from opentelemetry import trace
from uiprotect import ProtectApiClient
from uiprotect.data import Camera, NVR

from ..core.logging import get_logger

if TYPE_CHECKING:
    from ..core.config import Settings

logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)


class AsyncUniFiProtectClient:
    """Async wrapper for the UniFi Protect API client.

    Parameters
    ----------
    settings : Settings
        Application settings containing API configuration.

    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the async UniFi Protect client with settings."""
        self.settings = settings
        self._client: ProtectApiClient | None = None
        self._semaphore = asyncio.Semaphore(settings.api.concurrency_limit)
        self._client_lock = asyncio.Lock()
        self._api_call_count = 0
        self._bootstrap_data: dict[str, Any] | None = None
        
        logger.debug(
            "Initialized AsyncUniFiProtectClient",
            host=settings.unifi.host,
            concurrency_limit=settings.api.concurrency_limit,
            api_timeout=settings.api.timeout,
            verify_ssl=settings.unifi.verify_ssl,
        )

    @asynccontextmanager
    async def get_client(self) -> AsyncIterator[ProtectApiClient]:
        """Get or create the API client instance with proper lifecycle management.

        Yields
        ------
        ProtectApiClient
            The UniFi Protect API client.

        """
        async with self._client_lock:
            if self._client is None:
                logger.debug(
                    "Creating new UniFi Protect API client",
                    host=self.settings.unifi.host,
                    port=self.settings.unifi.port,
                    verify_ssl=self.settings.unifi.verify_ssl,
                )
                
                self._client = ProtectApiClient(
                    host=self.settings.unifi.host,
                    port=self.settings.unifi.port,
                    username=self.settings.unifi.username,
                    password=self.settings.unifi.password.get_secret_value(),
                    verify_ssl=self.settings.unifi.verify_ssl,
                    timeout=self.settings.api.timeout,
                )
                
                # Authenticate and get initial data
                await self._client.connect()
                logger.info(
                    "Successfully connected to UniFi Protect",
                    host=self.settings.unifi.host,
                    nvr_name=self._client.bootstrap.nvr.name,
                    version=self._client.bootstrap.nvr.version,
                )
                
        yield self._client

    async def get_bootstrap(self) -> dict[str, Any]:
        """Get bootstrap data with caching.

        Returns
        -------
        dict[str, Any]
            Bootstrap data containing system information.

        """
        with tracer.start_as_current_span("get_bootstrap") as span:
            logger.debug("Fetching bootstrap data")
            span.set_attribute("api.endpoint", "getBootstrap")
            
            async with self._semaphore:
                async with self.get_client() as client:
                    # Force refresh of bootstrap data
                    await client.refresh()
                    self._bootstrap_data = client.bootstrap.unifi_dict()
                    
            if self._bootstrap_data:
                span.set_attribute("nvr.id", self._bootstrap_data.get("nvr", {}).get("id", ""))
                span.set_attribute("camera.count", len(self._bootstrap_data.get("cameras", [])))
                
            logger.debug(
                "Successfully fetched bootstrap data",
                nvr_name=self._bootstrap_data.get("nvr", {}).get("name", "Unknown"),
                camera_count=len(self._bootstrap_data.get("cameras", [])),
            )
            
            return self._bootstrap_data

    async def get_cameras(self) -> list[Camera]:
        """Fetch all cameras.

        Returns
        -------
        list[Camera]
            List of camera objects.

        """
        with tracer.start_as_current_span("get_cameras") as span:
            logger.debug("Fetching all cameras")
            span.set_attribute("api.endpoint", "getCameras")
            
            async with self._semaphore:
                async with self.get_client() as client:
                    cameras = list(client.bootstrap.cameras.values())
                    
            logger.debug("Successfully fetched cameras", count=len(cameras))
            span.set_attribute("camera.count", len(cameras))
            
            return cameras

    async def get_nvr(self) -> NVR:
        """Get NVR information.

        Returns
        -------
        NVR
            NVR object with system information.

        """
        with tracer.start_as_current_span("get_nvr") as span:
            logger.debug("Fetching NVR information")
            span.set_attribute("api.endpoint", "getNVR")
            
            async with self._semaphore:
                async with self.get_client() as client:
                    nvr = client.bootstrap.nvr
                    
            logger.debug(
                "Successfully fetched NVR info",
                nvr_name=nvr.name,
                version=nvr.version,
            )
            span.set_attribute("nvr.id", nvr.id)
            span.set_attribute("nvr.name", nvr.name)
            
            return nvr

    async def get_camera_count(self) -> int:
        """Get total number of cameras.

        Returns
        -------
        int
            Total number of cameras in the system.

        """
        cameras = await self.get_cameras()
        return len(cameras)

    async def close(self) -> None:
        """Close the API client connection."""
        if self._client:
            logger.debug("Closing UniFi Protect API client")
            await self._client.close()
            self._client = None
            self._bootstrap_data = None

    def track_api_call(self) -> None:
        """Track an API call for monitoring purposes."""
        self._api_call_count += 1

    @property
    def api_call_count(self) -> int:
        """Get the total number of API calls made.

        Returns
        -------
        int
            Total API call count.

        """
        return self._api_call_count