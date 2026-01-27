[![CI](https://github.com/ashutoshfolane/pytest-dummyjson-api/actions/workflows/ci.yml/badge.svg)](https://github.com/ashutoshfolane/pytest-dummyjson-api/actions/workflows/ci.yml)
# pytest-dummyjson-api

Production-grade **API automation framework** built with **pytest + Python**, using **DummyJSON** as a public demo API.

This repository demonstrates how to build a **scalable, maintainable API test framework** with:
- clean architecture
- multi-environment support
- token-based authentication
- CI-ready design
- strong coding standards
---
## Tech stack
- Python 3.11+
- pytest
- httpx
- pydantic (settings & validation)
- tenacity (retries)
- ruff (lint + format)
- pre-commit (quality gates)
---
## Project structure
```text
pytest-dummyjson-api
├── .github/
│   └── workflows/
│       ├── ci.yml                  # PR smoke + main regression
│       └── nightly.yml             # Scheduled nightly regression
│
├── src/
│   └── api_framework/
│       ├── client.py               # Core HTTP client (httpx, retries, auth, logging)
│       ├── auth.py                 # Token minting & auth strategy
│       ├── config.py               # Environment & settings loader
│       │
│       ├── clients/                # Domain-level API abstractions
│       │   ├── __init__.py
│       │   ├── users_client.py     # Users domain operations
│       │   └── auth_client.py      # Auth domain operations
│       │
│       ├── validation/             # Validation utilities
│       │   ├── __init__.py
│       │   ├── settings.py         # Config validation (fail-fast)
│       │   └── schema.py           # JSON Schema / contract validation
│       │
│       └── utils/                  # Shared helpers (logging, redaction, etc.)
│
├── tests/
│   ├── auth/                       # Auth domain tests
│   │   ├── test_login_smoke.py
│   │   └── test_me_authenticated.py
│   │
│   ├── users/                      # Users domain tests
│   │   ├── test_users_smoke.py
│   │   └── test_users_regression.py
│   │
│   ├── contracts/                  # Contract / schema tests
│   │   └── test_users_contract.py
│   │
│   ├── schemas/                    # JSON Schemas for contract validation
│   │   └── users_list.schema.json
│   │
│   └── conftest.py                 # Pytest fixtures (api, settings)
│
├── env/
│   └── .env.local.example          # Example env config (no secrets)
│
├── pyproject.toml                  # Dependencies, pytest config, linting
├── README.md
└── CODEOWNERS
```
## Test Architecture
```text
┌──────────────────────┐
│        Tests         │
│  (smoke / regression │
│   / contract suites) │
└───────────┬──────────┘
            │
            ▼
┌──────────────────────┐
│    Domain Clients    │
│  UsersClient, Auth   │
│  (business intent)   │
└───────────┬──────────┘
            │
            ▼
┌──────────────────────┐
│     API Client       │
│  httpx + retries +   │
│  auth + logging      │
└───────────┬──────────┘
            │
            ▼
┌──────────────────────┐
│   External API       │
│    (DummyJSON)       │
└───────────┬──────────┘
            │
            ▼
┌──────────────────────┐
│ Contract Validation  │
│ JSON Schema checks  │
│ (@contract tests)   │
└──────────────────────┘
```
---
## Environment configuration
The framework supports **multiple environments** without relying on OS environment variables.
Environment files live under `env/`:
```text
env/
├── .env.example   # committed
├── .env.local     # gitignored
├── .env.qa        # gitignored
└── .env.staging   # gitignored
```
Example (env/.env.example)
```text
BASE_URL=https://dummyjson.com
TIMEOUT_SECONDS=10
RETRY_ATTEMPTS=3

# Auth (choose one approach)

# Fast path (CI or manual token)
AUTH_HEADER_NAME=Authorization
AUTH_HEADER_VALUE=

# Login-based auth (DummyJSON)
AUTH_USERNAME=
AUTH_PASSWORD=
```
Only .env.example is committed.
All real environment files are ignored.
---
## Authentication strategy
The framework supports **two authentication paths**:
### 1️⃣ Token fast path (recommended for CI)
Provide a token directly:
```env
AUTH_HEADER_VALUE=Bearer <access_token>
```
### 2️⃣ Login-based token (recommended for local)
Provide test credentials from https://dummyjson.com/docs/auth#auth-login
```text
AUTH_USERNAME=abc
AUTH_PASSWORD=xyz
```
• Token is fetched via POST /auth/login
• Token is cached per test session
• Automatically injected into authenticated requests
---
## Running tests locally
### Install dependencies
```bash
make install
```
Run smoke tests
```bash
pytest --env local -m smoke
```
Run authenticated tests
```bash
pytest --env local -m auth
```
Run full regression
```bash
make regression
```
---
## CI Test Runs
### GitHub Actions pipelines:
• Smoke tests on every PR
• Full regression on main and nightly schedule
### Test artifacts generated on CI:
• JUnit XML (for CI integrations)
• pytest-html report (self-contained)
---
## Secure & Transparent API Logging
* request/response logging for all API calls (pass or fail)
* log redaction to prevent credential leakage:
  * Redacts Authorization, Cookie, Set-Cookie
  * Redacts sensitive JSON fields (e.g. accessToken, refreshToken, password)
* Logs are printed in JSON-formatted, readable blocks for easy inspection
* CI uses --capture=tee-sys so logs appear in:
  * Console output
  * HTML reports
---
## Test Reports
* pytest-html reports include:
  * Environment details (Python, OS, plugins)
  * Per-test execution status
  * Captured request/response logs
* Reports are published as CI artifacts for post-run inspection
---
## Test markers
| Marker       | Purpose              |
|--------------|----------------------|
| `smoke`      | Fast critical checks |
| `regression` | Broader coverage     |
| `auth`       | Authenticated flows  |
| `negative`   | Error / edge cases   |

---
## Coding standards
This repository enforces quality gates via **pre-commit hooks**:
- Ruff (lint + format)
- Secret detection
- Consistent formatting before every commit
### Install pre-commit hooks
```bash
pre-commit install
```
### Run checks manually
```bash
pre-commit run --all-files
```
---
## Quality Dashboard

This framework includes a **lightweight, zero-backend quality dashboard** to provide clear visibility into API test health.

### What the dashboard shows
- Test suite summary (smoke / regression / contract)
- Total tests, pass rate, failures, skips
- Execution duration
- Flaky candidates (based on rolling history)
- Top failing tests

### How it works
1. Pytest generates **JUnit XML** during test execution.
2. Reporting scripts aggregate results into a single **metrics.json** file.
3. A static **HTML dashboard** renders the metrics in the browser.
4. All reports and dashboards are published as **CI artifacts**.

### How to view the dashboard
- Download `dashboard.html` and `metrics.json` from CI artifacts.
- Open `dashboard.html` locally in a browser.
- Load `metrics.json` when prompted.
---
## Design principles (6C model)
This framework is built using the **6C approach**:
1. **Core** – clean runnable skeleton  
2. **Config** – multi-env, auth, validation  
3. **CI** – Continuous Integration  
4. **Consistency** – data & reliability  
5. **Confidence** – reporting & visibility  
6. **Continue** – advanced quality layers
---
## Why DummyJSON?
DummyJSON provides:
- public authentication endpoints
- realistic response schemas
- no setup or infrastructure cost
---