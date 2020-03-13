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

"""Utils functions for application."""

import re

from flask import current_app
from invenio_mail.api import TemplatedMessage
from wand.color import Color
from wand.image import Image


def create_thumbnail_from_file(file_path, mimetype):
    """Create a thumbnail from given file path and return image blob.

    :param file_path: Full path of file.
    :param mimetype: Mime type of the file.
    """
    # Thumbnail can only be done from images or PDFs.
    if not mimetype.startswith('image/') and mimetype != 'application/pdf':
        raise Exception(
            'Cannot create thumbnail from file {file} with mimetype'
            ' "{mimetype}", only images and PDFs are allowed'.format(
                file=file_path, mimetype=mimetype))

    # For PDF, we take only the first page
    if mimetype == 'application/pdf':
        # Append [0] force to take only the first page
        file_path = file_path + '[0]'

    # Create the image thumbnail
    with Image(filename=file_path) as img:
        img.format = 'jpg'
        img.background_color = Color('white')
        img.alpha_channel = 'remove'
        img.resize(200, 300)

        return img.make_blob()


def change_filename_extension(filename, extension):
    """Return filename with the given extension."""
    matches = re.search(r'(.*)\..*$', filename)

    if matches is None:
        raise Exception(
            '{filename} is not a valid filename'.format(filename=filename))

    return matches.group(1) + '.' + extension


def send_email(recipients, subject, template, ctx=None, **kwargs):
    """Send email."""
    lang = kwargs.get('lang', 'en')

    template = '{template}.{lang}.txt'.format(template=template, lang=lang)

    msg = TemplatedMessage(
        template_body=template,
        sender=current_app.config.get('SECURITY_EMAIL_SENDER'),
        recipients=recipients,
        subject=subject,
        ctx=ctx)
    current_app.extensions['mail'].send(msg)


def get_switch_aai_providers():
    """Return the list of available SWITCHaai providers."""
    providers = []
    for provider, data in current_app.config.get(
            'SHIBBOLETH_IDENTITY_PROVIDERS').items():
        # Don't take providers flagged as dev in production mode
        if current_app.config.get('ENV') != 'development' and data.get(
                'dev', False):
            continue

        providers.append(provider)

    return providers
