# Metrics Reference

This page provides a comprehensive reference of all Prometheus metrics exposed by the UniFi Protect Exporter.

!!! summary "Metrics Summary"
    📊 **Total Metrics:** TBD
    🏗️ **Collectors:** TBD
    📈 **Gauges:** TBD
    📊 **Counters:** TBD
    ℹ️ **Info Metrics:** TBD

## Overview

The exporter provides metrics across several categories:

| Collector | Metrics | Description |
|-----------|---------|-------------|
| SystemCollector | TBD | 🖥️ System-level metrics including NVR health and storage |
| CameraCollector | TBD | 📹 Camera status, recording state, and performance |
| MotionCollector | TBD | 🏃 Motion detection events and smart detections |
| RecordingCollector | TBD | 📼 Recording statistics and quality metrics |

## System Metrics

### unifi_protect_cameras_total
**Type:** Gauge  
**Description:** Total number of cameras connected to the UniFi Protect system  
**Labels:**
- `nvr_id`: NVR identifier
- `nvr_name`: NVR display name

**Example:**
```prometheus
unifi_protect_cameras_total{nvr_id="12345", nvr_name="Main NVR"} 8
```

### unifi_protect_storage_used_bytes
**Type:** Gauge  
**Description:** Storage space used in bytes  
**Labels:**
- `nvr_id`: NVR identifier
- `nvr_name`: NVR display name

### unifi_protect_storage_total_bytes
**Type:** Gauge  
**Description:** Total storage capacity in bytes  
**Labels:**
- `nvr_id`: NVR identifier
- `nvr_name`: NVR display name

### unifi_protect_system_info
**Type:** Info  
**Description:** UniFi Protect system information  
**Labels:**
- `nvr_id`: NVR identifier
- `nvr_name`: NVR display name
- `version`: UniFi Protect version
- `model`: NVR model

## Camera Metrics

### unifi_protect_camera_up
**Type:** Gauge  
**Description:** Camera online status (1 = online, 0 = offline)  
**Labels:**
- `camera_id`: Camera identifier
- `camera_name`: Camera display name
- `camera_model`: Camera model
- `nvr_id`: NVR identifier

**Example:**
```prometheus
unifi_protect_camera_up{camera_id="abc123", camera_name="Front Door", camera_model="G4 Pro", nvr_id="12345"} 1
```

### unifi_protect_camera_recording_enabled
**Type:** Gauge  
**Description:** Camera recording status (1 = enabled, 0 = disabled)  
**Labels:**
- `camera_id`: Camera identifier
- `camera_name`: Camera display name
- `camera_model`: Camera model

### unifi_protect_camera_storage_bytes
**Type:** Gauge  
**Description:** Storage used by camera recordings in bytes  
**Labels:**
- `camera_id`: Camera identifier
- `camera_name`: Camera display name

## Motion Event Metrics

### unifi_protect_motion_events_total
**Type:** Counter  
**Description:** Total number of motion events detected  
**Labels:**
- `camera_id`: Camera identifier
- `camera_name`: Camera display name
- `event_type`: Type of motion event (motion, person, vehicle, package)

**Example:**
```prometheus
unifi_protect_motion_events_total{camera_id="abc123", camera_name="Front Door", event_type="person"} 42
```

### unifi_protect_motion_events_duration_seconds
**Type:** Gauge  
**Description:** Duration of the last motion event in seconds  
**Labels:**
- `camera_id`: Camera identifier
- `camera_name`: Camera display name

## Recording Metrics

### unifi_protect_recording_duration_seconds
**Type:** Gauge  
**Description:** Total recording duration in seconds for the last 24 hours  
**Labels:**
- `camera_id`: Camera identifier
- `camera_name`: Camera display name

### unifi_protect_recording_gaps_total
**Type:** Counter  
**Description:** Total number of recording gaps/failures  
**Labels:**
- `camera_id`: Camera identifier
- `camera_name`: Camera display name

## Exporter Metrics

### unifi_protect_collector_duration_seconds
**Type:** Gauge  
**Description:** Time taken to collect metrics from each collector  
**Labels:**
- `collector`: Collector name

### unifi_protect_collector_errors_total
**Type:** Counter  
**Description:** Total number of collection errors  
**Labels:**
- `collector`: Collector name
- `error_type`: Type of error

### unifi_protect_collector_last_success_timestamp_seconds
**Type:** Gauge  
**Description:** Unix timestamp of the last successful collection  
**Labels:**
- `collector`: Collector name

## Query Examples

### Camera Availability
```promql
# Overall camera availability percentage
(sum(unifi_protect_camera_up) / count(unifi_protect_camera_up)) * 100

# Cameras offline for more than 5 minutes
unifi_protect_camera_up == 0
```

### Motion Detection
```promql
# Motion events per camera in the last hour
increase(unifi_protect_motion_events_total[1h])

# Person detection rate
rate(unifi_protect_motion_events_total{event_type="person"}[5m])
```

### Storage Usage
```promql
# Storage usage percentage
(unifi_protect_storage_used_bytes / unifi_protect_storage_total_bytes) * 100

# Storage usage per camera
topk(10, unifi_protect_camera_storage_bytes)
```

## Label Reference

### Common Labels
| Label | Description | Example Values |
|-------|-------------|----------------|
| `nvr_id` | NVR unique identifier | `12345678` |
| `nvr_name` | NVR display name | `Main NVR`, `Office NVR` |
| `camera_id` | Camera unique identifier | `abc123def456` |
| `camera_name` | Camera display name | `Front Door`, `Parking Lot` |
| `camera_model` | Camera model | `G4 Pro`, `G3 Flex`, `G4 Doorbell` |

### Event-Specific Labels
| Label | Description | Example Values |
|-------|-------------|----------------|
| `event_type` | Type of motion event | `motion`, `person`, `vehicle`, `package` |
| `collector` | Exporter collector name | `system`, `camera`, `motion` |
| `error_type` | Type of collection error | `api_error`, `timeout`, `parse_error` |

## Best Practices

1. **Use label matchers** to filter metrics efficiently
2. **Aggregate carefully** to avoid high cardinality issues
3. **Set up recording rules** for frequently used queries
4. **Monitor the exporter** using its self-reported metrics

For more information on using these metrics, see the [Integration & Dashboards](../integration-dashboards.md) guide.