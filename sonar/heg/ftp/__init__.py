# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""HEG FTP repository."""

import json
from ftplib import FTP
from os import listdir, path, remove
from zipfile import ZipFile


class HEGRepository():
    """HEG FTP repository."""

    host = None
    directory = None

    # FTP connection
    _ftp = None

    def __init__(self, host, directory):
        """Init class.

        :param host: FTP host.
        :param directory: Directory where files are stored.
        """
        self.host = host
        self.directory = directory

    def connect(self):
        """Connect to FTP server and change directory."""
        self._ftp = FTP(self.host)
        self._ftp.login()
        self._ftp.cwd(self.directory)

    def close(self):
        """Close the FTP connection."""
        self._ftp.close()

    def queue_files(self, file, target):
        """Download file and unzip it.

        :param file: File to download.
        :param target: Target directory.
        """
        self.remove_files_from_target(target)

        target_file = path.join(target, file)
        # Download file
        with open(target_file, 'wb') as f:
            self._ftp.retrbinary('RETR {file}'.format(file=file), f.write)

        # Extract archive
        with ZipFile(target_file, 'r') as zip_object:
            zip_object.extractall(target)

        try:
            # Remove source file
            remove(target_file)
            # Remove useless file
            remove(path.join(target, 'clusters.json'))
        except Exception:
            pass

    def remove_files_from_target(self, target):
        """Remove all data files from target.

        :param target: Target directory.
        """
        for filename in listdir(target):
            if filename.startswith('HEG'):
                remove(path.join(target, filename))
