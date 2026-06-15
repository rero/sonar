# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""HEG FTP repository."""

import contextlib
import re
from ftplib import FTP
from os import listdir, path, remove
from zipfile import ZipFile


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
            self._ftp.retrbinary(f"RETR {file}", f.write)

        # Extract archive
        with ZipFile(target_file, "r") as zip_object:
            zip_object.extractall(target)

        # Remove source file
        remove(target_file)
        # Remove useless file
        with contextlib.suppress(Exception):
            remove(path.join(target, "clusters.json"))

        # Number of splitted files for each file
        number_of_files = int(10000 / records_size)

        # Split source files in smaller files
        for filename in listdir(target):
            file_path = path.join(target, filename)

            matches = re.match(r"^(.*)\.json$", filename)
            if matches:
                with open(file_path) as json_file:
                    files = [
                        open(path.join(target, f"{matches.group(1)}_{i + 1}.json"), "w")  # noqa: SIM115
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
