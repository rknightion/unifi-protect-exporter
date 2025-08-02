<system_context>
UniFi Protect Exporter Test Suite - Comprehensive testing infrastructure with factories, mocks, and assertions for validating collector behavior, API interactions, and metric generation.
</system_context>

<critical_notes>
- **Inherit from BaseCollectorTest** for automatic fixture setup
- **Use test factories** from `helpers/factories.py` for consistent test data
- **Mock with MockAPIBuilder** for cleaner API response mocking
- **Assert metrics** with MetricAssertions for clear verification
- **Test error scenarios** with `.with_error()` method on mocks
</critical_notes>

<file_map>
## TEST ORGANIZATION
- `conftest.py` - Pytest configuration and shared fixtures
- `helpers/` - Test utilities and support classes
  - `factories.py` - Data factories for creating realistic test data
  - `mock_api.py` - MockAPIBuilder for API response mocking
  - `metrics.py` - MetricAssertions for metric validation
  - `base.py` - BaseCollectorTest with common test patterns
- `unit/` - Unit tests for individual components
- `integration/` - Integration tests for end-to-end scenarios
- `test_config.py` - Configuration and environment testing
</file_map>

<paved_path>
## BASE TEST PATTERN
```python
from tests.helpers.base import BaseCollectorTest
from tests.helpers.factories import CameraFactory, NVRFactory
from tests.helpers.mock_api import MockAPIBuilder

class TestMyCollector(BaseCollectorTest):
    """Test MyCollector with standard patterns"""

    async def test_collector_basic_operation(self, collector, mock_api_builder, metrics):
        # Setup test data with factories
        nvr = NVRFactory.create()
        cameras = CameraFactory.create_many(3, model="G4 Pro")

        # Configure API mocks
        mock_api_builder.with_nvr(nvr).with_cameras(cameras)

        # Run collector
        await self.run_collector(collector)

        # Assert metrics were created
        metrics.assert_gauge_exists("unifi_protect_camera_online")
        metrics.assert_gauge_value("unifi_protect_camera_online", 1, camera_id=cameras[0]["id"])
```

## ERROR TESTING PATTERN
```python
async def test_collector_api_error_handling(self, collector, mock_api_builder, metrics):
    # Setup error scenario
    nvr = NVRFactory.create()
    mock_api_builder.with_nvr(nvr).with_error(
        "getCameras",
        exception_type="APIError",
        message="Connection timeout"
    )

    # Run collector - should handle error gracefully
    await self.run_collector(collector)

    # Verify error handling
    metrics.assert_no_gauge_exists("unifi_protect_camera_online")
```
</paved_path>

<patterns>
## TESTING STRATEGIES

### Data Factory Usage
```python
# Create single realistic camera
camera = CameraFactory.create(
    id="cam123",
    model="G4 Pro",
    name="Front Door"
)

# Create multiple cameras with variations
cameras = CameraFactory.create_many(5, model="G3 Flex")

# Create NVR with specific attributes
nvr = NVRFactory.create(
    id="nvr123",
    name="Test NVR",
    version="2.4.0"
)
```

### API Mock Configuration
```python
# Basic mock setup
mock_api_builder.with_nvr(nvr).with_cameras(cameras)

# Add specific API responses
mock_api_builder.with_custom_response(
    "getMotionEvents",
    [{"id": "event123", "camera": "cam123", "score": 95}]
)

# Configure error scenarios
mock_api_builder.with_error(
    "getCameras",
    exception_type="ConnectionError"
)
```

### Metric Assertions
```python
# Check metric exists
metrics.assert_gauge_exists("unifi_protect_camera_online")

# Check specific metric value
metrics.assert_gauge_value("unifi_protect_camera_online", 1, nvr_id="nvr123", camera_id="cam123")

# Check metric does not exist
metrics.assert_no_gauge_exists("invalid_metric")

# Check metric with partial labels
metrics.assert_gauge_value("unifi_protect_camera_fps", 30.0, camera_id="cam123")
```
</patterns>

<examples>
## Complete Test Class Example
```python
import pytest
from tests.helpers.base import BaseCollectorTest
from tests.helpers.factories import CameraFactory, NVRFactory
from tests.helpers.mock_api import MockAPIBuilder
from src.unifi_protect_exporter.collectors.cameras import CameraCollector

class TestCameraCollector(BaseCollectorTest):
    """Test Camera metrics collector"""

    @pytest.fixture
    def collector_class(self):
        return CameraCollector

    async def test_camera_metrics_collection(self, collector, mock_api_builder, metrics):
        """Test collection of camera status metrics"""
        # Setup test data
        nvr = NVRFactory.create(id="nvr123")
        cameras = CameraFactory.create_many(2, [
            {"id": "cam1", "name": "Front Door", "model": "G4 Pro", "state": "CONNECTED"},
            {"id": "cam2", "name": "Garage", "model": "G3 Flex", "state": "DISCONNECTED"}
        ])

        # Configure mocks
        mock_api_builder.with_nvr(nvr).with_cameras(cameras)

        # Run collector
        await self.run_collector(collector)

        # Assert metrics were created correctly
        metrics.assert_gauge_exists("unifi_protect_camera_online")

        # Check specific values
        metrics.assert_gauge_value(
            "unifi_protect_camera_online",
            1,
            nvr_id="nvr123",
            camera_id="cam1",
            camera_name="Front Door"
        )

        metrics.assert_gauge_value(
            "unifi_protect_camera_online",
            0,
            nvr_id="nvr123",
            camera_id="cam2",
            camera_name="Garage"
        )

    async def test_api_error_handling(self, collector, mock_api_builder, metrics):
        """Test graceful handling of API errors"""
        nvr = NVRFactory.create()

        # Configure API to return error
        mock_api_builder.with_nvr(nvr).with_error(
            "getCameras",
            exception_type="APIError",
            message="Connection timeout"
        )

        # Collector should handle error gracefully
        await self.run_collector(collector)

        # No metrics should be created on error
        metrics.assert_no_gauge_exists("unifi_protect_camera_online")

    async def test_empty_camera_list(self, collector, mock_api_builder, metrics):
        """Test behavior with no cameras"""
        nvr = NVRFactory.create()

        # No cameras returned
        mock_api_builder.with_nvr(nvr).with_cameras([])

        # Should complete without error
        await self.run_collector(collector)

        # No camera metrics should be created
        metrics.assert_no_gauge_exists("unifi_protect_camera_online")
```

## Factory Usage Example
```python
# Create realistic motion event data
motion_event = MotionEventFactory.create(
    id="event123",
    camera="cam123",
    score=95,
    timestamp="2024-01-15T10:30:00Z"
)

# Create multiple NVRs for multi-NVR testing
nvrs = NVRFactory.create_many(3)

# Create cameras with specific attributes
cameras = CameraFactory.create_many(
    5,
    state="CONNECTED",
    is_recording=True
)
```
</examples>

<workflow>
## WRITING NEW TESTS
1. **Inherit from BaseCollectorTest**: Provides fixtures and common patterns
2. **Use appropriate factory**: Create realistic test data with factories
3. **Mock API responses**: Use MockAPIBuilder for clean API mocking
4. **Test positive path**: Verify normal operation with expected metrics
5. **Test error scenarios**: Use `.with_error()` to test error handling
6. **Test edge cases**: Empty data, malformed responses, etc.
7. **Assert metrics**: Use MetricAssertions for clear metric validation
8. **Test isolation**: Ensure tests don't interfere with each other
</workflow>

<common_tasks>
## DEBUGGING FAILED TESTS
1. **Check factory data**: Verify test data matches expectations
2. **Inspect API mocks**: Ensure mocks return expected data format
3. **Review metric assertions**: Check label names and values match exactly
4. **Add debug logging**: Use `pytest -s` to see log output
5. **Isolate test**: Run single test to eliminate interference
6. **Check fixtures**: Verify collector and mock setup is correct
</common_tasks>

<api_quirks>
## TESTING API SPECIFIC BEHAVIORS
- **Mock bootstrap data**: UniFi Protect uses bootstrap for initial data
- **Response formats**: Test both direct API responses and bootstrap data
- **Error scenarios**: Mock connection errors, authentication failures
- **WebSocket events**: Test real-time event processing (future)
- **SSL verification**: Test both verified and unverified connections
</api_quirks>

<fatal_implications>
- **NEVER use real UniFi credentials** in tests - always use mocks
- **NEVER test against live NVR** - use MockAPIBuilder exclusively
- **NEVER skip error testing** - API failures are common
- **NEVER assume test isolation** - use proper setup/teardown
- **NEVER hardcode test data** - use factories for consistency
</fatal_implications>