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

"""Test CLI for importing documents."""

from click.testing import CliRunner

import sonar.modules.users.cli as Cli


def test_import_users(app, script_info, organisation):
    """Test import users."""
    runner = CliRunner()

    datastore = app.extensions['security'].datastore
    datastore.create_role(name='admin')

    # Test valid user import
    result = runner.invoke(Cli.import_users,
                           ['./tests/ui/users/data/valid.json'],
                           obj=script_info)
    user = datastore.find_user(email='rero.sonar+admin@gmail.com')
    assert user

    # Test already existing user
    result = runner.invoke(Cli.import_users,
                           ['./tests/ui/users/data/valid.json'],
                           obj=script_info)
    assert result.output.find(
        'User with email rero.sonar+admin@gmail.com already exists') != -1

    # Test if email not in user data
    result = runner.invoke(Cli.import_users,
                           ['./tests/ui/users/data/without_email.json'],
                           obj=script_info)
    assert result.output.find('Email not defined') != -1

    # Test if not roles defined in user data
    result = runner.invoke(Cli.import_users,
                           ['./tests/ui/users/data/without_roles.json'],
                           obj=script_info)
    user = datastore.find_user(email='rero.sonar+user@gmail.com')
    assert user
    assert user.roles[0].name == 'user'
