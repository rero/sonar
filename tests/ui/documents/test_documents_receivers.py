# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test documents recievers."""

import shutil
from os import listdir
from os.path import exists, join

from sonar.modules.documents.receivers import (
    chunks,
    export_json,
    transform_harvested_records,
)


def test_transform_harvested_records(app, bucket_location, capsys, harvested_record):
    """Test harvested record transformation."""

    transform_harvested_records(None, [harvested_record], name="archive_ouverte_unige", max="1")
    captured = capsys.readouterr()
    assert captured.out.find("1 records harvested") != -1

    # Max set to 0 --> import all
    transform_harvested_records(None, [harvested_record], name="archive_ouverte_unige", max="0")
    captured = capsys.readouterr()
    assert captured.out.find("1 records harvested") != -1

    # Not an import
    transform_harvested_records(None, [harvested_record], name="archive_ouverte_unige", max="1", action="not-existing")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_chunks():
    """Test chunks."""
    records = chunks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 3)
    records = list(records)
    assert len(records) == 4
    assert records[0] == [1, 2, 3]
    assert records[-1] == [10]


def test_export_json(app, bucket_location, monkeypatch, harvested_record):
    """Test export records to file."""
    # Patch the file upload to webdav.

    monkeypatch.setattr("webdav3.client.Client.upload_file", lambda *args: True)

    data_directory = join(app.instance_path, "data")

    export_json(None, [harvested_record], clean_file=False, name="archive_ouverte_unige", action="not-existing")
    assert not exists(data_directory)

    export_json(None, [harvested_record], clean_file=False, name="archive_ouverte_unige", action="export")
    assert len(listdir(data_directory)) == 1

    shutil.rmtree(data_directory)
