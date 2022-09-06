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

"""Test SNL FTP repository."""

from unittest.mock import MagicMock

import mock
import pytest

from sonar.snl.ftp import SNLRepository


@mock.patch('sonar.snl.ftp.FTP', autospec=True)
def test_connect(mock_ftp_constructor):
    """Test connection."""
    # Connexion OK
    mock_ftp = mock_ftp_constructor.return_value
    mock_ftp.getwelcome.return_value = '220'

    repository = SNLRepository('snl_host', 'user', 'password', 'snl_folder')
    repository.connect()

    def unknown_host_exception(user, password):
        raise Exception('nodename nor servername provided, or not known')

    mock_ftp.login.side_effect = unknown_host_exception

    # Unknown host
    repository = SNLRepository('unknown.host.ch', 'user', 'password',
                               'snl_folder')
    with pytest.raises(Exception) as exception:
        repository.connect()
    assert 'nodename nor servername provided, or not known' in str(exception)

    def cwd_exception(directory):
        raise Exception('550 CWD failed')

    mock_ftp.login.side_effect = None
    mock_ftp.cwd.side_effect = cwd_exception

    # Unknown directory
    repository = SNLRepository('snl_host', 'user', 'password',
                               '550 CWD failed')
    with pytest.raises(Exception) as exception:
        repository.connect()
    assert '550 CWD failed' in str(exception)


@mock.patch('sonar.snl.ftp.FTP', autospec=True)
def test_mkdir(mock_ftp_constructor):
    """Test make directory via FTP connection."""
    mock_ftp = mock_ftp_constructor.return_value
    mock_ftp.login.return_value = True

    pathname = '006-72'
    repository = SNLRepository('snl_host', 'user', 'password', 'snl_folder')
    repository.connect()
    repository.make_dir(pathname)
    mock_ftp.mkd.assert_called_with(pathname)


@mock.patch('sonar.snl.ftp.FTP', autospec=True)
def test_cwd(mock_ftp_constructor):
    """Test change directory via FTP connection."""
    mock_ftp = mock_ftp_constructor.return_value
    mock_ftp.login.return_value = True

    pathname = 'urn:nbn:ch:rero-006-72'
    repository = SNLRepository('snl_host', 'user', 'password', 'snl_folder')
    repository.connect()
    repository.cwd(pathname)
    mock_ftp.cwd.assert_called_with(pathname)


@mock.patch('sonar.snl.ftp.FTP', autospec=True)
def test_list(mock_ftp_constructor):
    """Test list directory via FTP connection."""
    mock_ftp = mock_ftp_constructor.return_value
    mock_ftp.login.return_value = True
    mock_ftp.nlst = MagicMock(return_value=['test.pdf'])

    repository = SNLRepository('snl_host', 'user', 'password', 'snl_folder')
    repository.connect()

    results = repository.list()
    mock_ftp.nlst.assert_called_with()
    assert results == ['test.pdf']


@mock.patch('sonar.snl.ftp.FTP', autospec=True)
def test_close(mock_ftp_constructor):
    """Test close connection."""
    mock_ftp = mock_ftp_constructor.return_value
    mock_ftp.login.return_value = True
    mock_ftp.close.return_value = True

    repository = SNLRepository('snl_host', 'user', 'password', 'snl_folder')
    repository.connect()
    repository.close()

    def no_connection_exception():
        raise Exception('\'NoneType\' object has no attribute \'sendall\'')

    mock_ftp.close.side_effect = no_connection_exception

    with pytest.raises(Exception) as exception:
        repository.close()
    assert '\'NoneType\' object has no attribute \'sendall\'' in str(exception)
