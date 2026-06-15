# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Signals for users."""

from sonar.modules.users.api import UserRecord, datastore


def user_registered_handler(app, user, confirm_token):
    """Called when a new user is registered.

    :param app: App context.
    :param user: User account.
    """
    # Add a default role to user
    role = datastore.find_role(UserRecord.ROLE_USER)
    datastore.add_role_to_user(user, role)
    datastore.commit()


def add_full_name(sender=None, record=None, json=None, index=None, **kwargs):
    """Add full name field in index.

    :param sender: Sender of the signal.
    :param record: Record to index.
    :param json: Indexed data.
    :param index: Index where data is sent.
    """
    # Takes care only about users indexing
    if not index.startswith("users"):
        return

    json["full_name"] = f"{json['first_name']} {json['last_name']}"
