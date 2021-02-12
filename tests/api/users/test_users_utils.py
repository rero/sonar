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

"""Test users utils."""

from flask_mail import Mail

from sonar.modules.users.utils import send_welcome_email


def test_send_welcome_email(app, user, submitter, moderator, admin):
    """Test send welcome email."""
    datastore = app.extensions['security'].datastore

    # For user
    account = datastore.find_user(email=user['email'])

    with Mail().record_messages() as outbox:
        send_welcome_email(user, account)

        assert len(outbox) == 1
        assert outbox[0].html.find('Dear Orguser') != -1
        assert outbox[0].html.find('<li>Upload publications.</li>') == -1
        assert outbox[0].html.find(
            '<li>Moderate submissions and edit document metadata.</li>') == -1
        assert outbox[0].html.find(
            '<li>Manage the repository as an administrator.</li>') == -1

    # For submitter
    account = datastore.find_user(email=submitter['email'])

    with Mail().record_messages() as outbox:
        send_welcome_email(submitter, account)

        assert len(outbox) == 1
        assert outbox[0].html.find('Dear Orgsubmitter') != -1
        assert outbox[0].html.find('<li>Upload publications.</li>') != -1
        assert outbox[0].html.find(
            '<li>Moderate submissions and edit document metadata.</li>') == -1
        assert outbox[0].html.find(
            '<li>Manage the repository as an administrator.</li>') == -1

    # For moderator
    account = datastore.find_user(email=moderator['email'])

    with Mail().record_messages() as outbox:
        send_welcome_email(moderator, account)

        assert len(outbox) == 1
        assert outbox[0].html.find('Dear Orgmoderator') != -1
        assert outbox[0].html.find('<li>Upload publications.</li>') != -1
        assert outbox[0].html.find(
            '<li>Moderate submissions and edit document metadata.</li>') != -1
        assert outbox[0].html.find(
            '<li>Manage the repository as an administrator.</li>') == -1

    # For admin
    account = datastore.find_user(email=admin['email'])

    with Mail().record_messages() as outbox:
        send_welcome_email(admin, account)

        assert len(outbox) == 1
        assert outbox[0].html.find('Dear Orgadmin') != -1
        assert outbox[0].html.find('<li>Upload publications.</li>') != -1
        assert outbox[0].html.find(
            '<li>Moderate submissions and edit document metadata.</li>') != -1
        assert outbox[0].html.find(
            '<li>Manage the repository as an administrator.</li>') != -1
