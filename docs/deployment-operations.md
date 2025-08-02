---
title: Deployment & Operations
description: Running the exporter in production
---

# Deployment & Operations

This exporter is distributed as a container image. The repository contains a [docker-compose.yml](https://github.com/rknightion/unifi-protect-exporter/blob/main/docker-compose.yml) with sane defaults. Adjust the environment variables in your `.env` file and start the stack:

```bash
docker compose up -d
```

## Health checks
- `/health` – basic liveness
- `/ready` – exporter has successfully connected to UniFi Protect

## Monitoring
Scrape `http://<host>:9099/metrics` with Prometheus. Example job:
```yaml
scrape_configs:
  - job_name: unifi_protect
    static_configs:
      - targets: ['unifi-protect-exporter:9099']
```

## Updating
Pull the latest image and restart the container:
```bash
docker compose pull
docker compose up -d
```

## Troubleshooting
- Check container logs with `docker compose logs unifi_protect_exporter`.
- Verify UniFi Protect credentials and network connectivity.
- Ensure the UniFi Protect NVR is accessible from the exporter.
- Metrics `unifi_protect_collector_errors_total` help identify failing collectors.

## Security Considerations
- Use a dedicated read-only user for the exporter if possible.
- Consider SSL certificate verification settings for self-signed certificates.
- Store credentials securely using environment variables or secrets management.

For configuration options see the [Configuration](config.md) guide. A list of
exported metrics is available in the [Metrics Reference](metrics/metrics.md).
