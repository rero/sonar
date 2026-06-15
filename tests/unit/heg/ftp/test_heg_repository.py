# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test HEG FTP repository."""

import os
import tempfile
from unittest import mock

import pytest

from sonar.heg.ftp import HEGRepository


@mock.patch("sonar.heg.ftp.FTP", autospec=True)
def test_connect(mock_ftp_constructor):
    """Test connection."""
    # Connexion OK
    mock_ftp = mock_ftp_constructor.return_value
    mock_ftp.getwelcome.return_value = "220"

    repository = HEGRepository("candy.hesge.ch", "SONAR/baseline/complete")
    repository.connect()

    def unknown_host_exception():
        raise Exception("nodename nor servname provided, or not known")

    mock_ftp.login.side_effect = unknown_host_exception

    # Unknown host
    repository = HEGRepository("unknown.host.ch", "SONAR/baseline/complete")
    with pytest.raises(Exception) as exception:
        repository.connect()
    assert "nodename nor servname provided, or not known" in str(exception)

    def cwd_exception(directory):
        raise Exception("550 CWD failed")

    mock_ftp.login.side_effect = None
    mock_ftp.cwd.side_effect = cwd_exception

    # Unknown directory
    repository = HEGRepository("candy.hesge.ch", "550 CWD failed")
    with pytest.raises(Exception) as exception:
        repository.connect()
    assert "550 CWD failed" in str(exception)


@mock.patch("sonar.heg.ftp.FTP", autospec=True)
def test_close(mock_ftp_constructor):
    """Test close connection."""
    mock_ftp = mock_ftp_constructor.return_value
    mock_ftp.login.return_value = True
    mock_ftp.close.return_value = True

    repository = HEGRepository("candy.hesge.ch", "SONAR/baseline/complete")
    repository.connect()
    repository.close()

    def no_connection_exception():
        raise Exception("'NoneType' object has no attribute 'sendall'")

    mock_ftp.close.side_effect = no_connection_exception

    with pytest.raises(Exception) as exception:
        repository.close()
    assert "'NoneType' object has no attribute 'sendall'" in str(exception)


def test_queue_files(monkeypatch):
    """Test queue files."""
    file_name = os.path.join(os.path.dirname(__file__), "..", "data", "heg_data.zip")

    class MockFTP:
        def retrbinary(self, path, callback):
            with open(file_name, "rb") as file:
                callback(file.read())

    monkeypatch.setattr("sonar.heg.ftp.HEGRepository._ftp", MockFTP())

    repository = HEGRepository("candy.hesge.ch", "SONAR/baseline/complete")
    repository.queue_files("data.zip", "./data/heg")
    assert not os.path.exists("./data/heg/HEG_data_1.json")
    assert os.path.exists("./data/heg/HEG_data_1_1.json")


def test_remove_files_from_target():
    """Test remove file from target."""
    repository = HEGRepository("candy.hesge.ch", "SONAR/baseline/complete")

    path = tempfile.mkdtemp()

    with open(os.path.join(path, "test.txt"), "w") as f:
        f.write("Temp")

    with open(os.path.join(path, "HEG_test.txt"), "w") as f:
        f.write("Temp")

    assert len(os.listdir(path)) == 2
    repository.remove_files_from_target(path)
    assert len(os.listdir(path)) == 1
