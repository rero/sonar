# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test HEG harvest CLI."""

from shutil import copyfile

from click.testing import CliRunner

from sonar.heg.cli.harvest import import_records, queue_files


def test_queue_files(app, script_info, monkeypatch):
    """Test queue files."""

    # Error
    def mock_queue_files(*args):
        raise Exception("File not found")

    monkeypatch.setattr("sonar.heg.ftp.HEGRepository.queue_files", mock_queue_files)
    runner = CliRunner()
    result = runner.invoke(queue_files, obj=script_info)
    assert "File not found" in result.output

    # OK
    monkeypatch.setattr("sonar.heg.ftp.HEGRepository.queue_files", lambda *args: True)
    result = runner.invoke(queue_files, ["--file", "data_200121"], obj=script_info)
    assert "Files queued successfully" in result.output


def test_import_records(app, script_info, monkeypatch, bucket_location):
    """Test import records."""
    # Data file not exist
    app.config.update(SONAR_APP_HEG_DATA_DIRECTORY="/non-existing/dir")
    runner = CliRunner()
    result = runner.invoke(import_records, ["--file", "HEG_data_1.json"], obj=script_info)
    assert "No such file or directory" in result.output

    # OK, with file param
    app.config.update(SONAR_APP_HEG_DATA_DIRECTORY="./tests/unit/heg/data")
    result = runner.invoke(import_records, ["--file", "HEG_data_1.json"], obj=script_info)
    assert "Process finished" in result.output

    # OK, with file param and remove file
    copyfile("./tests/unit/heg/data/HEG_data_1.json", "./tests/unit/heg/data/HEG_data_2.json")
    result = runner.invoke(import_records, ["--file", "HEG_data_2.json", "--remove-file"], obj=script_info)
    assert "Process finished" in result.output

    # OK, processing all files in directory
    result = runner.invoke(import_records, obj=script_info)
    assert "Process finished" in result.output

    # Record serialization failed
    def mock_serialize(*args):
        raise Exception("Serialization error")

    monkeypatch.setattr("sonar.heg.record.HEGRecord.serialize", mock_serialize)
    result = runner.invoke(import_records, obj=script_info)
    assert "Serialization error" in result.output
