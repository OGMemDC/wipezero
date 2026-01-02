#!/usr/bin/env bash
set -euo pipefail

# Integration loopback test for wipezero
# Safe by default: only runs if RUN_INTEGRATION=1
# Usage: RUN_INTEGRATION=1 bash tests/integration_loopback.sh

if [ "${RUN_INTEGRATION:-0}" != "1" ]; then
  echo "Skipping integration test; set RUN_INTEGRATION=1 to enable destructive loopback test"
  exit 0
fi

echo "Creating loopback image..."
fallocate -l 50M ci-test.img
loopdev=$(sudo losetup -f --show ci-test.img)

echo "Loop device: $loopdev"

# Dry-run (safe)
python3 wipezero.py "$loopdev" --profile nist-clear

# Destructive test (requires sudo and is run on the loop device only)
sudo python3 wipezero.py "$loopdev" --force --profile nist-clear --verify --report --report-dir ./ci-reports

# Clean up
sudo losetup -d "$loopdev"
rm ci-test.img

echo "Integration loopback test completed successfully."