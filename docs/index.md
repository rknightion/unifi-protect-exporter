---
title: UniFi Protect Exporter
description: High level overview and quick links
---

# UniFi Protect Exporter

A lightweight Prometheus exporter for UniFi Protect systems. It collects metrics from UniFi Protect NVRs, cameras, and sensors, with support for forwarding data via OpenTelemetry.

## Quick start

### Docker
1. Copy `.env.example` to `.env` and set your UniFi Protect credentials.
2. Run `docker compose up -d` using the [provided compose file](https://github.com/rknightion/unifi-protect-exporter/blob/main/docker-compose.yml).

### Python
1. `uv pip install unifi-protect-exporter`
2. Set UniFi Protect environment variables
3. `python -m unifi_protect_exporter`

## Learn more
- [Getting Started](getting-started.md)
- [Configuration](config.md)
- [Deployment & Operations](deployment-operations.md)
- [Integration & Dashboards](integration-dashboards.md)
 - [Metrics Reference](metrics/index.md)
