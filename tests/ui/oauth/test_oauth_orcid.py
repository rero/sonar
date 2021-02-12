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

"""Test OAuth with ORCID."""

import sonar.modules.oauth.orcid as sonar_orcid


def test_account_info(app, mock_api_read_record, orcid_record, user_record):
    """Test account info extraction."""
    assert sonar_orcid.account_info(None, orcid_record) == user_record


def test_account_setup(app, orcid_record, remote_account):
    """Test account setup after login."""
    account, token = remote_account

    ioc = app.extensions['oauthlib.client']

    sonar_orcid.account_setup(ioc.remote_apps['orcid'], token, orcid_record)

    assert account.extra_data['orcid'] == orcid_record['orcid']


def test_get_orcid_record(mock_api_read_record, app, orcid_record):
    """Test to get an orcid detail."""
    # Test valid returned record
    record = sonar_orcid.get_orcid_record(orcid_record['orcid'],
                                          orcid_record['access_token'])
    assert record['orcid-identifier']['path'] == orcid_record['orcid']

    # Test error when request_type is invalid
    record = sonar_orcid.get_orcid_record(orcid_record['orcid'],
                                          orcid_record['access_token'], 'FAKE')
    assert not record

    # Test error when access token is invalid
    record = sonar_orcid.get_orcid_record(orcid_record['orcid'],
                                          'NOT_EXISTING')
    assert not record

    # Test error when record id does not exist
    record = sonar_orcid.get_orcid_record('NOT_EXISTING',
                                          orcid_record['access_token'])
    assert not record


def test_get_orcid_record_email(mock_api_read_record, app, orcid_record):
    """Test getting ORCID record email."""
    # Test existing email
    email = sonar_orcid.get_orcid_record_email(orcid_record['orcid'],
                                               orcid_record['access_token'])
    assert email == 'john.doe@test.com'

    # Test when record id does not exists
    email = sonar_orcid.get_orcid_record_email('NOT_EXISTING',
                                               orcid_record['access_token'])
    assert email == ''

    # Test when access token does not exists
    email = sonar_orcid.get_orcid_record_email(orcid_record['orcid'],
                                               'NOT_EXISTING')
    assert email == ''
