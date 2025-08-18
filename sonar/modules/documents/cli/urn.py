# Swiss Open Access Repository
# Copyright (C) 2022 RERO
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

"""URN specific CLI commands."""

import os

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.dnb import DnbServerError, DnbUrnService
from sonar.modules.documents.urn import Urn
from sonar.snl.ftp import SNLRepository


@click.group()
def urn():
    """URN specific commands."""


@urn.command()
@click.argument("urn")
@with_appcontext
def get(urn):
    """Get a URN information.

    :param urn: str - URN identifier
    """
    p = PersistentIdentifier.get("urn", urn)
    if not p.is_registered():
        click.secho(f"error: bad pid status ({p.status})", fg="red")
    dnb_urn = DnbUrnService.get(urn)
    dnb_urls = DnbUrnService.get_urls(urn)
    document = DocumentRecord.get_record(p.object_uuid)
    url = DnbUrnService.get_url(document)
    if dnb_urls["items"][0]["url"] != url:
        click.secho(
            f"error: DNB has the wrong url ({dnb_urls['items'][0]['url']} != {url})",
            fg="red",
        )
    if len(dnb_urls["items"]) > 1:
        urls = [item["url"] for item in dnb_urls["items"]]
        click.secho(f"error: DNB has more than one urls ({', '.join(urls)})", fg="red")

    click.echo(f"urn created: {dnb_urn['created']}")
    click.echo(f"urn modified: {dnb_urn['lastModified']}")
    dnb_url = dnb_urls["items"][0]
    click.echo(f"url created: {dnb_url['created']}")
    click.echo(f"url modified: {dnb_url['lastModified']}")
    click.echo(f"url: {url}")


@urn.command()
@with_appcontext
def create():
    """Create and register urns for loaded records."""
    idx = 0
    for idx, document in enumerate(Urn.get_documents_to_generate_urns(), 1):
        click.secho(f"\t{idx}: generate urn code for pid: {document['pid']}", fg="green")
        Urn.create_urn(document)
        document.commit()
        db.session.commit()
        document.reindex()
        Urn.register_urn_code_from_document(document)
    click.secho(f"{idx} URN created.", fg="green")


@urn.command()
@with_appcontext
def register():
    """Register urns for reserved URN pids."""
    query = PersistentIdentifier.query.filter_by(pid_type="urn").filter_by(status=PIDStatus.RESERVED)
    for idx, pid in enumerate(query.all()):
        doc = DocumentRecord.get_record(pid.object_uuid)
        click.secho(f"Registering document (pid: {doc['pid']})", fg="yellow")
        Urn.register_urn_code_from_document(doc)
    click.secho(f"{idx} URN registered.", fg="green")


@urn.command("snl-upload-file")
@click.argument("urn_code")
@with_appcontext
def snl_upload_file(urn_code):
    r"""Upload file on the SNL server via FTP for REGISTRED urn.

    Ex. invenio documents urn snl-upload-file 006-72 ~/my_dir/a.pdf
    :param urn_code: urn code of the document. Ex. 006-72
    :param filepath: local filepath of file to upload
    """
    try:
        pid = PersistentIdentifier.get(Urn.urn_pid_type, urn_code)
    except PIDDoesNotExistError:
        click.secho("Error: URN does not exists.")
        return

    if not pid.is_registered():
        click.secho("Error: the given urn is not registered.")
        return

    doc = DocumentRecord.get_record(pid.object_uuid)
    if not doc:
        click.secho("Error: the given urn is not linked to any document.")
        return

    files = [file for file in doc.files if file.get("type") == "file"]
    if not files:
        click.secho("Error: the document does not contains any files.")
        return

    snl_repository = SNLRepository(
        host=current_app.config.get("SONAR_APP_FTP_SNL_HOST"),
        user=current_app.config.get("SONAR_APP_FTP_SNL_USER"),
        password=current_app.config.get("SONAR_APP_FTP_SNL_PASSWORD"),
        directory=current_app.config.get("SONAR_APP_FTP_SNL_PATH"),
    )
    snl_repository.connect()

    dnb_base_urn = current_app.config.get("SONAR_APP_FTP_SNL_PATH")
    urn_dir = "/".join([dnb_base_urn, urn_code.split(":")[-1]])

    # create directory for urn
    snl_repository.make_dir(urn_dir)

    # upload file
    for _file in files:
        try:
            snl_repository.upload_file(_file.file.uri, os.path.join(urn_dir, _file.key))
            click.secho(f"Successfully uploaded file {os.path.basename(_file.key)}.", fg="green")
        except Exception as exception:
            click.secho(str(exception), fg="red")

    # print email template
    template_email_snl = current_app.config.get("SONAR_APP_SNL_EMAIL_TEMPLATE")

    click.secho("Template of email to send to SNL:", fg="green")
    with open(template_email_snl) as file:
        email_txt = file.read()
        email_txt = email_txt.replace("<URN>", urn_code)
        email_txt = email_txt.replace("<URL>", f"https://sonar.ch/global/documents/{doc.get('pid')}")
        click.secho(email_txt)


@urn.command("snl-list-files")
@with_appcontext
def snl_list_files():
    """List files uploaded on SNL server."""
    snl_repository = SNLRepository(
        host=current_app.config.get("SONAR_APP_FTP_SNL_HOST"),
        user=current_app.config.get("SONAR_APP_FTP_SNL_USER"),
        password=current_app.config.get("SONAR_APP_FTP_SNL_PASSWORD"),
        directory=current_app.config.get("SONAR_APP_FTP_SNL_PATH"),
    )
    snl_repository.connect()
    snl_repository.client.walktree(".", lambda x: click.secho(x), lambda x: click.secho(x), lambda x: click.secho(x))


@urn.command()
@click.argument("urn")
@click.argument("successor_urn")
@with_appcontext
def successor(urn, successor_urn):
    """Set a successor for a given run.

    :param urn: str - URN identifier
    :param successor_urn: str - Sucessor URN identifier
    """
    try:
        DnbUrnService().set_successor(urn, successor_urn)
        click.secho("Added successfully a successor.", fg="green")
    except DnbServerError as err:
        click.secho(str(err), fg="red")
