![wipezero logo](https://github.com/OGMemDC/wipezero/blob/main/doc/resources/wipezero_small.png)
# WipeZero
Lightweight USB storage wipe utility.

[![CI](https://github.com/OGMemDC/wipezero/actions/workflows/ci.yml/badge.svg)](https://github.com/OGMemDC/wipezero/actions/workflows/ci.yml)

Quick start

- Install dependencies: `./setup.sh` (Debian/Ubuntu).
- Run unit tests locally: `make test` (or `pytest -q`).
- Run integration loopback test locally (destructive; uses loop devices):

  ```bash
  # Safety gate: set RUN_INTEGRATION=1 to opt in
  export RUN_INTEGRATION=1
  tests/integration_loopback.sh
  ```

CI integration notes

- Unit tests run on push and PRs automatically.
- Integration loopback tests are gated and run only when:
  - A workflow dispatch is performed with `run_integration=true` AND the repository secret `ENABLE_INTEGRATION=true`, OR
  - A PR is labeled `run-integration` AND the repository secret `ENABLE_INTEGRATION=true`.

