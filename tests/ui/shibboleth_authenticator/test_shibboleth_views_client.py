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

"""Test documents views."""

import os

from flask_login.utils import _create_identifier
from onelogin.saml2.auth import OneLogin_Saml2_Error


def test_login(app, client, valid_sp_configuration):
    """Test login view."""
    app.config.update(SHIBBOLETH_SERVICE_PROVIDER=valid_sp_configuration)

    # Test not existing identity provider
    assert client.get('/shibboleth/login/not_exists').status_code == 404

    # Test existing identity provider
    assert client.get('/shibboleth/login/idp').status_code == 302

    # Test misconfigured identity provider
    app.config.update(SHIBBOLETH_SERVICE_PROVIDER=dict(
        debug=True,
        strict=True,
        x509cert='./data/shibboleth/sp.pem',
        private_key='./data/shibboleth/sp.key'))

    assert client.get('/shibboleth/login/idp').status_code == 500


def test_authorized(monkeypatch, app, client, user_fixture, valid_attributes):
    """Test authorized view."""
    # Test unexisting identity provider
    app.config.update(SHIBBOLETH_SERVICE_PROVIDER=dict(
        debug=True,
        strict=True,
        x509cert='./data/shibboleth/sp.pem',
        private_key='./data/shibboleth/sp.key'))

    assert client.post('/shibboleth/authorized/not_exists').status_code == 404

    # Test exception in SAML authentication init
    monkeypatch.setattr(
        'sonar.modules.shibboleth_authenticator.views.client.init_saml_auth',
        lambda: Exception)
    assert client.post('/shibboleth/authorized/idp').status_code == 500

    class MockAuth(object):
        """Mock auth."""

        @staticmethod
        def process_response():
            """Process response for authentication."""
            raise OneLogin_Saml2_Error(message='')

        @staticmethod
        def get_errors():
            """Get auth errors."""
            return ['Error']

        @staticmethod
        def is_authenticated():
            """Is user authenticated."""
            return True

        @staticmethod
        def get_attributes():
            """Return auth attributes."""
            return valid_attributes

    # Test error in authentication process
    mock_auth = MockAuth()
    monkeypatch.setattr(
        'sonar.modules.shibboleth_authenticator.views.client.init_saml_auth',
        lambda req, remote_app: mock_auth)
    assert client.post('/shibboleth/authorized/idp').status_code == 400

    # Test when user is authenticated
    class MockUser(object):
        """Mock user."""

        def is_authenticated(self):
            """Return if user is authenticated."""
            return True

    mock_user = MockUser()
    monkeypatch.setattr(
        'sonar.modules.shibboleth_authenticator.views.client.current_user',
        mock_user)
    assert client.post('/shibboleth/authorized/idp').status_code == 400

    # Test errors in authentication (but no exception)
    mock_auth.process_response = lambda: None
    assert client.post(
        '/shibboleth/authorized/idp',
        data=dict(
            SAMLResponse=_load_file('valid_saml_response'))).status_code == 403

    # Test valid authentication
    mock_auth.get_errors = lambda: []

    from sonar.modules.shibboleth_authenticator.views.client import serializer
    next_url = '/test/redirect'
    state = serializer.dumps({
        'app': 'idp',
        'sid': _create_identifier(),
        'next': next_url,
    })

    assert client.post('/shibboleth/authorized/idp',
                       data=dict(
                           SAMLResponse=_load_file('valid_saml_response'),
                           RelayState=state)).status_code == 302

    # Test error in relay state token
    monkeypatch.setattr(
        'sonar.modules.shibboleth_authenticator.views.client'
        '._create_identifier',
        lambda: 'test')
    assert client.post('/shibboleth/authorized/idp',
                       data=dict(
                           SAMLResponse=_load_file('valid_saml_response'),
                           RelayState=state)).status_code == 400

    class MockRequest(object):
        """Mock request."""
        url = 'https://sonar.ch/test/page?parameter=test'
        host = 'sonar.ch'
        scheme = 'https'
        path = '/test/page'
        args = dict(parameter='test')
        form = dict(RelayState=None)

    mock_request = MockRequest()

    # Test error when no relay state token found
    monkeypatch.setattr(
        'sonar.modules.shibboleth_authenticator.views.client.request',
        mock_request)

    assert client.post(
        '/shibboleth/authorized/idp',
        data=dict(
            SAMLResponse=_load_file('valid_saml_response'))).status_code == 400


def _load_file(filename):
    """Load content of file."""
    filename = os.path.join(os.path.dirname(__file__), 'data', filename)

    if os.path.exists(filename):
        f = open(filename, 'r')
        content = f.read()
        f.close()
        return content

    return None
