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

"""Utils for application."""

from flask import current_app
from invenio_mail.api import TemplatedMessage


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
