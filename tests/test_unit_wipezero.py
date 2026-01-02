import argparse
from unittest.mock import patch, MagicMock
import pytest

import wipezero


def test_linux_probe_controller_parses_smart_supported():
    # subprocess.run is called twice: lsblk then smartctl
    mock_lsblk = MagicMock()
    mock_lsblk.stdout = "sda 0 MODEL SERIAL"
    mock_smart = MagicMock()
    mock_smart.stdout = "SMART support is: Enabled\nOther info"

    with patch('subprocess.run', side_effect=[mock_lsblk, mock_smart]) as mock_run:
        info = wipezero.linux_probe_controller('/dev/sda')
        assert 'lsblk' in info
        assert info['smart_supported'] is True
        assert mock_run.call_count == 2


def test_dd_wipe_calls_dd_with_progress():
    with patch('subprocess.run') as mock_run:
        wipezero.dd_wipe('/dev/fake', source='zero', progress=True, dry_run=False)
        expected = ['dd', 'if=/dev/zero', 'of=/dev/fake', 'bs=4M', 'status=progress']
        mock_run.assert_called_with(expected, check=True)


def test_validate_command_line_conflicts_crypto_secure_erase_raises():
    args = argparse.Namespace(crypto_erase=True, secure_erase=True, force=False, path='/', list=False, gui=False)
    with pytest.raises(SystemExit):
        wipezero.validate_command_line_parameters(args, dry_run=True)


def test_validate_requires_path_unless_list():
    args = argparse.Namespace(crypto_erase=False, secure_erase=False, force=False, path=None, list=False, gui=False)
    with pytest.raises(SystemExit):
        wipezero.validate_command_line_parameters(args, dry_run=True)
