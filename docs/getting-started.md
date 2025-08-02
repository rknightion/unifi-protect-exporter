---
title: Getting Started
description: Install and run the exporter
---

# Getting Started

This section shows the quickest way to run the exporter.

## Requirements
- Docker or Python 3.13+
- UniFi Protect NVR with API access
- Username and password for UniFi Protect

## Setup

1. Copy `.env.example` to `.env` and set your UniFi Protect credentials:
   - `UNIFI_PROTECT_HOST`: Your UniFi Protect NVR IP/hostname
   - `UNIFI_PROTECT_USERNAME`: UniFi Protect username
   - `UNIFI_PROTECT_PASSWORD`: UniFi Protect password
2. Start the container with `docker compose up -d`. You can review the [docker-compose.yml](https://github.com/rknightion/unifi-protect-exporter/blob/main/docker-compose.yml) for optional settings.

Alternatively install with Python:
```bash
uv pip install unifi-protect-exporter
export UNIFI_PROTECT_HOST=your_nvr_host
export UNIFI_PROTECT_USERNAME=your_username
export UNIFI_PROTECT_PASSWORD=your_password
python -m unifi_protect_exporter
```

## Verify
- Visit `http://localhost:9099/metrics` to see metrics.
- `curl http://localhost:9099/health` should return `{"status": "healthy"}`.

Next read the [Configuration](config.md) guide for all settings and the
[Metrics Reference](metrics/metrics.md) for available metrics.
