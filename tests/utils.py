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

"""Utils function for testing."""

import mock


class VerifyRecordPermissionPatch():
    """Verify record permissions."""

    status_code = 200


def mock_response(status=200, content="CONTENT", json_data=None,
                  raise_for_status=None):
    """Mock a request response."""
    mock_resp = mock.Mock()
    # mock raise_for_status call w/optional error
    mock_resp.raise_for_status = mock.Mock()
    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status
    # set status code and content
    mock_resp.status_code = status
    mock_resp.content = content
    # add json data if provided
    if json_data:
        mock_resp.json = mock.Mock(return_value=json_data)
    return mock_resp

class MockArkServer:
    """Mock an ARK Server."""

    @staticmethod
    def get(url, auth=None, *args, **kwargs):
        """Mock the requests get function."""
        import requests
        class Response:
            """Dummy response object."""

            status_code = 200
            text = ''
        if auth and (auth.username != 'test' or auth.password != 'test'):
            Response.status_code = 401
            Response.text = 'error: unauthorized'
            return Response
        # status
        if url.startswith('https://www.arketype.ch/status'):
            Response.text = 'success: EZID is up'
        # get
        elif url.startswith('https://www.arketype.ch/id/'):
            ark_id = url.replace('https://www.arketype.ch/id/', '')
            Response.text = f'''
success: {ark_id}
_updated: 1620802178
_target: https://sonar.ch/global/documents/1
_profile: erc
_export: yes
_owner: apitest
_ownergroup: apitest_g
_created: 1620802104
_status: public
'''
        # login
        elif url.startswith('https://www.arketype.ch/login'):
            Response.text = 'success: session cookie returned'
        # resolve
        elif url.startswith('https://n2t.net/'):
            Response.status_code = 302
            Response.headers = dict(
                Location='https://sonar.ch/global/documents/1')
        else:
            return requests.get(url, *args, **kwargs)
        return Response

    @staticmethod
    def put(url, auth=None, *args, **kwargs):
        """Mock the requests put function."""
        class Response:
            """Dummy response object."""

            status_code = 200
            text = ''
        if auth and (auth.username != 'test' or auth.password != 'test'):
            Response.status_code = 401
            Response.text = 'error: unauthorized'
            return Response
        # create
        if url.startswith('https://www.arketype.ch/id/ark:/99999/ffk3'):
            Response.status_code = 201
            ark_id = url.replace('https://www.arketype.ch/id/', '')\
                .replace('?update_if_exists=yes', '')
            Response.text = f'success: {ark_id}'
        else:
            return None
        return Response

    @staticmethod
    def post(url, auth=None, *args, **kwargs):
        """Mock the requests post function."""

        class Response:
            """Dummy response object."""

            status_code = 200
            text = ''
        if auth and (auth.username != 'test' or auth.password != 'test'):
            Response.status_code = 401
            Response.text = 'error: unauthorized'
            return Response
        # mint
        if url.startswith('https://www.arketype.ch/shoulder/ark:/99999/ffk3'):
            Response.status_code = 201
            Response.text = 'success: ark:/99999/ffk3xx'
        # update
        elif url.startswith('https://www.arketype.ch/id/ark:/99999/ffk3'):
            ark_id = url.replace('https://www.arketype.ch/id/', '')
            Response.text = f'success: {ark_id}'
        else:
            return None
        return Response
