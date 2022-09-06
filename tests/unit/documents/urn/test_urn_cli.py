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

import os
import tempfile

import mock
from click.testing import CliRunner
from invenio_pidstore.providers.base import BaseProvider

from sonar.modules.documents.cli.urn import snl_upload_file
from sonar.snl.ftp import SNLRepository


@mock.patch('sonar.snl.ftp.FTP', autospec=True)
def test_snl_upload_file(mock_ftp_constructor, app, script_info):
    """Test upload file."""

    mock_ftp = mock_ftp_constructor.return_value
    mock_ftp.getwelcome.return_value = '220'

    repository = SNLRepository('snl_host', 'user', 'password', 'snl_folder')
    repository.connect()

    runner = CliRunner()
    result = runner.invoke(snl_upload_file, ['006-72', '/test/test.pdf'],
        obj=script_info)

    assert result.output == \
        'Persistent identifier does not exist for urn:nbn:ch:rero-006-72\n'

    with app.app_context():
        # create pid identifier
        provider = BaseProvider.create(
                pid_type="urn",
                pid_value="urn:nbn:ch:rero-006-72"
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
        path = tempfile.mkdtemp()
        filepath = os.path.join(path, 'test.pdf')
        f = open(filepath, 'w')
        f.write('Test')
        f.close()

        # upload file
        result = runner.invoke(snl_upload_file, ['006-72', filepath],
            obj=script_info)

        assert result.output == 'Successfully uploaded file test.pdf.\n'
        mock_ftp.mkd.assert_called_with('urn:nbn:ch:rero-006-72')
        mock_ftp.cwd.assert_called_with('urn:nbn:ch:rero-006-72')
