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

"""Blueprint for handling Shibboleth callbacks."""

from __future__ import absolute_import, print_function

from flask import Blueprint, abort, current_app, redirect, request
from flask_login import current_user, logout_user
from flask_login.utils import _create_identifier
from invenio_oauthclient.handlers import set_session_next_url
from itsdangerous import BadData, TimedJSONWebSignatureSerializer
from onelogin.saml2.auth import OneLogin_Saml2_Error
from werkzeug.local import LocalProxy

from ..auth import init_saml_auth
from ..handlers import authorized_signup_handler
from ..utils import get_safe_redirect_target, prepare_flask_request

blueprint = Blueprint('shibboleth_authenticator',
                      __name__,
                      url_prefix='/shibboleth')

serializer = LocalProxy(lambda: TimedJSONWebSignatureSerializer(
    current_app.config['SECRET_KEY'],
    expires_in=current_app.config['SHIBBOLETH_STATE_EXPIRES'],
))


@blueprint.route('/login/<remote_app>', methods=['GET', 'POST'])
def login(remote_app):
    """
    Redirect user to remote application for authentication.

    This function redirects the user to the IdP for authorization. After having
    authorized the IdP redirects the user back to this web application as
    configured in your ``saml_path``.

    :param remote_app: (str) Identity provider key.
    :returns: (flask.Response) Return redirect response to IdP or abort in case
                        of failure.
    """
    if remote_app not in current_app.config['SHIBBOLETH_IDENTITY_PROVIDERS']:
        return abort(404)

    # Store next parameter in state token
    next_param = get_safe_redirect_target(arg='next')
    if not next_param:
        next_param = '/'
    state_token = serializer.dumps({
        'app': remote_app,
        'next': next_param,
        'sid': _create_identifier()
    })

    # req = prepare_flask_request(request)
    try:
        auth = init_saml_auth(request, remote_app)
    except Exception:
        return abort(500)

    return redirect(auth.login(state_token))


@blueprint.route('/authorized/<remote_app>', methods=['GET', 'POST'])
def authorized(remote_app=None):
    """
    Authorize handler callback.

    This function is called when the user is redirected from the IdP to the
    web application. It handles the authorization.

    :param remote_app: (str) Identity provider key
    :returns: (flask.Response) Return redirect response or abort in case of
    failure.
    """
    # Logout user if already logged
    if current_user.is_authenticated:
        logout_user()

    # Configuration not found for given identity provider
    if remote_app not in current_app.config['SHIBBOLETH_IDENTITY_PROVIDERS']:
        return abort(404)

    # Init SAML auth
    req = prepare_flask_request(request)
    try:
        auth = init_saml_auth(req, remote_app)
    except Exception:
        return abort(500)

    # Process response
    errors = []
    try:
        auth.process_response()
    except OneLogin_Saml2_Error:
        return abort(400)

    errors = auth.get_errors()

    if not errors and auth.is_authenticated():
        if 'RelayState' in request.form:
            # Get state token stored in RelayState
            state_token = request.form['RelayState']
            try:
                if not state_token:
                    raise ValueError
                # Check authenticity and integrity of state and decode the
                # values.
                state = serializer.loads(state_token)
                # Verify that state is for this session, app and that next
                # parameter have not been modified.
                if (state['sid'] != _create_identifier() or
                        state['app'] != remote_app):
                    raise ValueError
                # Store next url
                set_session_next_url(remote_app, state['next'])
            except (ValueError, BadData):
                if current_app.config.get('OAUTHCLIENT_STATE_ENABLED',
                                          True) or (not (current_app.debug or
                                                         current_app.testing)):
                    return abort(400)
        return authorized_signup_handler(auth, remote_app)
    return abort(403)
