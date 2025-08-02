"""UniFi Protect exporter for Prometheus and OpenTelemetry."""

from .core import get_settings
from .core.config import get_version

__version__ = get_version()

__all__ = ["get_settings", "__version__"]