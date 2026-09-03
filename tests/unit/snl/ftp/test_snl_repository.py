# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test SNL FTP repository."""

from stat import S_IFDIR, S_IFREG
from unittest import mock

import pytest
from paramiko import SFTPAttributes

from sonar.snl.ftp import SNLRepository


def sftp_attribute(filename, mode):
    """Build a remote directory entry.

    :param filename: name of the entry.
    :param mode: stat mode of the entry.
    :returns: SFTPAttributes object.
    """
    attribute = SFTPAttributes()
    attribute.filename = filename
    attribute.st_mode = mode
    return attribute


@pytest.fixture
def repository():
    """Return a repository connected to a mocked SFTP server."""
    with mock.patch("sonar.snl.ftp.SSHClient", autospec=True):
        repository = SNLRepository("snl_host", "user", "password", "/snl_folder")
        repository.connect()
        yield repository


SNL_HOST_KEY = "snl_host ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPZqFuISvMFSw/cZXBVt/AnjFXbb0N+xbwx0ZMzn3x6h"


@mock.patch("sonar.snl.ftp.SSHClient", autospec=True)
def test_connect(mock_ssh_client):
    """Test connection to the SNL server, host key taken from known_hosts."""
    repository = SNLRepository("snl_host", "user", "password", "/snl_folder")
    repository.connect()

    repository.ssh.load_system_host_keys.assert_called_with()
    repository.ssh.get_host_keys.return_value.add.assert_not_called()
    repository.ssh.connect.assert_called_with(
        "snl_host", username="user", password="password", allow_agent=False, look_for_keys=False
    )
    repository.client.chdir.assert_called_with("/snl_folder")


@mock.patch("paramiko.SSHClient.open_sftp")
@mock.patch("paramiko.SSHClient.connect")
def test_connect_with_configured_host_key(mock_connect, mock_open_sftp):
    """Test connection to the SNL server, host key given by the configuration."""
    repository = SNLRepository("snl_host", "user", "password", "/snl_folder", host_key=f"\n{SNL_HOST_KEY}\n")
    repository.connect()

    host_keys = repository.ssh.get_host_keys().lookup("snl_host")
    assert list(host_keys) == ["ssh-ed25519"]


def test_make_dir(repository):
    """Test directory creation, an existing directory is left untouched."""
    repository.make_dir("/snl_folder/rero-006-17")
    repository.client.mkdir.assert_not_called()

    repository.client.stat.side_effect = FileNotFoundError
    repository.make_dir("/snl_folder/rero-006-17")
    repository.client.mkdir.assert_called_with("/snl_folder/rero-006-17", mode=0o777)


def test_cwd(repository):
    """Test directory change."""
    repository.cwd("/snl_folder/rero-006-17")
    repository.client.chdir.assert_called_with("/snl_folder/rero-006-17")


def test_upload_file(repository):
    """Test file upload."""
    repository.upload_file("/tmp/test.pdf", "/snl_folder/rero-006-17/test.pdf")
    repository.client.put.assert_called_with("/tmp/test.pdf", "/snl_folder/rero-006-17/test.pdf")


def test_list_files(repository):
    """Test recursive listing of the stored files."""
    tree = {
        ".": [sftp_attribute("rero-006-17", S_IFDIR), sftp_attribute("readme.txt", S_IFREG)],
        "./rero-006-17": [sftp_attribute("test.pdf", S_IFREG)],
    }
    repository.client.listdir_attr.side_effect = lambda pathname: tree[pathname]

    assert list(repository.list_files()) == ["./rero-006-17/test.pdf", "./readme.txt"]


def test_close(repository):
    """Test connection closing."""
    repository.close()
    repository.client.close.assert_called_with()
    repository.ssh.close.assert_called_with()
