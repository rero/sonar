# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Utils functions for user module."""

from urllib.parse import urlencode

from flask_babel import _
from invenio_accounts.utils import default_reset_password_link_func

from sonar.modules.organisations.utils import platform_name
from sonar.modules.utils import send_email


def send_welcome_email(user_record, user):
    """Send this email when user is created from backend.

    :param user_record: User record.
    :param user: User account.
    """
    user_record = user_record.replace_refs()
    code = user_record["organisation"].get("code", "")
    plain_platform_name = "SONAR"
    pname = platform_name(user_record["organisation"])
    if pname:
        plain_platform_name = pname

    # The link points to the UI application, as the Flask-Security views are
    # not registered on the API application.
    _token, reset_link = default_reset_password_link_func(user)
    reset_link = f"{reset_link}?{urlencode({'next': f'/{code}'})}"

    send_email(
        [user_record["email"]],
        f"{_('Welcome to')} {plain_platform_name}",
        "users/email/welcome",
        {
            "user": user_record,
            "reset_link": reset_link,
            "platform_name": plain_platform_name,
        },
    )
