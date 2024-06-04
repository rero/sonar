# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
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
import re
from ftplib import FTP
from os import listdir, path, remove
from zipfile import ZipFile

from sonar.modules.utils import chunks


class HEGRepository:
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

    def queue_files(self, file, target, records_size=500):
        """Download file and unzip it.

        :param file: File to download.
        :param target: Target directory.
        :param records_size: Number of records per file.
        """
        self.remove_files_from_target(target)

        target_file = path.join(target, file)
        # Download file
        with open(target_file, "wb") as f:
            self._ftp.retrbinary("RETR {file}".format(file=file), f.write)

        # Extract archive
        with ZipFile(target_file, "r") as zip_object:
            zip_object.extractall(target)

        # Remove source file
        remove(target_file)
        # Remove useless file
        try:
            remove(path.join(target, "clusters.json"))
        except Exception:
            pass

        # Number of splitted files for each file
        number_of_files = int(10000 / records_size)

        # Split source files in smaller files
        for filename in listdir(target):
            file_path = path.join(target, filename)

            matches = re.match(r"^(.*)\.json$", filename)
            if matches:
                with open(file_path) as json_file:
                    files = [
                        open(
                            path.join(
                                target,
                                "{prefix}_{index}.json".format(
                                    prefix=matches.group(1), index=(i + 1)
                                ),
                            ),
                            "w",
                        )
                        for i in range(number_of_files)
                    ]
                    for i, line in enumerate(json_file):
                        files[i % number_of_files].write(line)
                    for f in files:
                        f.close()

                    remove(file_path)

    def remove_files_from_target(self, target):
        """Remove all data files from target.

        :param target: Target directory.
        """
        for filename in listdir(target):
            if filename.startswith("HEG"):
                remove(path.join(target, filename))
