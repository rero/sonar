# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""SNL FTP repository."""

from sftpretty import Connection


class SNLRepository:
    """SNL FTP repository."""

    def __init__(self, host, user, password, directory):
        """Init class.

        :param host: FTP host.
        :param user: FTP user.
        :param password: FTP password.
        :param directory: Directory where files are stored.
        """
        self.host = host
        self.user = user
        self.password = password
        self.directory = directory

    def connect(self):
        """Connect to FTP server and change directory."""
        self.client = Connection(
            self.host,
            username=self.user,
            password=self.password,
            default_path=self.directory,
        )

    def make_dir(self, pathname):
        """Make new directory via FTP connection."""
        self.client.mkdir(pathname)

    def cwd(self, pathname):
        """Move to directory via FTP connection."""
        self.client.cd(pathname)

    def upload_file(self, file_path, file_name):
        """Upload file to SNL server via FTP connection.

        :param filepath: local filepath of file to upload
        """
        self.client.put(file_path, file_name)

    def close(self):
        """Close FTP connection."""
        self.client.close()
