---
title: Metrics Reference
description: Complete reference for all metrics collected by the UniFi Protect Exporter
tags:
  - prometheus
  - monitoring
  - metrics
---

# Metrics Reference

The UniFi Protect Exporter provides comprehensive metrics for monitoring your UniFi Protect infrastructure. This section contains detailed documentation about all available metrics, their collection tiers, and usage examples.

## Documentation Structure

<div class="grid cards" markdown>

- :material-chart-line-stacked: **[Metrics Overview](overview.md)**

    ---

    High-level overview of metric categories, collection tiers, and naming conventions

- :material-format-list-bulleted-square: **[Complete Reference](metrics.md)**

    ---

    Detailed reference of every metric with descriptions, labels, and examples

</div>

## Metric Categories

### System Metrics
- NVR status and health
- Storage utilization
- System resource usage
- Total camera counts

### Camera Metrics
- Camera online/offline status
- Recording status
- Video quality metrics
- Motion detection statistics

### Recording Metrics
- Recording duration and gaps
- Storage usage per camera
- Recording quality statistics

### Motion Event Metrics
- Motion events per camera
- Event duration and frequency
- Smart detection events (person, vehicle, etc.)

## Collection Tiers

The exporter uses a three-tier collection system:

| Tier | Interval | Metrics | Purpose |
|------|----------|---------|---------|
| **Fast** | 60 seconds | Motion events, camera status | Real-time monitoring |
| **Medium** | 5 minutes | Recording stats, camera metrics | Operational monitoring |
| **Slow** | 15 minutes | Configuration, system info | Change detection |

## Getting Started

1. **Browse the Overview**: Start with the [overview](overview.md) to understand the metric structure
2. **Find Specific Metrics**: Use the [complete reference](metrics.md) to find detailed information
3. **Use in Queries**: See examples in our [Integration & Dashboards](../integration-dashboards.md) guide

## Prometheus Query Examples

```promql
# Camera availability percentage
avg by (nvr_name) (unifi_protect_camera_up) * 100

# Top cameras by motion events
topk(5, sum by (camera_name) (rate(unifi_protect_motion_events_total[5m])))

# Storage usage percentage
(unifi_protect_storage_used_bytes / unifi_protect_storage_total_bytes) * 100
```

!!! tip "Performance Tips"
    - Use recording rules for frequently accessed metrics
    - Filter by camera or NVR early in queries
    - Consider metric cardinality when using high-cardinality labels
