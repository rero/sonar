# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test URN cli."""

from io import BytesIO
from unittest import mock

from click.testing import CliRunner
from invenio_pidstore.providers.base import BaseProvider

from sonar.modules.documents.cli.urn import snl_list_files, snl_upload_file
from sonar.snl.ftp import SNLRepository


@mock.patch("sonar.snl.ftp.SSHClient", autospec=True)
def test_snl_upload_file(mock_ssh_constructor, app, script_info, minimal_thesis_document_with_urn):
    """Test upload file."""
    app.config["SONAR_APP_FTP_SNL_PATH"] = "/rero"

    mock_ftp = mock_ssh_constructor.return_value.open_sftp.return_value
    mock_ftp.stat.side_effect = FileNotFoundError

    repository = SNLRepository("snl_host", "user", "password", "snl_folder")
    repository.connect()

    runner = CliRunner()
    result = runner.invoke(snl_upload_file, ["006-72"], obj=script_info)

    assert result.output == "Error: URN does not exists.\n"

    with app.app_context():
        # create pid identifier
        provider = BaseProvider.create(pid_type="urn", pid_value="urn:nbn:ch:rero-006-72")
        assert provider.pid
        assert provider.pid.pid_type == "urn"
        assert provider.pid.pid_value == "urn:nbn:ch:rero-006-72"

        # register identifier
        provider.register()
        assert provider.pid.is_registered()
        provider.sync_status()
        provider.update()

        # create file to upload
        minimal_thesis_document_with_urn.files["test.pdf"] = BytesIO(b"File content")
        minimal_thesis_document_with_urn.files["test.pdf"]["type"] = "file"
        minimal_thesis_document_with_urn.commit()

        # upload file
        result = runner.invoke(
            snl_upload_file,
            [minimal_thesis_document_with_urn.get_rero_urn_code(minimal_thesis_document_with_urn)],
            obj=script_info,
        )
        assert "Template of email to send to SNL:" in result.output
        mock_ftp.mkdir.assert_called_with("/rero/rero-006-17", mode=0o777)


@mock.patch("sonar.snl.ftp.SNLRepository.list_files")
@mock.patch("sonar.snl.ftp.SSHClient", autospec=True)
def test_snl_list_files(mock_ssh_constructor, mock_list_files, app, script_info):
    """Test listing of the files stored on the SNL server."""
    mock_list_files.return_value = ["./rero-006-17/test.pdf", "./readme.txt"]

    runner = CliRunner()
    result = runner.invoke(snl_list_files, obj=script_info)

    assert result.output == "./rero-006-17/test.pdf\n./readme.txt\n"

    # empty server
    mock_list_files.return_value = []
    result = runner.invoke(snl_list_files, obj=script_info)

    assert result.output == "No file found on SNL server.\n"
