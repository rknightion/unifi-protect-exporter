---
title: Extending Collectors
description: How to add new metric collectors
---

# Extending the Collector System

Collectors gather metrics from the UniFi Protect API. New collectors live in `src/unifi_protect_exporter/collectors/`.

## Basic steps
1. Create a new module under `collectors/`.
2. Define a class inheriting from `MetricCollector` and decorate it with `@register_collector(UpdateTier.X)`.
3. Implement `_initialize_metrics()` to create Prometheus metrics.
4. Implement `_collect_impl()` with your collection logic.
5. Add metric names to `core/constants/metrics_constants.py`.

```python
@register_collector(UpdateTier.MEDIUM)
class CameraCollector(MetricCollector):
    def _initialize_metrics(self) -> None:
        self._camera_status = self._create_gauge(
            MetricName.CAMERA_STATUS, 
            "Camera online status (1 = online, 0 = offline)"
        )

    async def _collect_impl(self) -> None:
        protect_api = await self.api.get_protect_client()
        cameras = await protect_api.get_cameras()
        
        for camera in cameras:
            labels = {
                "camera_id": camera.id,
                "camera_name": camera.name,
                "camera_model": camera.model
            }
            self._camera_status.labels(**labels).set(
                1 if camera.is_connected else 0
            )
```

## Update Tiers
- **FAST (60s)**: Real-time metrics (motion events, status changes)
- **MEDIUM (300s)**: Regular metrics (camera stats, recording info)
- **SLOW (900s)**: Configuration data (system info, device details)

## Testing
Use the helpers under `tests/` to build unit tests. Run them with:
```bash
uv run pytest
```

See [CLAUDE.md](../CLAUDE.md) for development conventions.
