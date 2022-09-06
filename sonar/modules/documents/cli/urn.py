# -*- coding: utf-8 -*-
#
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
from invenio_files_rest.models import ObjectVersion
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.urn import Urn
from sonar.snl.ftp import SNLRepository


@click.group()
def urn():
    """URN specific commands."""


@urn.command('urn-for-loaded-records')
@with_appcontext
def urn_for_loaded_records():
    """Generate and register urns for loaded records."""
    for idx, document in enumerate(Urn.get_documents_to_generate_urns(), 1):
        click.secho(
            f'\t{idx}: generate urn code for pid: {document.pid}', fg='green')
        Urn.create_urn(document)


@urn.command('register-urn-pids')
@with_appcontext
def register_urn_identifiers():
    """Register URN identifiers with status NEW."""
    urn_codes = Urn.get_unregistered_urns()
    if count := len(urn_codes):
        click.secho(f'Found  {count} urns to register', fg='yellow')
        registered = 0
        for urn_code in urn_codes:
            if Urn.register_urn_pid(urn=urn_code):
                click.secho(
                    f'\turn code: {urn_code} successfully registered', fg='green')
                registered += 1
            else:
                click.secho(
                    f'\turn code: {urn_code} still pending', fg='red')

        click.secho(f'Found  {count} urns to register', fg='yellow')
        click.secho(
            f'Number URNs successfully registered: {registered}', fg='green')
        click.secho(
            f'Number URNs pending: {count-registered}', fg='red')
    else:
        click.secho('No urns found to register', fg='yellow')


@urn.command('snl-upload-file')
@click.argument('urn_code')
@click.argument('filepath')
@with_appcontext
def snl_upload_file(urn_code, filepath):
    r"""Upload file on the SNL server via FTP for REGISTRED urn.

    Ex. invenio documents urn snl-upload-file 006-72 ~/my_dir/a.pdf
    :param urn_code: urn code of the document. Ex. 006-72
    :param filepath: local filepath of file to upload
    """
    snl_repository = SNLRepository(
        host=current_app.config.get('SONAR_APP_FTP_SNL_HOST'),
        user=current_app.config.get('SONAR_APP_FTP_SNL_USER'),
        password=current_app.config.get('SONAR_APP_FTP_SNL_PASSWORD'),
        directory=current_app.config.get('SONAR_APP_FTP_SNL_PATH')
    )
    snl_repository.connect()

    dnb_base_urn = current_app.config.get('SONAR_APP_URN_DNB_BASE_URN')
    urn = ''.join([dnb_base_urn, urn_code])

    try:
        urn_identifier = PersistentIdentifier.get('urn', urn)
    except PIDDoesNotExistError:
        click.secho(f'Persistent identifier does not exist for {urn}',
                    fg='red')
        return

    # check urn is registred
    if not urn_identifier.is_registered():
        click.secho(f'Urn: {urn} is not registred', fg='red')
        return

    # create directory for urn
    snl_repository.make_dir(urn)

    # move to the urn directory
    snl_repository.cwd(urn)

    # upload file
    try:
        snl_repository.upload_file(filepath)
        click.secho(
            f'Successfully uploaded file {os.path.basename(filepath)}.',
            fg='green')
    except Exception as exception:
        click.secho(str(exception), fg='red')

    # print email template
    template_emailSNL = current_app.config.get('SONAR_APP_SNL_EMAIL_TEMPLATE')

    pid = PersistentIdentifier.get(Urn.urn_pid_type, urn)
    record = DocumentRecord.get_record(pid.object_uuid)

    click.secho('Template of email to send to SNL:', fg='green')
    with open(template_emailSNL, 'r') as file:
        email_txt = file.read()
        email_txt = email_txt.replace("<URN>", urn)
        email_txt = email_txt.replace(
            "<URL>", f'https://sonar.ch/global/documents/{record.get("pid")}'
        )
        click.secho(email_txt)


@urn.command('replace-pdf-file')
@click.argument('urn_code')
@click.argument('filename')
@click.argument('filepath')
@with_appcontext
def replace_pdf_file(urn_code, filename, filepath):
    r"""Replace file in document with REGISTRED URN.

    Delete pdf file from record and upload new file.
    Ex. invenio documents urn replace-pdf-file 006-72 a.pdf ~/my_dir/b.pdf
    :param urn_code: urn code of the document. Ex. 006-72
    :param filename: filename of the file to delete
    :param filepath: filepath of the file to upload
    """
    dnb_base_urn = current_app.config.get('SONAR_APP_URN_DNB_BASE_URN')
    urn = ''.join([dnb_base_urn, urn_code])

    try:
        urn_identifier = PersistentIdentifier.get('urn', urn)
    except PIDDoesNotExistError:
        click.secho(f'Persistent identifier does not exist for {urn}',
                    fg='red')
        return

    # check urn is registred
    if not urn_identifier.is_registered():
        click.secho(f'Urn: {urn} is not registred', fg='red')
        return

    pid = PersistentIdentifier.get(Urn.urn_pid_type, urn)
    record = DocumentRecord.get_record(pid.object_uuid)

    try:
        f = record.files[filename]
    except KeyError:
        click.secho(f'File {filename} does not exist for urn: {urn}', fg='red')
        return

    if f.mimetype == 'application/pdf' and f.is_head:
        # get metadata of file to remove.
        pdf_dump = f.dumps()

        # remove file (soft delete)
        ObjectVersion.delete(bucket=f.bucket, key=f.key)

        # upload file
        new_filename = os.path.basename(filepath)
        with open(filepath, 'rb') as file:
            content = file.read()
        record.add_file(content, new_filename)

        # set file order from metadata of deleted file
        record.files[new_filename]['order'] = pdf_dump.get('order')

        record.commit()
        record.reindex()
        db.session.commit()

        click.secho(f'Removed file: {f.key}', fg='green')
        click.secho(f'Uploaded file: {filepath}', fg='green')
    else:
        click.secho(f'File {filename} is not pdf or is not head', fg='red')


@urn.command('snl-list-files')
@with_appcontext
def snl_list_files():
    """List files uploaded on SNL server."""
    snl_repository = SNLRepository(
        host=current_app.config.get('SONAR_APP_FTP_SNL_HOST'),
        user=current_app.config.get('SONAR_APP_FTP_SNL_USER'),
        password=current_app.config.get('SONAR_APP_FTP_SNL_PASSWORD'),
        directory=current_app.config.get('SONAR_APP_FTP_SNL_PATH')
    )
    snl_repository.connect()
    snl_repository.list()
