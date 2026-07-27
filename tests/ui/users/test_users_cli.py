# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test CLI for importing documents."""

from click.testing import CliRunner

from sonar.modules.users import cli


def test_import_users(app, script_info, organisation, roles):
    """Test import users."""
    runner = CliRunner()

    datastore = app.extensions["security"].datastore

    # Test valid user import
    result = runner.invoke(cli.import_users, ["./tests/ui/users/data/valid.json"], obj=script_info)
    user = datastore.find_user(email="rero.sonar+admin@gmail.com")
    assert user

    # Test already existing user
    result = runner.invoke(cli.import_users, ["./tests/ui/users/data/valid.json"], obj=script_info)
    assert result.output.find("User with email rero.sonar+admin@gmail.com already exists") != -1

    # Test if email not in user data
    result = runner.invoke(cli.import_users, ["./tests/ui/users/data/without_email.json"], obj=script_info)
    assert result.output.find("Email not defined") != -1

    # Test if not roles defined in user data
    result = runner.invoke(cli.import_users, ["./tests/ui/users/data/without_roles.json"], obj=script_info)
    user = datastore.find_user(email="rero.sonar+user@gmail.com")
    assert user
    assert user.roles[0].name == "user"
