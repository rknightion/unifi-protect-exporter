"""Metric name and label constants for UniFi Protect exporter."""

from __future__ import annotations

from enum import Enum


class MetricNames(str, Enum):
    """Standardized metric names for UniFi Protect exporter."""

    # System metrics
    SYSTEM_INFO = "system_info"
    NVR_UPTIME_SECONDS = "nvr_uptime_seconds"
    CAMERA_COUNT = "camera_count"
    SENSOR_COUNT = "sensor_count"
    
    # Storage metrics
    STORAGE_USED_BYTES = "storage_used_bytes"
    STORAGE_TOTAL_BYTES = "storage_total_bytes"
    STORAGE_USED_PERCENTAGE = "storage_used_percentage"
    RECORDING_RETENTION_DAYS = "recording_retention_days"
    
    # Camera metrics
    CAMERA_INFO = "camera_info"
    CAMERA_ONLINE = "camera_online"
    CAMERA_CONNECTED = "camera_connected"
    CAMERA_RECORDING = "camera_recording"
    CAMERA_MOTION_DETECTED = "camera_motion_detected"
    CAMERA_FPS = "camera_fps"
    CAMERA_BITRATE_BPS = "camera_bitrate_bps"
    CAMERA_UPTIME_SECONDS = "camera_uptime_seconds"
    CAMERA_LAST_SEEN_SECONDS = "camera_last_seen_seconds"
    CAMERA_LAST_MOTION_SECONDS = "camera_last_motion_seconds"
    CAMERA_MOTION_EVENTS_TOTAL = "camera_motion_events_total"
    CAMERA_RECORDING_EVENTS_TOTAL = "camera_recording_events_total"
    
    # Network metrics
    CAMERA_RX_BYTES_TOTAL = "camera_rx_bytes_total"
    CAMERA_TX_BYTES_TOTAL = "camera_tx_bytes_total"
    CAMERA_RX_PACKETS_TOTAL = "camera_rx_packets_total"
    CAMERA_TX_PACKETS_TOTAL = "camera_tx_packets_total"
    CAMERA_RX_DROPPED_TOTAL = "camera_rx_dropped_total"
    CAMERA_TX_DROPPED_TOTAL = "camera_tx_dropped_total"
    CAMERA_RX_ERRORS_TOTAL = "camera_rx_errors_total"
    CAMERA_TX_ERRORS_TOTAL = "camera_tx_errors_total"
    
    # Sensor metrics
    SENSOR_INFO = "sensor_info"
    SENSOR_ONLINE = "sensor_online"
    SENSOR_BATTERY_PERCENTAGE = "sensor_battery_percentage"
    SENSOR_TEMPERATURE_CELSIUS = "sensor_temperature_celsius"
    SENSOR_HUMIDITY_PERCENTAGE = "sensor_humidity_percentage"
    SENSOR_LIGHT_LEVEL = "sensor_light_level"
    SENSOR_MOTION_DETECTED = "sensor_motion_detected"
    SENSOR_DOOR_OPEN = "sensor_door_open"
    SENSOR_WATER_DETECTED = "sensor_water_detected"
    SENSOR_LAST_SEEN_SECONDS = "sensor_last_seen_seconds"
    
    # Event metrics
    EVENT_COUNT_TOTAL = "event_count_total"
    EVENT_DURATION_SECONDS = "event_duration_seconds"
    
    # Collector metrics
    COLLECTOR_DURATION_SECONDS = "collector_duration_seconds"
    COLLECTOR_ERRORS_TOTAL = "collector_errors_total"
    COLLECTOR_LAST_UPDATE_SECONDS = "collector_last_update_seconds"
    
    # API metrics
    API_REQUESTS_TOTAL = "api_requests_total"
    API_REQUEST_DURATION_SECONDS = "api_request_duration_seconds"
    API_RATE_LIMIT_REMAINING = "api_rate_limit_remaining"
    
    # Exporter metrics
    EXPORTER_BUILD_INFO = "exporter_build_info"
    EXPORTER_UP = "exporter_up"
    EXPORTER_SCRAPE_DURATION_SECONDS = "exporter_scrape_duration_seconds"
    EXPORTER_SCRAPE_ERRORS_TOTAL = "exporter_scrape_errors_total"


class MetricLabels(str, Enum):
    """Standardized metric labels for UniFi Protect exporter."""

    # Common labels
    NVR_ID = "nvr_id"
    NVR_NAME = "nvr_name"
    NVR_VERSION = "nvr_version"
    
    # Camera labels
    CAMERA_ID = "camera_id"
    CAMERA_NAME = "camera_name"
    CAMERA_TYPE = "camera_type"
    CAMERA_MODEL = "camera_model"
    CAMERA_FIRMWARE = "camera_firmware"
    CAMERA_MAC = "camera_mac"
    CAMERA_IP = "camera_ip"
    
    # Sensor labels
    SENSOR_ID = "sensor_id"
    SENSOR_NAME = "sensor_name"
    SENSOR_TYPE = "sensor_type"
    SENSOR_MODEL = "sensor_model"
    SENSOR_FIRMWARE = "sensor_firmware"
    SENSOR_MAC = "sensor_mac"
    
    # Event labels
    EVENT_TYPE = "event_type"
    EVENT_SCORE = "event_score"
    
    # Storage labels
    STORAGE_TYPE = "storage_type"
    STORAGE_PATH = "storage_path"
    
    # Collector labels
    COLLECTOR = "collector"
    ERROR_CATEGORY = "error_category"
    
    # API labels
    ENDPOINT = "endpoint"
    STATUS = "status"
    METHOD = "method"
    
    # Exporter labels
    VERSION = "version"
    BUILD_DATE = "build_date"


class EventTypes(str, Enum):
    """Event type constants."""

    MOTION = "motion"
    PERSON = "person"
    VEHICLE = "vehicle"
    PACKAGE = "package"
    ANIMAL = "animal"
    DOORBELL = "doorbell"
    SMART_DETECT = "smart_detect"
    RECORDING = "recording"
    RING = "ring"


class CameraTypes(str, Enum):
    """Camera type constants."""

    BULLET = "bullet"
    DOME = "dome"
    PTZ = "ptz"
    DOORBELL = "doorbell"
    INSTANT = "instant"
    FLEX = "flex"


class SensorTypes(str, Enum):
    """Sensor type constants."""

    MOTION = "motion"
    DOOR = "door"
    WINDOW = "window"
    WATER = "water"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    LIGHT = "light"