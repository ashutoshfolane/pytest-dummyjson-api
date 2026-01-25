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
pytest-dummyjson-api/
├── src/
│   └── api_framework/
│       ├── client.py        # API client wrapper
│       ├── auth.py          # Token-based auth helper
│       ├── config.py        # Config + env loading
│       └── validation.py   # Fail-fast config validation
├── tests/
│   ├── conftest.py          # pytest fixtures & --env option
│   ├── test_users_smoke.py
│   ├── test_auth_smoke.py
│   └── test_me_authenticated.py
├── env/
│   └── .env.example         # Example config (committed)
├── .pre-commit-config.yaml
├── Makefile
├── pyproject.toml
└── README.md
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