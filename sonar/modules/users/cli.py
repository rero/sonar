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

"""Click command-line interface for user management."""

from __future__ import absolute_import, print_function

import json

import click
from click.exceptions import ClickException
from flask import current_app
from flask.cli import with_appcontext
from flask_security.confirmable import confirm_user
from werkzeug.local import LocalProxy

from ..users.api import UserRecord

datastore = LocalProxy(lambda: current_app.extensions["security"].datastore)


@click.group()
def users():
    """Users CLI commands."""


@users.command("import")
@click.argument("infile", type=click.File("r"))
@with_appcontext
def import_users(infile):
    """Import users."""
    click.secho(f"Importing users from {infile.name}")

    data = json.load(infile)
    for user_data in data:
        try:
            email = user_data.get("email")

            # No email found in user's data, account cannot be created
            if not email:
                raise ClickException("Email not defined")

            user = datastore.find_user(email=email)

            # User already exists, skip account creation
            if user:
                raise ClickException(f"User with email {email} already exists")

            password = user_data.get(
                "password",
                "$pbkdf2-sha512$25000$29ubk1KqFUJorTXmHAPAmA$ooj0RJyHyinmZw"
                "/.pNMXne8p70X/BDoX5Ypww24OIguSWEo3y.KT6hiwxwHS5OynZNkgnLvf"
                "R3m1mNVfsHgfgA",
            )
            del user_data["password"]

            if not user_data.get("role"):
                user_data["role"] = UserRecord.ROLE_USER

            if not datastore.find_role(user_data["role"]):
                datastore.create_role(name=user_data["role"])
                datastore.commit()

            # Create account and activate it
            datastore.create_user(email=email, password=password, roles=[user_data["role"]])
            datastore.commit()
            user = datastore.find_user(email=email)
            confirm_user(user)
            datastore.commit()

            click.secho(
                f"User {email} with ID #{user.id} created successfully",
                fg="green",
            )

            # Create user resource
            user = UserRecord.create(user_data, dbcommit=True)
            user.reindex()

        except Exception as error:
            click.secho(
                f"User {user_data} could not be imported: {error}",
                fg="red",
            )

    click.secho("Finished", fg="green")
