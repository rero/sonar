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

"""Blueprint used for loading templates."""

from __future__ import absolute_import, print_function

import os
from datetime import datetime

from flask import current_app, request

from sonar.modules.api import SonarRecord
from sonar.modules.organisations.api import OrganisationRecord, current_organisation
from sonar.modules.utils import (
    change_filename_extension,
    format_date,
    is_ip_in_list,
    remove_trailing_punctuation,
)


def publication_statement_text(provision_activity):
    """Create publication statement from place, agent and date values."""
    # Only if provision activity is imported from field 269 (no statement,
    # but start date)
    if "statement" not in provision_activity:
        return format_date(provision_activity["startDate"])

    punctuation = {"bf:Place": " ; ", "bf:Agent": ", ", "Date": ", "}

    statement_with_language = {"default": ""}
    statement_type = None

    for statement in provision_activity["statement"]:
        labels = statement["label"]

        for label in labels:
            language = label.get("language", "default")

            statement_with_language.setdefault(language, "")

            if statement_with_language[language]:
                if statement_type == statement["type"]:
                    statement_with_language[language] += punctuation[statement_type]
                else:
                    if statement["type"] == "bf:Place":
                        statement_with_language[language] += " ; "
                    elif statement["type"] == "Date":
                        statement_with_language[language] += ", "
                    else:
                        statement_with_language[language] += " : "

            statement_with_language[language] += label["value"]
        statement_type = statement["type"]

    # date field: remove ';' and append
    for key, value in statement_with_language.items():
        value = remove_trailing_punctuation(value)
        statement_with_language[key] = value
    return statement_with_language


def get_file_links(file, record):
    """Return link data to preview and/or download the file.

    :param file: File record.
    :param record: Record.
    :returns: Dict containing the URL, the download URL and the type of link.
    """
    links = {"external": None, "preview": None, "download": None}

    # File is restricted, no link.
    if file["restriction"]["restricted"]:
        return links

    # File has an external url
    if (record["external_url"] or file.get("force_external_url", False)) and file.get("external_url"):
        links["external"] = file["external_url"]
        return links

    if not file.get("mimetype"):
        return links

    links["download"] = f"/documents/{record['pid']}/files/{file['key']}"

    if file["mimetype"] not in current_app.config.get("SONAR_APP_FILE_PREVIEW_MIMETYPES", []):
        return links
    # only markdown is supported
    if file["mimetype"] == "application/octet-stream":
        if os.path.splitext(file["key"])[-1] != ".md":
            return links
    links["preview"] = f"/documents/{record['pid']}/preview/{file['key']}"
    return links


def get_file_restriction(file, organisations, for_permission=True):
    """Check if current file can be displayed.

    :param file: File dict.
    :param organisations: List of organisations.
    :param for_permission: True if it is used to compute permissions.
    :returns: Object containing result as boolean and possibly embargo date.
    """

    def is_allowed_by_scope():
        """Check if file is fully restricted or only outside organisation.

        :returns: True if file is allowed.
        """
        if not file.get("restricted_outside_organisation"):
            return False

        if not organisations:
            return False

        # Logged user belongs to same organisation as record's organisation.
        for organisation in organisations:
            if current_organisation and current_organisation["pid"] == organisation["pid"]:
                return True

        # Check IP is allowed.
        ip_address = request.environ.get("X-Forwarded-For", request.remote_addr)
        # Take only the first IP, as X-Forwarded for gives the real IP + the
        # proxy IP.
        ip_address = ip_address.split(", ")[0]
        for organisation in organisations:
            if is_ip_in_list(ip_address, organisation.get("allowedIps", "").split("\n")):
                return True

        return False

    not_restricted = {"restricted": False, "date": None}

    # We are in admin, no restrictions are applied except for permissions.
    if (
        not for_permission
        and not request.args.get("view")
        and not request.view_args.get("view")
        and request.url_rule.rule != "/oai2d"
    ):
        return not_restricted

    # No specific access or specific access is open access
    if not file.get("access") or file["access"] == "coar:c_abf2":
        return not_restricted
    # Access is embargoed
    if file["access"] == "coar:c_f1cf":
        # No embargo date
        if not file.get("embargo_date"):
            return not_restricted
        try:
            embargo_date = datetime.strptime(file["embargo_date"], "%Y-%m-%d")
        except Exception:
            embargo_date = None

        # No embargo date or embargo date is in the past, file is accessible
        if not embargo_date or embargo_date <= datetime.now():
            return not_restricted

        # Restriction is full or file is not allowed in organisation.
        if not is_allowed_by_scope():
            return {"restricted": True, "date": embargo_date.strftime("%d/%m/%Y")}

    # Access is restricted
    if file["access"] == "coar:c_16ec" and not is_allowed_by_scope():
        return {"restricted": True, "date": None}

    return not_restricted


def has_external_urls_for_files(record):
    """Check if files point to external website.

    :param record: Current record.
    :returns: True if record's organisation is configured to point files to an
    external URL.
    """
    for organisation in record.get("organisation", []):
        organisation_pid = (
            SonarRecord.get_pid_by_ref_link(organisation["$ref"]) if organisation.get("$ref") else organisation["pid"]
        )

        return organisation_pid in current_app.config.get("SONAR_DOCUMENTS_ORGANISATIONS_EXTERNAL_FILES")

    return False


def get_thumbnail(file, record):
    """Get thumbnail from file.

    If file is restricted, a restricted image is returned. If no thumbnail
    found, a default image is returned.

    :param file: Dict of file from which thumbnail will be returned.
    :param record: Record object.
    :returns: URL to thumbnail file.
    """
    if file["restriction"]["restricted"]:
        return "static/images/restricted.png"

    key = change_filename_extension(file["key"], "jpg")

    matches = [file for file in record["_files"] if file["key"] == key]

    if not matches:
        return "static/images/no-image.png"

    return f"/documents/{record['pid']}/files/{key}"


def populate_files_properties(record):
    """Add restriction, link and thumbnail to file.

    :param record: Record object
    :param file: File dict
    """
    for file in record["_files"]:
        if file.get("type") == "file":
            file["restriction"] = get_file_restriction(file, get_organisations(record))
            file["thumbnail"] = get_thumbnail(file, record)
            file["links"] = get_file_links(file, record)


def get_organisations(record):
    """Get list of organisations with full data.

    :param record: Record object.
    """
    organisations = []
    for organisation in record.get("organisation", []):
        organisation_pid = (
            OrganisationRecord.get_pid_by_ref_link(organisation["$ref"])
            if organisation.get("$ref")
            else organisation["pid"]
        )
        organisations.append(OrganisationRecord.get_record_by_pid(organisation_pid))

    return organisations
