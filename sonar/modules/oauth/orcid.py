# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""ORCID OAuth custom process for SONAR."""

import orcid
from flask import current_app
from invenio_db import db
from invenio_oauthclient.utils import oauth_link_external_id
from requests import RequestException
from slugify import slugify


def account_info(remote, resp):
    """Retrieve remote account information used to find local user.

    It returns a dictionary with the following structure:

    .. code-block:: python

        {
            'user': {
                'profile': {
                    'full_name': 'Full Name',
                },
            },
            'external_id': 'orcid-unique-identifier',
            'external_method': 'orcid',
        }

    :param remote: The remote application.
    :param resp: (dict) Response given by the API.
    :returns: A dictionary with the user information.
    """
    orcid_id = resp.get('orcid')

    record = {
        'external_id': orcid_id,
        'external_method': 'orcid',
        'user': {
            'profile': {
                'full_name': resp.get('name'),
                'username': slugify(resp.get('name', '')),
            }
        },
    }

    # Try to get ORCID record email
    email = get_orcid_record_email(orcid_id, resp.get('access_token'))

    if email:
        record['user']['email'] = email

    return record


def account_setup(remote, token, resp):
    """Perform additional setup after user have been logged in.

    :param remote: The remote application.
    :param token: (str) The token value.
    :param resp: (dict) Response returned from api.
    """
    # Get ORCID record detail
    record = get_orcid_record(resp.get('orcid'), resp.get('access_token'))

    with db.session.begin_nested():
        # Retrieve ORCID from response.
        orcid_id = resp.get('orcid')

        # Set ORCID in extra_data.
        token.remote_account.extra_data = {'orcid': orcid_id, 'record': record}

        user = token.remote_account.user

        # Create user <-> external id link.
        oauth_link_external_id(user, {'id': orcid_id, 'method': 'orcid'})


def get_orcid_record(orcid_id, token, request_type=''):
    """Get ORCID record details.

    It returns a dictionary with the following structure:

    .. code-block:: python

        {
            'orcid-identifier': {
                'path': '0000-0000-0000-0000',
            },
            'person': {
                'name': {
                    'given-names': {
                        'value': 'John'
                    },
                    'family-name': {
                        'value': 'Doe'
                    },
                },
                'emails': {
                    'email': [{
                        'email': 'john.doe@test.com',
                    }],
                },
                ...
            },
            ...
        }


    :param orcid_id: (str) ORCID identifier.
    :param token: (str) Access token for querying API.
    :param request_type: (str) Request type for retreiving a specific section
    of the record.
    :returns: (dict|None) Dictionary of the Orcid record or none if something
    goes wrong
    """
    credentials = current_app.config.get('ORCID_APP_CREDENTIALS')
    api = orcid.PublicAPI(
        credentials['consumer_key'],
        credentials['consumer_secret'],
        sandbox=True,
    )
    try:
        return api.read_record_public(orcid_id, request_type, token)
    except RequestException:
        return None


def get_orcid_record_email(orcid_id, token):
    """Get ORCID record email.

    By default email address in ORCID is not publicly visible, so this
    information will not be found in almost records

    :param orcid_id: (str) ORCID identifier
    :param token: (str) access token for querying API
    :returns: (str|None) The email found or none
    """
    record = get_orcid_record(orcid_id, token, 'person')

    if not record or 'emails' not in record or not record['emails']['email']:
        return ''

    return record['emails']['email'][0]['email']
