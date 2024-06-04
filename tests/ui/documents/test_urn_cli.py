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

"""Test URN cli."""


from io import BytesIO

import mock
from click.testing import CliRunner
from invenio_pidstore.providers.base import BaseProvider

from sonar.modules.documents.cli.urn import snl_upload_file
from sonar.snl.ftp import SNLRepository


@mock.patch("sonar.snl.ftp.Connection", autospec=True)
def test_snl_upload_file(
    mock_ftp_constructor, app, script_info, minimal_thesis_document_with_urn
):
    """Test upload file."""
    app.config["SONAR_APP_FTP_SNL_PATH"] = "/rero"

    mock_ftp = mock_ftp_constructor.return_value

    repository = SNLRepository("snl_host", "user", "password", "snl_folder")
    repository.connect()

    runner = CliRunner()
    result = runner.invoke(snl_upload_file, ["006-72"], obj=script_info)

    assert result.output == "Error: URN does not exists.\n"

    with app.app_context():
        # create pid identifier
        provider = BaseProvider.create(
            pid_type="urn", pid_value="urn:nbn:ch:rero-006-72"
        )
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
            [
                minimal_thesis_document_with_urn.get_rero_urn_code(
                    minimal_thesis_document_with_urn
                )
            ],
            obj=script_info,
        )
        assert "Template of email to send to SNL:" in result.output
        mock_ftp.mkdir.assert_called_with("/rero/rero-006-17")
