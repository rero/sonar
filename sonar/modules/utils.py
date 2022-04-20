# -*- coding: utf-8 -*-
#
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

"""Utils functions for application."""

import datetime
import re

from flask import abort, current_app, g, request
from invenio_i18n.ext import current_i18n
from invenio_mail.api import TemplatedMessage
from netaddr import IPAddress, IPGlob, IPNetwork, IPSet
from wand.color import Color
from wand.image import Image

from sonar.theme.webpack import theme


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
        img.border('#dee2e6', 3, 3)
        img.transform(resize='200x')

        return img.make_blob()


def change_filename_extension(filename, extension):
    """Return filename with the given extension.

    Additionally, the original extension is appended to the filename, to avoid
    conflict with other files having the same name (without extension).
    """
    matches = re.search(r'(.*)\.(.*)$', filename)

    if matches is None:
        raise Exception(
            '{filename} is not a valid filename'.format(filename=filename))

    return '{name}-{source_extension}.{extension}'.format(
        name=matches.group(1),
        source_extension=matches.group(2),
        extension=extension)


def send_email(recipients, subject, template, ctx=None, html=True, lang='en'):
    """Send email."""
    email_type = 'html' if html else 'txt'

    template = '{template}/{lang}.{type}'.format(template=template,
                                                 lang=lang,
                                                 type=email_type)
    msg = TemplatedMessage(
        template_body=template if not html else None,
        template_html=template if html else None,
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


def remove_trailing_punctuation(data,
                                punctuation=',',
                                spaced_punctuation=':;/-'):
    """Remove trailing punctuation from data.

    The punctuation parameter list the
    punctuation characters to be removed
    (preceded by a space or not).

    The spaced_punctuation parameter list the
    punctuation characters needing one or more preceding space(s)
    in order to be removed.
    """
    punctuation = punctuation.replace('.', r'\.').replace('-', r'\-')
    spaced_punctuation = \
        spaced_punctuation.replace('.', r'\.').replace('-', r'\-')
    return re.sub(r'([{0}]|\s+[{1}])$'.format(punctuation, spaced_punctuation),
                  '', data.rstrip()).rstrip()


def get_current_language():
    """Return the current selected locale."""
    return current_i18n.locale.language


def get_view_code():
    """Return view code corresponding to organisation.

    :returns: View code as string.
    """
    if g.get('organisation'):
        return g.organisation['code']

    return current_app.config.get('SONAR_APP_DEFAULT_ORGANISATION')


def format_date(date):
    """Format date to given format.

    :param date: String representing the date.
    :param format: Format of the ouput.
    :returns: The formatted date.
    """
    # Complete date (eg. 2020-12-31)
    if re.match(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}$', date):
        return datetime.datetime.strptime(date,
                                          '%Y-%m-%d').strftime('%d.%m.%Y')

    return date


def get_specific_theme():
    """Return the webpack entry for the current organisation.

    :returns: String representing the webpack entry. Default to `global`.
    """
    if g.get('organisation', {}).get('isDedicated'):
        theme_name = '{organisation}-theme'.format(
            organisation=g.organisation['pid'])

        if theme.entry.get(theme_name):
            return '{theme}.css'.format(theme=theme_name)

    return 'global-theme.css'


def is_ip_in_list(ip_address, addresses_list):
    """Check if address IP is in list.

    :param ip_address: Address IP to check
    :param addresses_list: Range of IP, network or simple IP.
    :returns: True if given IP is in list.
    """
    if not isinstance(addresses_list, list):
        raise Exception('Given parameter is not a list.')

    ip_set = IPSet()

    for ip_range in addresses_list:
        try:
            # It's a glob
            if '*' in ip_range or '-' in ip_range:
                ip_set.add(IPGlob(ip_range))
            # It's a network
            elif '/' in ip_range:
                ip_set.add(IPNetwork(ip_range))
            # Simple IP
            else:
                ip_set.add(IPAddress(ip_range))
        except Exception:
            pass

    try:
        return ip_address in ip_set
    except Exception:
        return False


def chunks(records, size):
    """Yield chunks from records.

    :param list records: Full records list.
    :param int size: Size of chunks.
    """
    for i in range(0, len(records), size):
        yield records[i:i + size]


def remove_html(content):
    """Remove html tags from content."""
    return re.sub(re.compile('<.*?>'), '', content)


def has_custom_resource(resource_type):
    """Check if user's organisation has a custom resource.

    :param resource_type: Type of resource.
    :returns: True if resource is custom for organisation.
    """
    # Mandatory to import current_organisation here, to avoid an error during
    # tests.
    from sonar.modules.organisations.api import current_organisation

    if not current_organisation or not current_organisation.get('code'):
        return False

    return current_app.config.get('SONAR_APP_ORGANISATION_CONFIG').get(
        current_organisation['code'], {}).get(resource_type)


def get_language_value(values,
                       locale=None,
                       value_field='value',
                       language_field='language'):
    """Return the value corresponding to the locale.

    :params values: List of values with the language.
    :params locale: Two digit locale to find.
    :params value_field: Name of the property containing the value.
    :params language_field: Name of the property containing the language.
    :returns: The value associated with the language.
    """
    if not values:
        return None

    locale = locale or get_current_language()
    locale = get_bibliographic_code_from_language(locale)

    for value in values:
        if value[language_field] == locale:
            return value[value_field]

    return values[0][value_field]


def get_bibliographic_code_from_language(language_code):
    """Return bibliographic language code from language.

    For example, get_bibliographic_code_from_language("de") will
    return "ger".

    :param language_code: Bibliographic language.
    :returns: The bibliographic code corresponding to language.
    """
    for key, lang in current_app.config.get('SONAR_APP_LANGUAGES_MAP').items():
        if lang == language_code:
            return key

    raise Exception(f'Language code not found for "{language_code}"')


def get_current_ip():
    """Get current IP address.

    :returns: Current IP address.
    :rtype: str
    """
    ip_address = request.environ.get('X-Forwarded-For', request.remote_addr)
    # Take only the first IP, as X-Forwarded for gives the real IP + the
    # proxy IP.
    return ip_address.split(', ')[0]


def get_ips_list(ranges):
    """Get the IP addresses list from a list of ranges.

    :param list ranges: List of ranges.
    :returns: List of IP addresses.
    :rtype: list of cidr ips
            (https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing)
    """
    ip_set = IPSet()

    for ip_range in ranges:
        try:
            # It's a glob
            if '*' in ip_range or '-' in ip_range:
                ip_set.add(IPGlob(ip_range))
            # It's a network
            elif '/' in ip_range:
                ip_set.add(IPNetwork(ip_range))
            # Simple IP
            else:
                ip_set.add(IPAddress(ip_range))
        except Exception:
            pass

    return [str(ip.cidr) for ip in ip_set.iter_cidrs()]


def file_download_ui(pid, record, _record_file_factory=None, **kwargs):
    """File download view for a given record.

    RERO: Invenio do not pass pid and record to the files permission factory:
    we need to overwrite
    Plug this method into your ``RECORDS_UI_ENDPOINTS`` configuration:

    .. code-block:: python

        RECORDS_UI_ENDPOINTS = dict(
            recid=dict(
                # ...
                route='/records/<pid_value>/files/<filename>',
                view_imp='invenio_records_files.utils:file_download_ui',
                record_class='invenio_records_files.api:Record',
            )
        )

    If ``download`` is passed as a querystring argument, the file is sent as an
    attachment.

    :param pid: The :class:`invenio_pidstore.models.PersistentIdentifier`
        instance.
    :param record: The record metadata.
    """
    from invenio_files_rest.views import ObjectResource, check_permission
    from invenio_records_files.utils import record_file_factory

    from .permissions import files_permission_factory
    _record_file_factory = _record_file_factory or record_file_factory
    # Extract file from record.
    fileobj = _record_file_factory(
        pid, record, kwargs.get('filename')
    )

    if not fileobj:
        abort(404)

    obj = fileobj.obj
    # Check permissions
    # Invenio do not pass pid and record to the files permission factory:
    # we need to overwrite
    check_permission(files_permission_factory(
        obj,
        'object-read',
        pid,
        record
    ))
    if not obj.is_head:
        check_permission(
            files_permission_factory(obj, 'object-read-version', pid, record),
            hidden=False
        )

    # Send file.
    return ObjectResource.send_object(
        obj.bucket, obj,
        expected_chksum=fileobj.get('checksum'),
        logger_data={
            'bucket_id': obj.bucket_id,
            'pid_type': pid.pid_type,
            'pid_value': pid.pid_value,
        },
        as_attachment=('download' in request.args)
    )
