# UniFi Protect Exporter
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Frknightion%2Funifi-protect-exporter.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Frknightion%2Funifi-protect-exporter?ref=badge_shield)


A Prometheus exporter for UniFi Protect metrics with OpenTelemetry support.

## Features

- Collects metrics from UniFi Protect NVRs, cameras, and sensors
- Camera status and recording metrics
- Motion detection event tracking
- Storage utilization monitoring
- Async collection for improved performance
- **Dual metric export**: Prometheus `/metrics` endpoint + automatic OpenTelemetry export
- **Distributed tracing**: Full request tracing with OpenTelemetry instrumentation
- Structured logging with JSON output and trace correlation
- Docker support with health checks
- Configurable collection intervals

## Quick Start

### Using Docker

1. Copy `.env.example` to `.env` and configure your UniFi Protect credentials:
   ```bash
   cp .env.example .env
   # Edit .env and set:
   # UNIFI_PROTECT_EXPORTER_UNIFI__HOST=your_nvr_ip
   # UNIFI_PROTECT_EXPORTER_UNIFI__USERNAME=your_username
   # UNIFI_PROTECT_EXPORTER_UNIFI__PASSWORD=your_password
   ```

2. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Access metrics at http://localhost:9099/metrics

### Using Python

1. Install dependencies:
   ```bash
   uv pip install -e .
   ```

2. Set environment variables:
   ```bash
   export UNIFI_PROTECT_EXPORTER_UNIFI__HOST=your_nvr_ip
   export UNIFI_PROTECT_EXPORTER_UNIFI__USERNAME=your_username
   export UNIFI_PROTECT_EXPORTER_UNIFI__PASSWORD=your_password
   ```

3. Run the exporter:
   ```bash
   python -m unifi_protect_exporter
   ```

## Configuration

### Environment Variables

All configuration is done via environment variables with the prefix `UNIFI_PROTECT_EXPORTER_`.

#### Required Settings

- `UNIFI_PROTECT_EXPORTER_UNIFI__HOST`: UniFi Protect NVR IP address or hostname
- `UNIFI_PROTECT_EXPORTER_UNIFI__USERNAME`: UniFi Protect username
- `UNIFI_PROTECT_EXPORTER_UNIFI__PASSWORD`: UniFi Protect password

#### Optional Settings

- `UNIFI_PROTECT_EXPORTER_UNIFI__PORT`: UniFi Protect API port (default: 443)
- `UNIFI_PROTECT_EXPORTER_UNIFI__VERIFY_SSL`: Verify SSL certificates (default: false)
- `UNIFI_PROTECT_EXPORTER_SERVER__PORT`: Exporter HTTP port (default: 9099)
- `UNIFI_PROTECT_EXPORTER_LOGGING__LEVEL`: Log level (default: INFO)

See [docs/config.md](docs/config.md) for full configuration reference.

## Metrics

The exporter provides metrics for:

- **System**: NVR health, storage usage, camera counts
- **Cameras**: Online/offline status, recording state, per-camera storage
- **Motion Events**: Motion detection events with smart detection types
- **Recording**: Recording duration, quality, and failure tracking

Example metrics:
```
# Camera status
unifi_protect_camera_up{camera_name="Front Door",camera_model="G4 Pro"} 1

# Motion events
unifi_protect_motion_events_total{camera_name="Driveway",event_type="vehicle"} 42

# Storage usage
unifi_protect_storage_used_bytes{nvr_name="Main NVR"} 1234567890
```

See [docs/metrics/](docs/metrics/) for complete metrics documentation.

## Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'unifi_protect'
    static_configs:
      - targets: ['unifi-protect-exporter:9099']
```

## Grafana Dashboards

Pre-built dashboards are available in the [dashboards/](dashboards/) directory.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/rknightion/unifi-protect-exporter
cd unifi-protect-exporter

# Install dependencies
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Type checking
uv run mypy .
```

### Adding New Collectors

See [docs/extending-collectors.md](docs/extending-collectors.md) for guidance on adding new metric collectors.

## Architecture

The exporter uses a three-tier collection system:
- **FAST (60s)**: Real-time metrics like motion events
- **MEDIUM (5m)**: Operational metrics like camera health
- **SLOW (15m)**: Configuration and system information

See [docs/adr/](docs/adr/) for architecture decision records.

## Troubleshooting

- Check logs: `docker-compose logs unifi_protect_exporter`
- Verify connectivity to UniFi Protect NVR
- Ensure credentials have appropriate permissions
- Check SSL certificate settings for self-signed certificates

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

Apache License 2.0 - see [LICENSE](LICENSE) file.

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Frknightion%2Funifi-protect-exporter.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Frknightion%2Funifi-protect-exporter?ref=badge_large)