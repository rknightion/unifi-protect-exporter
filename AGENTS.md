# AGENTS.md

<system_context>
UniFi Protect Exporter - A production-ready Prometheus exporter that collects metrics from UniFi Protect systems and exposes them for monitoring. Supports OpenTelemetry mirroring and includes comprehensive collectors for cameras, motion events, recording statistics, and system health.
</system_context>

<critical_notes>
- **Navigate to subdirectories** for detailed context - each has its own `CLAUDE.md`
- **Follow update tiers**: FAST (60s), MEDIUM (300s), SLOW (900s) based on data volatility
- **Security**: Never log or expose credentials, use read-only access when possible
- **Memory**: Be mindful of API connections and implement proper error handling
- **Use parallel tasks/agents** when suitable use the parallel tasks and agents available to you
- **Never issue git commands** the user will handle all 'git' commands
</critical_notes>

<file_map>
## NAVIGATION MAP - DETAILED CONTEXT IN SUBDIRECTORIES
- `src/unifi_protect_exporter/` - Main source package - See `src/unifi_protect_exporter/CLAUDE.md`
- `src/unifi_protect_exporter/core/` - Core infrastructure - See `src/unifi_protect_exporter/core/CLAUDE.md`
- `src/unifi_protect_exporter/collectors/` - Collector implementations - See `src/unifi_protect_exporter/collectors/CLAUDE.md`
- `src/unifi_protect_exporter/collectors/cameras/` - Camera collectors - See `src/unifi_protect_exporter/collectors/cameras/CLAUDE.md`
- `src/unifi_protect_exporter/collectors/system_collectors/` - System collectors - See `src/unifi_protect_exporter/collectors/system_collectors/CLAUDE.md`
- `src/unifi_protect_exporter/collectors/motion_collectors/` - Motion event collectors - See `src/unifi_protect_exporter/collectors/motion_collectors/CLAUDE.md`
- `src/unifi_protect_exporter/api/` - API client wrapper - See `src/unifi_protect_exporter/api/CLAUDE.md`
- `tests/` - Test suite and patterns - See `tests/CLAUDE.md`
- `pyproject.toml` - Project dependencies and configuration
- `dashboards/` - Grafana dashboard JSON exports
- `docs/` - Documentation including ADRs and metrics reference
</file_map>

<paved_path>
## HIGH-LEVEL ARCHITECTURE

### Collector Organization
- **Core Infrastructure**: Logging, config, metrics, error handling ’ `src/unifi_protect_exporter/core/CLAUDE.md`
- **Collector Pattern**: Auto-registration, update tiers, base classes ’ `src/unifi_protect_exporter/collectors/CLAUDE.md`
- **Camera-Specific**: Individual camera model collectors ’ `src/unifi_protect_exporter/collectors/cameras/CLAUDE.md`
- **API Integration**: Async wrapper for uiprotect SDK ’ `src/unifi_protect_exporter/api/CLAUDE.md`
- **Testing**: Factories, mocks, assertions ’ `tests/CLAUDE.md`

### Key Principles
- **Enum-based naming**: Use MetricName and LabelName enums for consistency
- **Domain models**: Pydantic validation for all API responses
- **Error handling**: Decorators for consistent error management
- **Update tiers**: FAST (60s), MEDIUM (300s), SLOW (900s) based on volatility
</paved_path>

<workflow>
## PROJECT-WIDE WORKFLOW
Navigate to specific subdirectories for detailed implementation patterns:

### Development Areas
- **Core Changes**: Infrastructure, logging, config ’ `src/unifi_protect_exporter/core/CLAUDE.md`
- **New Collectors**: Camera, system, motion event ’ `src/unifi_protect_exporter/collectors/CLAUDE.md`
- **API Updates**: Client wrapper changes ’ `src/unifi_protect_exporter/api/CLAUDE.md`
- **Testing**: New tests, factories, mocks ’ `tests/CLAUDE.md`

### Cross-Cutting Concerns
- **Metrics**: Always use enums from `core/constants/metrics_constants.py`
- **Labels**: Always use `LabelName` enum from `core/metrics.py`
- **Domain Models**: Always validate with Pydantic models
- **Error Handling**: Always use decorators from `core/error_handling.py`
</workflow>

<bash_commands>
## COMMON COMMANDS
- `uv run python -m unifi_protect_exporter` - Start the exporter
- `uv run ruff check --fix .` - Lint and auto-fix code
- `uv run mypy .` - Type checking
- `uv run pytest` - Run tests
- `uv run pytest -v -k test_name` - Run specific test
- `uv run python src/unifi_protect_exporter/tools/generate_metrics_docs.py` - Generate metrics docs
- `uv add package_name` - Add new dependency
- `docker-compose up` - Start with Docker
- `make docs-serve` - Serve documentation locally
</bash_commands>

<code_style>
## PROJECT-WIDE STYLE GUIDELINES
- **Formatting**: Black with 88-char line length
- **Type hints**: Use `from __future__ import annotations` and proper typing
- **Imports**: Group stdlib, third-party, local with proper organization
- **Docstrings**: NumPy-style with type hints
- **Constants**: Use Literal & Enum/StrEnum appropriately
- **Early returns**: Reduce nesting where possible
- **Async**: Use proper async patterns for UniFi Protect SDK calls
</code_style>

<fatal_implications>
## PROJECT-WIDE CRITICAL "DO NOT" RULES
- **NEVER use hardcoded metric/label names** - always use enums
- **NEVER log passwords or credentials**
- **NEVER assume API response format** - always validate
- **NEVER skip error handling** for API calls
- **NEVER use `any` types** without explicit justification
- **NEVER modify tests to match incorrect implementations**
- **NEVER commit without running linters and type checks**
- **NEVER work in subdirectories without consulting their `CLAUDE.md`**
</fatal_implications>