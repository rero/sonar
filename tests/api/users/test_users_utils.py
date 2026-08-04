# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test users utils."""

from flask_mail import Mail

from sonar.modules.users.utils import send_welcome_email


def test_send_welcome_email_reset_link(app, user):
    """Test that the reset password link points to the UI application."""
    account = app.extensions["security"].datastore.find_user(email=user["email"])

    # The API application is mounted on `/api` by the WSGI dispatcher.
    with app.test_request_context(environ_overrides={"SCRIPT_NAME": "/api"}), Mail().record_messages() as outbox:
        send_welcome_email(user, account)

    assert 'href="http://localhost/lost-password/' in outbox[0].html
    assert "next=%2Forg" in outbox[0].html


def test_send_welcome_email(app, user, submitter, moderator, admin):
    """Test send welcome email."""
    datastore = app.extensions["security"].datastore

    # For user
    account = datastore.find_user(email=user["email"])

    with Mail().record_messages() as outbox:
        send_welcome_email(user, account)

        assert len(outbox) == 1
        assert outbox[0].html.find("Dear Orguser") != -1
        assert outbox[0].html.find("<li>Upload publications.</li>") == -1
        assert outbox[0].html.find("<li>Moderate submissions and edit document metadata.</li>") == -1
        assert outbox[0].html.find("<li>Manage the repository as an administrator.</li>") == -1

    # For submitter
    account = datastore.find_user(email=submitter["email"])

    with Mail().record_messages() as outbox:
        send_welcome_email(submitter, account)

        assert len(outbox) == 1
        assert outbox[0].html.find("Dear Orgsubmitter") != -1
        assert outbox[0].html.find("<li>Upload publications.</li>") != -1
        assert outbox[0].html.find("<li>Moderate submissions and edit document metadata.</li>") == -1
        assert outbox[0].html.find("<li>Manage the repository as an administrator.</li>") == -1

    # For moderator
    account = datastore.find_user(email=moderator["email"])

    with Mail().record_messages() as outbox:
        send_welcome_email(moderator, account)

        assert len(outbox) == 1
        assert outbox[0].html.find("Dear Orgmoderator") != -1
        assert outbox[0].html.find("<li>Upload publications.</li>") != -1
        assert outbox[0].html.find("<li>Moderate submissions and edit document metadata.</li>") != -1
        assert outbox[0].html.find("<li>Manage the repository as an administrator.</li>") == -1

    # For admin
    account = datastore.find_user(email=admin["email"])

    with Mail().record_messages() as outbox:
        send_welcome_email(admin, account)

        assert len(outbox) == 1
        assert outbox[0].html.find("Dear Orgadmin") != -1
        assert outbox[0].html.find("<li>Upload publications.</li>") != -1
        assert outbox[0].html.find("<li>Moderate submissions and edit document metadata.</li>") != -1
        assert outbox[0].html.find("<li>Manage the repository as an administrator.</li>") != -1
