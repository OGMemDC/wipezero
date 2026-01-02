# WipeZero

Lightweight USB storage wipe utility for testing and CI.

[![CI](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml/badge.svg)](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml)

Quick start

- Install dependencies: `./setup.sh` (Debian/Ubuntu).
- Run unit tests locally: `make test` (or `pytest -q`).
- Run integration loopback test locally (destructive; uses loop devices):

  ```bash
  # Safety gate: set RUN_INTEGRATION=1 to opt in
  export RUN_INTEGRATION=1
  make integration
  ```

CI integration notes

- Unit tests run on push and PRs automatically.
- Integration loopback tests are gated and run only when:
  - A workflow dispatch is performed with `run_integration=true` AND the repository secret `ENABLE_INTEGRATION=true`, OR
  - A PR is labeled `run-integration` AND the repository secret `ENABLE_INTEGRATION=true`.

Replace `<OWNER>/<REPO>` in the CI badge URL with your repository owner/name to enable the badge link.
