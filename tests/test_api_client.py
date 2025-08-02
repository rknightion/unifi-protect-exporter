"""Tests for the AsyncUniFiProtectClient wrapper."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from pydantic import SecretStr
from uiprotect import ProtectApiClient
from uiprotect.data import Camera, NVR, Bootstrap

from unifi_protect_exporter.api.client import AsyncUniFiProtectClient
from unifi_protect_exporter.core.config import Settings


@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing."""
    settings = MagicMock()
    
    # Create nested mock objects
    settings.unifi = MagicMock()
    settings.unifi.host = "192.168.1.100"
    settings.unifi.port = 443
    settings.unifi.username = "testuser"
    settings.unifi.password = SecretStr("testpass123")
    settings.unifi.verify_ssl = False
    
    settings.api = MagicMock()
    settings.api.concurrency_limit = 5
    settings.api.timeout = 30
    settings.api.max_retries = 3
    
    return settings


@pytest.fixture
def mock_protect_api() -> Mock:
    """Create mock ProtectApiClient instance."""
    api = AsyncMock(spec=ProtectApiClient)
    
    # Mock bootstrap data
    bootstrap = MagicMock(spec=Bootstrap)
    bootstrap.nvr = MagicMock(spec=NVR)
    bootstrap.nvr.id = "nvr123"
    bootstrap.nvr.name = "Test NVR"
    bootstrap.nvr.version = "2.4.0"
    bootstrap.nvr.host = "192.168.1.100"
    bootstrap.nvr.platform = "linux"
    bootstrap.nvr.firmwareVersion = "2.4.0"
    bootstrap.nvr.uptime = 86400
    
    # Mock storage info
    storage_device = MagicMock()
    storage_device.type = "main"
    storage_device.path = "/volume1"
    storage_device.used = 1000000000
    storage_device.size = 2000000000
    
    storage_stats = MagicMock()
    storage_stats.devices = [storage_device]
    
    bootstrap.nvr.storage = MagicMock()
    bootstrap.nvr.storage.stats = storage_stats
    
    # Mock cameras
    camera1 = MagicMock(spec=Camera)
    camera1.id = "cam1"
    camera1.name = "Front Door"
    camera1.model = "G4 Pro"
    camera1.mac = "00:11:22:33:44:55"
    
    camera2 = MagicMock(spec=Camera)
    camera2.id = "cam2"
    camera2.name = "Garage"
    camera2.model = "G3 Flex"
    camera2.mac = "00:11:22:33:44:66"
    
    bootstrap.cameras = {"cam1": camera1, "cam2": camera2}
    bootstrap.sensors = {}
    
    api.bootstrap = bootstrap
    
    # Mock unifi_dict method
    def mock_unifi_dict():
        return {
            "nvr": {
                "id": bootstrap.nvr.id,
                "name": bootstrap.nvr.name,
                "version": bootstrap.nvr.version,
            },
            "cameras": [
                {"id": "cam1", "name": "Front Door"},
                {"id": "cam2", "name": "Garage"},
            ],
            "sensors": [],
        }
    
    bootstrap.unifi_dict = mock_unifi_dict
    
    # Mock connect method
    api.connect = AsyncMock()
    api.refresh = AsyncMock()
    api.close = AsyncMock()
    
    return api


class TestAsyncUniFiProtectClientInitialization:
    """Test client initialization and configuration."""
    
    def test_init_with_settings(self, mock_settings: Settings) -> None:
        """Test client initialization with settings."""
        client = AsyncUniFiProtectClient(mock_settings)
        
        assert client.settings == mock_settings
        assert client._client is None
        assert isinstance(client._semaphore, asyncio.Semaphore)
        assert isinstance(client._client_lock, asyncio.Lock)
        assert client._api_call_count == 0
        assert client._bootstrap_data is None


class TestClientConnection:
    """Test client connection management."""
    
    @pytest.mark.asyncio
    @patch("unifi_protect_exporter.api.client.ProtectApiClient")
    async def test_get_client_creates_connection(
        self,
        mock_protect_class: Mock,
        mock_settings: Settings,
        mock_protect_api: Mock,
    ) -> None:
        """Test that get_client creates and connects properly."""
        mock_protect_class.return_value = mock_protect_api
        
        client = AsyncUniFiProtectClient(mock_settings)
        
        async with client.get_client() as api:
            assert api == mock_protect_api
            
        # Verify initialization parameters
        mock_protect_class.assert_called_once_with(
            host="192.168.1.100",
            port=443,
            username="testuser",
            password="testpass123",
            verify_ssl=False,
            timeout=30,
        )
        
        # Verify connection was established
        mock_protect_api.connect.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("unifi_protect_exporter.api.client.ProtectApiClient")
    async def test_get_client_reuses_connection(
        self,
        mock_protect_class: Mock,
        mock_settings: Settings,
        mock_protect_api: Mock,
    ) -> None:
        """Test that get_client reuses existing connection."""
        mock_protect_class.return_value = mock_protect_api
        
        client = AsyncUniFiProtectClient(mock_settings)
        
        # First access
        async with client.get_client() as api1:
            assert api1 == mock_protect_api
            
        # Second access should reuse
        async with client.get_client() as api2:
            assert api2 == mock_protect_api
            
        # Should only create one client
        assert mock_protect_class.call_count == 1
        assert mock_protect_api.connect.call_count == 1


class TestDataRetrieval:
    """Test data retrieval methods."""
    
    @pytest.mark.asyncio
    @patch("unifi_protect_exporter.api.client.ProtectApiClient")
    async def test_get_bootstrap(
        self,
        mock_protect_class: Mock,
        mock_settings: Settings,
        mock_protect_api: Mock,
    ) -> None:
        """Test fetching bootstrap data."""
        mock_protect_class.return_value = mock_protect_api
        
        client = AsyncUniFiProtectClient(mock_settings)
        result = await client.get_bootstrap()
        
        assert result["nvr"]["id"] == "nvr123"
        assert result["nvr"]["name"] == "Test NVR"
        assert len(result["cameras"]) == 2
        assert len(result["sensors"]) == 0
        
        # Verify refresh was called
        mock_protect_api.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("unifi_protect_exporter.api.client.ProtectApiClient")
    async def test_get_cameras(
        self,
        mock_protect_class: Mock,
        mock_settings: Settings,
        mock_protect_api: Mock,
    ) -> None:
        """Test fetching cameras."""
        mock_protect_class.return_value = mock_protect_api
        
        client = AsyncUniFiProtectClient(mock_settings)
        cameras = await client.get_cameras()
        
        assert len(cameras) == 2
        assert cameras[0].name == "Front Door"
        assert cameras[1].name == "Garage"
    
    @pytest.mark.asyncio
    @patch("unifi_protect_exporter.api.client.ProtectApiClient")
    async def test_get_nvr(
        self,
        mock_protect_class: Mock,
        mock_settings: Settings,
        mock_protect_api: Mock,
    ) -> None:
        """Test fetching NVR information."""
        mock_protect_class.return_value = mock_protect_api
        
        client = AsyncUniFiProtectClient(mock_settings)
        nvr = await client.get_nvr()
        
        assert nvr.id == "nvr123"
        assert nvr.name == "Test NVR"
        assert nvr.version == "2.4.0"
    
    @pytest.mark.asyncio
    @patch("unifi_protect_exporter.api.client.ProtectApiClient")
    async def test_get_camera_count(
        self,
        mock_protect_class: Mock,
        mock_settings: Settings,
        mock_protect_api: Mock,
    ) -> None:
        """Test getting camera count."""
        mock_protect_class.return_value = mock_protect_api
        
        client = AsyncUniFiProtectClient(mock_settings)
        count = await client.get_camera_count()
        
        assert count == 2


class TestConcurrencyControl:
    """Test concurrency limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrent_requests(
        self,
        mock_settings: Settings,
    ) -> None:
        """Test that semaphore properly limits concurrent requests."""
        mock_settings.api.concurrency_limit = 2
        client = AsyncUniFiProtectClient(mock_settings)
        
        # Track concurrent executions
        concurrent_count = 0
        max_concurrent = 0
        
        async def slow_operation():
            nonlocal concurrent_count, max_concurrent
            concurrent_count += 1
            max_concurrent = max(max_concurrent, concurrent_count)
            await asyncio.sleep(0.1)
            concurrent_count -= 1
            return {"nvr": {}, "cameras": [], "sensors": []}
        
        with patch.object(client, "_client") as mock_client:
            mock_client.refresh = slow_operation
            mock_client.bootstrap = MagicMock()
            mock_client.bootstrap.unifi_dict.return_value = {"nvr": {}, "cameras": [], "sensors": []}
            
            # Launch multiple concurrent requests
            tasks = [
                client.get_bootstrap(),
                client.get_bootstrap(),
                client.get_bootstrap(),
                client.get_bootstrap(),
            ]
            
            await asyncio.gather(*tasks)
        
        # Should respect concurrency limit
        assert max_concurrent <= 2


class TestClientLifecycle:
    """Test client lifecycle management."""
    
    @pytest.mark.asyncio
    @patch("unifi_protect_exporter.api.client.ProtectApiClient")
    async def test_close_client(
        self,
        mock_protect_class: Mock,
        mock_settings: Settings,
        mock_protect_api: Mock,
    ) -> None:
        """Test closing the client."""
        mock_protect_class.return_value = mock_protect_api
        
        client = AsyncUniFiProtectClient(mock_settings)
        
        # Force client creation
        async with client.get_client():
            pass
        
        assert client._client is not None
        
        # Close should clear the client instance
        await client.close()
        assert client._client is None
        assert client._bootstrap_data is None
        
        # Verify close was called on the API
        mock_protect_api.close.assert_called_once()


class TestApiCallTracking:
    """Test API call tracking."""
    
    def test_track_api_call(self, mock_settings: Settings) -> None:
        """Test API call counting."""
        client = AsyncUniFiProtectClient(mock_settings)
        
        assert client.api_call_count == 0
        
        client.track_api_call()
        assert client.api_call_count == 1
        
        client.track_api_call()
        assert client.api_call_count == 2


class TestTracing:
    """Test OpenTelemetry tracing integration."""
    
    @pytest.mark.asyncio
    @patch("unifi_protect_exporter.api.client.tracer")
    @patch("unifi_protect_exporter.api.client.ProtectApiClient")
    async def test_tracing_spans(
        self,
        mock_protect_class: Mock,
        mock_tracer: Mock,
        mock_settings: Settings,
        mock_protect_api: Mock,
    ) -> None:
        """Test that operations create proper tracing spans."""
        mock_protect_class.return_value = mock_protect_api
        mock_span = MagicMock()
        mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span
        
        client = AsyncUniFiProtectClient(mock_settings)
        
        # Test get_bootstrap span
        await client.get_bootstrap()
        mock_tracer.start_as_current_span.assert_any_call("get_bootstrap")
        
        # Test get_cameras span
        await client.get_cameras()
        mock_tracer.start_as_current_span.assert_any_call("get_cameras")
        
        # Test get_nvr span
        await client.get_nvr()
        mock_tracer.start_as_current_span.assert_any_call("get_nvr")
        
        # Verify attributes were set
        assert mock_span.set_attribute.call_count > 0