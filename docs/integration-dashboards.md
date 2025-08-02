---
title: Integration & Dashboards
description: Connect the exporter to Prometheus and Grafana
---

# Integration & Dashboards

The exporter exposes metrics on `http://<host>:9099/metrics`. Scrape this endpoint with Prometheus or any other OpenMetrics compatible collector.

## Prometheus example
```yaml
scrape_configs:
  - job_name: unifi_protect
    static_configs:
      - targets: ['unifi-protect-exporter:9099']
```

## Grafana Alloy example
```alloy
discovery.relabel "unifi_protect" {
  targets = [{"__address__" = "unifi-protect-exporter:9099"}]
}

prometheus.scrape "unifi_protect" {
  targets    = discovery.relabel.unifi_protect.output
  forward_to = [prometheus.remote_write.default.receiver]
  scrape_interval = "30s"
  scrape_timeout  = "25s"
}

prometheus.remote_write "default" {
  endpoint { url = "http://prometheus:9090/api/v1/write" }
}
```

Prometheus and Grafana configuration examples are available in the [docker-compose.yml](https://github.com/rknightion/unifi-protect-exporter/blob/main/docker-compose.yml).

## Dashboards
Pre-built Grafana dashboards can be found in the [dashboards directory](https://github.com/rknightion/unifi-protect-exporter/tree/main/dashboards). Import them to get instant visibility into your UniFi Protect system.

## Alerting
Use PromQL rules with metrics such as `unifi_protect_camera_up` or `unifi_protect_collector_errors_total` to trigger alerts.

Example alert rules:
```yaml
groups:
  - name: unifi_protect_alerts
    rules:
      - alert: CameraOffline
        expr: unifi_protect_camera_up == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Camera {{ $labels.camera_name }} is offline"
```

For more metrics see the [Metrics Reference](metrics/metrics.md).
Configuration options are documented in the [Configuration](config.md) guide.
