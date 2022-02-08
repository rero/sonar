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

"""Utils functions for user module."""

from flask_babelex import _
from flask_security import url_for_security
from flask_security.recoverable import generate_reset_password_token

from sonar.modules.organisations.utils import platform_name
from sonar.modules.utils import send_email


def send_welcome_email(user_record, user):
    """Send this email when user is created from backend.

    :param user_record: User record.
    :param user: User account.
    """
    user_record = user_record.replace_refs()
    code = user_record['organisation'].get('code', '')
    plain_platform_name = 'SONAR'
    pname = platform_name(user_record['organisation'])
    if pname:
        plain_platform_name = pname

    token = generate_reset_password_token(user)
    reset_link = url_for_security(
        'reset_password',
        token=token,
        next=f'/{code}',
        _external=True
    )

    send_email(
        [user_record['email']],
        f'{_("Welcome to")} {plain_platform_name}',
        'users/email/welcome', {
            'user': user_record,
            'reset_link': reset_link,
            'platform_name': plain_platform_name
        }
    )
