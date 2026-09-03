# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""SNL FTP repository."""

import os
from stat import S_ISDIR

from paramiko import SSHClient
from paramiko.hostkeys import HostKeyEntry


class SNLRepository:
    """SNL FTP repository."""

    def __init__(self, host, user, password, directory, host_key=None):
        """Init class.

        :param host: FTP host.
        :param user: FTP user.
        :param password: FTP password.
        :param directory: Directory where files are stored.
        :param host_key: Host key of the FTP server, as a `known_hosts` line.
        """
        self.host = host
        self.user = user
        self.password = password
        self.directory = directory
        self.host_key = host_key

    def connect(self):
        """Connect to FTP server and change directory.

        The host key must be known, otherwise the connection is rejected.
        """
        self.ssh = SSHClient()
        self.ssh.load_system_host_keys()
        for line in (self.host_key or "").splitlines():
            if entry := HostKeyEntry.from_line(line.strip()):
                for name in entry.hostnames:
                    self.ssh.get_host_keys().add(name, entry.key.get_name(), entry.key)
        self.ssh.connect(
            self.host,
            username=self.user,
            password=self.password,
            allow_agent=False,
            look_for_keys=False,
        )
        self.client = self.ssh.open_sftp()
        self.client.chdir(self.directory)

    def make_dir(self, pathname):
        """Make new directory via FTP connection, if it does not exist yet."""
        try:
            self.client.stat(pathname)
        except FileNotFoundError:
            self.client.mkdir(pathname, mode=0o777)

    def cwd(self, pathname):
        """Move to directory via FTP connection."""
        self.client.chdir(pathname)

    def upload_file(self, file_path, file_name):
        """Upload file to SNL server via FTP connection.

        :param filepath: local filepath of file to upload
        """
        self.client.put(file_path, file_name)

    def list_files(self, pathname="."):
        """Recursively list files stored in a directory via FTP connection.

        :param pathname: remote directory to walk through.
        :returns: generator of remote file paths.
        """
        for attribute in self.client.listdir_attr(pathname):
            path = os.path.join(pathname, attribute.filename)
            if S_ISDIR(attribute.st_mode):
                yield from self.list_files(path)
            else:
                yield path

    def close(self):
        """Close FTP connection."""
        self.client.close()
        self.ssh.close()
