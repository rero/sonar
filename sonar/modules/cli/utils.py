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

"""Utils commands."""

import json
import pathlib
import shutil
import sys
from os.path import dirname, join

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_db import db
from invenio_files_rest.models import Location
from invenio_oauth2server.cli import process_scopes, process_user
from invenio_oauth2server.models import Client, Token
from invenio_records_rest.utils import obj_or_import_string
from invenio_search.cli import search_version_check
from invenio_search.proxies import current_search
from werkzeug.local import LocalProxy
from werkzeug.security import gen_salt

from sonar.modules.api import SonarRecord

_datastore = LocalProxy(lambda: current_app.extensions["security"].datastore)


@click.group()
def utils():
    """Utils commands."""


@utils.command()
@click.option("--force", is_flag=True, default=False)
@with_appcontext
@search_version_check
def es_init(force):
    """Initialize registered templates, aliases and mappings."""
    # TODO: to remove once it is fixed in invenio-search module
    click.secho("Putting templates...", fg="green", bold=True, file=sys.stderr)
    with click.progressbar(
        current_search.put_templates(ignore=[400] if force else None),
        length=len(current_search.templates),
    ) as item:
        for response in item:
            item.label = response
    click.secho("Creating indexes...", fg="green", bold=True, file=sys.stderr)
    with click.progressbar(
        current_search.create(ignore=[400] if force else None),
        length=len(current_search.mappings),
    ) as item:
        for name, response in item:
            item.label = name


@utils.command()
@with_appcontext
def clear_files():
    """Remove all files and delete directory from all locations."""
    for location in Location.query.all():
        try:
            shutil.rmtree(location.uri)
        except Exception:
            click.secho(f"Directory {location.uri} cannot be cleaned", fg="yellow")

    click.secho("Finished", fg="green")


@utils.command("export")
@click.option("-p", "--pid-type", "pid_type", default="doc")
@click.option("-s", "--serializer", "serializer_key", default="export")
@click.option("-o", "--output-dir", "output_dir", required=True, type=click.File("w"))
@with_appcontext
def export(pid_type, serializer_key, output_dir):
    """Export records for the given record type.

    :param pid_type: record type
    :param output_dir: Output directory
    """
    click.secho(f'Export "{pid_type}" records in {output_dir.name}')

    try:
        # Get the correct record class
        record_class = SonarRecord.get_record_class_by_pid_type(pid_type)

        if not record_class:
            raise Exception(f'No record class found for type "{pid_type}"')

        # Load the serializer
        serializer_class = current_app.config.get("SONAR_APP_EXPORT_SERIALIZERS", {}).get(pid_type)

        serializer = obj_or_import_string(serializer_class)() if serializer_class else None

        pids = record_class.get_all_pids()
        records = []

        # Create ouptut directory if not exists
        if pids:
            pathlib.Path(output_dir.name).mkdir(mode=0o755, parents=True, exist_ok=True)

        for pid in pids:
            record = record_class.get_record_by_pid(pid)

            record = serializer.dump(record) if serializer else record.dumps()

            for file in record.get("files", []):
                if file.get("uri"):
                    target_path = join(output_dir.name, pid, file["key"])
                    pathlib.Path(dirname(target_path)).mkdir(mode=0o755, parents=True, exist_ok=True)
                    shutil.copyfile(file["uri"], target_path)
                    file.pop("uri")
                    file["path"] = f"./{pid}/{file['key']}"

            records.append(record)

        if records:
            # Write data
            output_file = join(output_dir.name, "data.json")
            with open(output_file, "w") as f:
                f.write(json.dumps(records))

        click.secho("Finished", fg="green")

    except Exception as err:
        click.secho(f"An error occured during export: {err}", fg="red")


def create_personal(name, user_id, scopes=None, is_internal=False, access_token=None):
    """Create a personal access token.

    A token that is bound to a specific user and which doesn't expire, i.e.
    similar to the concept of an API key.

    :param name: Client name.
    :param user_id: User ID.
    :param scopes: The list of permitted scopes. (Default: ``None``)
    :param is_internal: If ``True`` it's a internal access token.
            (Default: ``False``)
    :param access_token: personalized access_token.
    :returns: A new access token.
    """
    with db.session.begin_nested():
        scopes = " ".join(scopes) if scopes else ""

        client = Client(
            name=name,
            user_id=user_id,
            is_internal=True,
            is_confidential=False,
            _default_scopes=scopes,
        )
        client.gen_salt()

        if not access_token:
            access_token = gen_salt(current_app.config.get("OAUTH2SERVER_TOKEN_PERSONAL_SALT_LEN"))
        token = Token(
            client_id=client.client_id,
            user_id=user_id,
            access_token=access_token,
            expires=None,
            _scopes=scopes,
            is_personal=True,
            is_internal=is_internal,
        )
        db.session.add(client)
        db.session.add(token)

    return token


@utils.command()
@click.option("-n", "--name", required=True)
@click.option("-u", "--user", required=True, callback=process_user, help="User ID or email.")
@click.option("-s", "--scope", "scopes", multiple=True, callback=process_scopes)
@click.option("-i", "--internal", is_flag=True)
@click.option(
    "-t",
    "--access_token",
    "access_token",
    required=False,
    help="personalized access_token.",
)
@with_appcontext
def token_create(name, user, scopes, internal, access_token):
    """Create a personal OAuth token."""
    if user:
        token = create_personal(
            name,
            user.id,
            scopes=scopes,
            is_internal=internal,
            access_token=access_token,
        )
        db.session.commit()
        click.secho(token.access_token, fg="blue")
    else:
        click.secho("No user found", fg="red")
