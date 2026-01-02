# Copilot Instructions for WipeZero 🔧

Purpose
- Brief: Guide an AI coding agent to be immediately productive in this repository (what matters, how to run, safety rules, and key code locations).

Getting started
- Install dependencies: run `./setup.sh` (assumes Debian/Ubuntu; `apt` and `pip` access required).
- Python requirement: source uses `match/case` (Python >= 3.10). Confirm interpreter version before running.
- Quick smoke: `python3 wipezero.py --list` (non-destructive by default).
- Build: use PyInstaller (installed by `setup.sh`): `pyinstaller --onefile wipezero.py`.

Safety & workflow notes ⚠️
- Default mode is a dry-run. The script is non-destructive unless run with `--force` (required for destructive operations).
- Critical safety checks in `validate_command_line_parameters()` and `is_system_disk()` — do not bypass them.
- Always test on a disposable device or a loopback image (example below) before running against real hardware.

Common commands / examples
- List removable devices (safe): `python3 wipezero.py --list`
- Dry-run NIST clear overwrite (safe): `python3 wipezero.py /path/to/mount --profile nist-clear`
- Destructive DOD wipe: `python3 wipezero.py /dev/sdb --force --profile dod`
- Auto-select (requires `--force`): `python3 wipezero.py /dev/sdb --auto --force`
- Attempt crypto erase (Linux only): `python3 wipezero.py /dev/sdb --crypto-erase --force`
- Generate reports: `--report --report-dir ./reports`, `--pdf-report`, `--gui-report`
- Verification flags: use `--verify`, `--hash-verify`, `--forensic-verify`

Key files & code pointers (where to look) 🔍
- `wipezero.py` — single-file application. Main flow: comment above `main()` lists the execution steps.
  - Device discovery and listing: `list_usb()`
  - Capability detection: `detect_device_capabilities()` and `linux_detect_capabilities()`
  - Controller probe (SMART): `probe_controller()` -> `linux_probe_controller()`
  - Wipe implementations: `dd_wipe()`, `wipe_device()`, `secure_erase()` and OS-specific helpers
  - Verification: `verify_zero_pattern()`, `hash_sample_verify()`, `forensic_verify()`
  - Reporting/signing: `generate_report()`, `generate_signed_pdf()`, `sign_report_x509()`
  - GUI helpers: `gui_confirm()`, `launch_gui_report()`
- `setup.sh` — dependency installer and PyInstaller toolchain.

Project-specific conventions & gotchas
- Uses many OS utilities (`lsblk`, `blkdiscard`, `smartctl`, `diskutil`, `diskpart`, `wmic`) — CI or developer machines must install these for integration testing.
- `--crypto-erase` is Linux-only in practice (code checks for OS and controller capability).
- The code uses `--force` to enable destructive behavior and disallows `--crypto-erase`/`--secure-erase` without `--force`.
- The PDF signing helper (`sign_report_x509`) exists, but main() does not accept cert/key paths — be conservative when adding automated signing.
- Help text and some strings contain small typos; fix them if you touch CLI help text.
- Prefer unit/integration tests that use loopback device images and `losetup` or mock subprocess calls rather than touching physical devices.

Loopback-device test recipe 🧪

A short, reproducible recipe to test destructive branches safely using a loopback file image and `losetup` (Linux-only):

1. Create a sparse image file and attach it to a loop device (100MiB example):

```bash
fallocate -l 100M test.img
sudo losetup -f --show test.img   # prints e.g. /dev/loop0
```

2. (Optional) Add a partition table and a filesystem, or test the raw block device directly:

```bash
sudo parted /dev/loop0 mklabel msdos mkpart primary 1MiB 100%
sudo mkfs.ext4 /dev/loop0
```

3. Dry-run a wipe (safe): target the mount path or the raw loop device. Dry-run behavior is the default unless `--force` is passed.

```bash
python3 wipezero.py /path/to/mount_or_loopdev --profile nist-clear
```

4. Run a destructive wipe (use only on the loop device, and with `--force`):

```bash
sudo python3 wipezero.py /dev/loop0 --force --profile nist-clear --verify --report --report-dir ./reports
```

5. Verify and clean up:

```bash
sudo losetup -d /dev/loop0
rm test.img
```

Bash test snippet for CI (unprivileged CI may require `sudo` or a privileged job):

```bash
set -e
fallocate -l 50M ci-test.img
loopdev=$(sudo losetup -f --show ci-test.img)
# Dry-run
python3 wipezero.py $loopdev --profile nist-clear
# Destructive
sudo python3 wipezero.py $loopdev --force --profile nist-clear --verify --report --report-dir ./ci-reports
sudo losetup -d $loopdev
rm ci-test.img
```

Notes & tips:
- Use small image sizes and ensure the loop device is used (not a physical disk) to avoid accidental data loss.
- Prefer mocking `subprocess.run` when writing unit tests for functions that call external utilities (`lsblk`, `blkdiscard`, `diskutil`, `smartctl`).
- Ensure the test runner has `losetup` available (install `util-linux` on minimal images).

Contribution pointers for an AI agent ✅
- Before changing any destructive path: add unit tests and a loopback image test that exercises the branch.
- CI: a GitHub Actions workflow has been added at `.github/workflows/ci.yml`.
  - Unit tests run on `push`/`pull_request` and use `pytest`.
  - Integration loopback tests are gated: run via `workflow_dispatch` with `run_integration=true` *or* by adding the `run-integration` label to a PR. Both require a repo secret `ENABLE_INTEGRATION=true` and a self-hosted Linux runner with `losetup`.
- Add a `README.md` describing Python version, basic usage, and release build steps (PyInstaller example). A CI badge template has been added to `README.md` — replace `<OWNER>/<REPO>` in the URL.
- `tox.ini` has been added for multi-Python testing (see `tox.ini` for py310 and py311 envs).
- Add a small test harness that can emulate devices (e.g., `test.img` + `losetup`) and automated CI steps for Linux integration.
- Make sure new changes preserve dry-run behavior and safety checks.

If anything in this summary is unclear or you want more examples (e.g., loopback test recipe or sample PyInstaller build spec), tell me which area to expand. 🙋‍♂️
