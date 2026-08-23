# Development and quality checks

HA Organizer is a Home Assistant custom integration targeting Python 3.14 and
Home Assistant `2026.8.0`. The project uses Home Assistant's `YYYY.M.patch`
version format.

## Local checks

Install the development environment and run the same checks used by CI:

```bash
uv sync
uv run ruff check custom_components/ha_organizer tests
uv run pytest
uv run pytest --cov=custom_components/ha_organizer \
  --cov-report=term --cov-report=xml
```

The project aims to keep Python coverage at or above 80%. The XML report is
written to `coverage.xml` for SonarQube and should not be committed.

## SonarQube validation

SonarQube reads the project configuration from
[`sonar-project.properties`](../sonar-project.properties). The required local
sequence is:

```bash
uv run ruff check custom_components/ha_organizer tests
uv run pytest --cov=custom_components/ha_organizer \
  --cov-report=term --cov-report=xml
```

The remote analysis runs automatically for pushes to `develop` and pull
requests targeting `main`. Check the **SonarQube Analysis** workflow in GitHub
Actions and confirm that the run and quality gate completed successfully.

For read-only diagnostic access to the configured SonarQube project, use the
repository's helper without printing or exposing its token:

```bash
sonar_script=/home/alves-dev/.codex/skills/sonar-analyzer/scripts/query_sonar.sh
"$sonar_script" > /tmp/ha-organizer-sonar.json
```

The helper may fail when the local environment cannot resolve
`sonar.alves-dev.com`; in that case, use the GitHub Actions result as the source
of truth for the remote analysis.

## Local Home Assistant testing

The local Home Assistant checkout is `/home/alves-dev/projects/others/core`.
The integration can be copied with:

```bash
.dev/copy-to-core.sh
```

Start Home Assistant from that checkout with:

```bash
uv run --project . python -m homeassistant --config config
```

Use the browser MCP/Chrome DevTools against `http://localhost:8123` for
exploratory UI, console, and network checks. The local test account is `igor`
with password `dev`; never reuse that credential outside this test instance.
