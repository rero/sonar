# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2025 RERO
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

"""Jinja filters."""

import markdown
from flask import current_app, url_for
from flask_wiki.markdown_ext import BootstrapExtension

from sonar.modules.organisations.utils import platform_name
from sonar.modules.utils import get_language_value


def nl2br(string):
    r"""Replace \n to <br>."""
    return string.replace("\n", "<br>")


def language_value(values, locale=None, value_field="value", language_field="language"):
    """Get the value of a field corresponding to the current language.

    :params values: List of values with the language.
    :params locale: Two digit locale to find.
    :params value_field: Name of the property containing the value.
    :params language_field: Name of the property containing the language.
    :returns: The value corresponding to the current language.
    """
    return get_language_value(values, locale, value_field, language_field)


def get_admin_record_detail_url(record):
    r"""Return the frontend application URL for a record detail.

    :param record: Record object.
    :returns: Absolute URL to recrod detail.
    :rtype: str
    """
    url = [
        current_app.config.get("SONAR_APP_ANGULAR_URL")[:-1],
        "records",
        record.index_name,
        "detail",
        record.pid.pid_value,
    ]
    return "/".join(url)


def markdown_filter(content):
    """Markdown filter.

    :param str content: Content to convert
    :returns: HTML corresponding to markdown
    :rtype: str
    """
    return markdown.markdown(
        content,
        extensions=[
            BootstrapExtension(),
            "codehilite",
            "fenced_code",
            "toc",
            "meta",
            "tables",
        ],
    )


def organisation_platform_name(org):
    """Get organisation platform name."""
    name = platform_name(org)
    return name or current_app.config.get("THEME_SITENAME")


def favicon(org):
    """Fav icon for current organisation."""
    if (
        org
        and "_files" in org
        and (
            favicon := list(
                filter(
                    lambda d: d["mimetype"] in ["image/x-icon", "image/vnd.microsoft.icon"],
                    org["_files"],
                )
            )
        )
    ):
        return {
            "mimetype": favicon[0]["mimetype"],
            "url": url_for(
                "invenio_records_ui.org_files",
                pid_value=org.get("pid"),
                filename=favicon[0]["key"],
            ),
        }
    return None
