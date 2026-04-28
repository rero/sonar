# SONAR Claude guide

## Overview

SONAR (Swiss Open Access Repository) is the Python/Flask backend for an archive of scholarly publications from Swiss public research institutions. Some frontend elements live in this project as HTML/Jinja templates; the rest is a separate Angular project (sonar-ui) based on ng-core.

**Stack**: Python 3.14, Flask (Invenio), PostgreSQL, Elasticsearch 7, Celery, RabbitMQ, Redis
**Package manager**: `uv` with `poethepoet` for task running

## Commands

During development, all commands are run through uv's virtual env with `uv run`.

### Linting and formatting

**IMPORTANT:** After editing files, make sure that there are no errors in the formatting and linting.

```bash
uv run poe lint     # ruff check sonar tests
uv run poe format   # ruff format .
```

### Setup (done by humans)

Human developers will run the required containers, the app setup and the servers on their own terms.

## Architecture

### Module Structure

Most business logic lives in `sonar/modules/`. Each module follows a consistent pattern:

```text
sonar/modules/<module_name>/
├── api.py            # Record class + Search class + Indexer (core business logic)
├── models.py         # SQLAlchemy model + Identifier + Metadata
├── views.py          # Flask blueprint (UI routes)
├── rest.py           # Flask blueprint (REST API routes)
├── tasks.py          # Celery async tasks
├── receivers.py      # Signal handlers (enrich data before indexing, file events)
├── permissions.py    # Access control rules
├── minters.py        # PID minting
├── jsonschemas/      # JSON Schema for validation
├── mappings/v7/      # Elasticsearch index mappings
├── serializers/      # REST response serializers
├── dumpers.py        # Data dumpers for ES indexing
├── jsonresolvers.py  # JSON $ref resolver
└── marshmallow/      # Marshmallow schemas (loaders/dumpers for REST)
```

A newer `sonar/resources/` tree hosts modules built on `invenio-records-resources` (e.g. `projects`) with the service/resource pattern; new resources should generally follow that style. Organisation-specific customizations live under `sonar/dedicated/` (e.g. `hepvs`).

### Base Classes

- **`SonarRecord`** (`sonar/modules/api.py`): extends `invenio_records_files.api.Record` with a `FilesMixin`. All domain records (Document, Deposit, Organisation, User, Collection, etc.) inherit from this. Provides PID management, ref-link helpers, file handling, and reindexing.
- **`SonarSearch`** (`sonar/modules/api.py`): extends `invenio_search.api.RecordsSearch`. Each module defines its own search class with a specific ES index.
- **`SonarIndexer`** (`sonar/modules/api.py`): extends `invenio_indexer.api.RecordIndexer` and flushes the ES index after each operation.

### Signal/Event Flow

The `sonar/ext.py` file wires up signal listeners. Before a record is indexed in Elasticsearch, `receivers.py` in each module (and dumpers) can enrich the data (e.g., adding computed fields, resolving references). This is the primary mechanism for denormalizing data into ES. File upload/delete signals are also bridged through `sonar/modules/receivers.py`.

### API Entry Points

REST endpoints are registered in `pyproject.toml` under `[project.entry-points."invenio_base.api_blueprints"]`. Each module's `rest.py` exports an `api_blueprint`. UI blueprints are registered under `[project.entry-points."invenio_base.blueprints"]` and exported from `views.py`.

### Permissions

Each module has a `permissions.py` using `invenio-records-permissions`. Access is typically scoped by organisation membership (multi-tenancy); some records are further scoped by subdivision.

## Code Style

- Be clear and concise in the docstrings and do not over-comment the code.
- Do not use Python type annotations (no `-> str`, `: str`, etc. in signatures).
- Ruff is configured with `line-length = 120` and pep257 docstring convention; see `[tool.ruff]` in `pyproject.toml` for the enabled rule sets.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org)

### Translations

Translations are only added manually before a release. During standard development, only make sure that any strings that must be displayed to the end-user are marked for translations in the code, but do not run the extractor or edit any files in `sonar/translations`.

## Testing Notes

- Tests use function-based style (no class-based tests).
- Tests are split into `tests/api/`, `tests/ui/`, `tests/unit/`
- The project follows a test-driven development methodology. Each commit must be accompanied by tests that ensure that the functionality works as intended. Tests must follow DRY principles and should only test specific app behaviour and not the behaviour of external modules (e.g. invenio dependencies).
- Test fixtures (shared data) are in `tests/conftest.py` and the per-layer `conftest.py` files (`tests/api/conftest.py`, `tests/ui/conftest.py`).
- Sample data is in `tests/data/` and `data/`
- pytest is configured in `pyproject.toml` (`[tool.pytest.ini_options]`) with `--ruff`, `--doctest-modules` and coverage on `sonar`.

### Running the tests (done by humans)

Human developers will run the needed tests from their consoles because they need to make sure the tests run only when their testing container runs.
