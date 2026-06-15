# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Utils functions for user module."""

from flask_babel import _
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
    code = user_record["organisation"].get("code", "")
    plain_platform_name = "SONAR"
    pname = platform_name(user_record["organisation"])
    if pname:
        plain_platform_name = pname

    token = generate_reset_password_token(user)
    reset_link = url_for_security("reset_password", token=token, next=f"/{code}", _external=True)

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
