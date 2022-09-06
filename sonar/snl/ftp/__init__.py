# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2023 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""SNL FTP repository."""

import os
from ftplib import FTP

from flask import current_app


class SNLRepository():
    """SNL FTP repository."""

    host = None
    user = None
    password = None
    directory = None

    # FTP connection
    _ftp = None

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
        self._ftp = FTP(self.host)
        self._ftp.login(self.user, self.password)
        self._ftp.cwd(self.directory)

    def make_dir(self, pathname):
        """Make new directory via FTP connection."""
        self._ftp.mkd(pathname)

    def cwd(self, pathname):
        """Move to directory via FTP connection."""
        self._ftp.cwd(pathname)

    def list(self):
        """List directory via FTP connection."""
        return self._ftp.nlst()

    def upload_file(self, filepath):
        """Upload file to SNL server via FTP connection.

        :param filepath: local filepath of file to upload
        """
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as file:
            self._ftp.storbinary(f"STOR {filename}", file)

    def close(self):
        """Close FTP connection."""
        self._ftp.close()
