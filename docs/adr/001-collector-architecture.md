# ADR-001: Collector Architecture

**Status**: Accepted
**Date**: 2024-01-15
**Decision Makers**: Development Team

## Context

The UniFi Protect Exporter needs to collect metrics from various UniFi Protect API endpoints at different intervals while managing API connections, handling errors gracefully, and maintaining good performance.

## Decision

We will use a hierarchical collector architecture with the following key patterns:

### 1. Three-Tier Update System
- **FAST** (60s): Real-time metrics like motion events and camera status
- **MEDIUM** (300s): Operational metrics like recording statistics and camera health
- **SLOW** (900s): Configuration and slowly-changing data

### 2. Collector Hierarchy
```
CollectorManager
├── Main Collectors (auto-registered via @register_collector)
│   ├── SystemCollector
│   │   └── Sub-collectors (manually registered)
│   │       ├── StorageCollector
│   │       ├── ResourceCollector
│   │       └── ConfigCollector
│   ├── CameraCollector
│   │   └── Camera Type Collectors
│   │       ├── G4ProCollector
│   │       ├── G3FlexCollector
│   │       └── (others)
│   └── MotionCollector
│       └── Event Sub-collectors
│           ├── SmartDetectionCollector
│           └── ZoneCollector
```

### 3. Metric Ownership Pattern
Each collector owns its specific metrics:
- Main collectors own shared metrics
- Sub-collectors own type-specific metrics
- Metrics are initialized in `_initialize_metrics()` method

### 4. Registration Pattern
Main collectors use decorator-based auto-registration:
```python
@register_collector(UpdateTier.MEDIUM)
class MyCollector(MetricCollector):
    pass
```

## Consequences

### Positive
- Clear separation of concerns
- Easy to add new collectors
- Metrics are organized by ownership
- Update intervals align with API characteristics
- Reduced code duplication

### Negative
- More complex initialization flow
- Sub-collectors require manual registration
- Potential for metric naming conflicts

## Alternatives Considered

1. **Flat collector structure**: Simpler but would lead to massive files
2. **Single update interval**: Simpler but inefficient API usage
3. **Dynamic metric creation**: More flexible but harder to track metrics

## Implementation Notes

- Use `BaseDeviceCollector` for common device functionality
- Always call parent's `_initialize_metrics()` when extending
- Track API calls via `_track_api_call()` for monitoring
- Use error categories for proper error tracking
