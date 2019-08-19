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

"""Click command-line interface for user management."""

from __future__ import absolute_import, print_function

import json

import click
from click.exceptions import ClickException
from flask import current_app
from flask.cli import with_appcontext
from flask_security.confirmable import confirm_user
from invenio_accounts.ext import hash_password
from werkzeug.local import LocalProxy

from ..users.api import UserRecord

datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)


@click.group()
def users():
    """Users CLI commands."""


@users.command('import')
@click.argument('infile', type=click.File('r'))
@with_appcontext
def import_users(infile):
    """Import users."""
    click.secho('Importing users from {file}'.format(file=infile))

    data = json.load(infile)
    for user_data in data:
        try:
            email = user_data.get('email')

            # No email found in user's data, account cannot be created
            if not email:
                raise ClickException('Email not defined')

            user = datastore.find_user(email=email)

            # User already exists, skip account creation
            if user:
                raise ClickException(
                    'User with email {email} already exists'.format(
                        email=email))

            password = user_data.get('password', '123456')
            password = hash_password(password)
            del user_data['password']

            roles = user_data.get('roles', []).copy()
            if not roles or not isinstance(roles, list):
                roles = []

            # Create account and activate it
            datastore.create_user(email=email, password=password, roles=roles)
            datastore.commit()
            user = datastore.find_user(email=email)
            confirm_user(user)
            datastore.commit()

            # Store account ID in user resource
            user_data['user_id'] = user.id

            click.secho(
                'User {email} with ID #{id} created successfully'.format(
                    email=email, id=user.id),
                fg='green')

            # Create user resource
            user = UserRecord.create(user_data, dbcommit=True)
            user.reindex()

        except Exception as error:
            click.secho(
                'User {user} could not be imported: {error}'.format(
                    user=user_data, error=str(error)),
                fg='red')

    click.secho('Finished', fg='green')
