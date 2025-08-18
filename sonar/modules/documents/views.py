# Swiss Open Access Repository
# Copyright (C) 2021-2022 RERO
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

"""Blueprint definitions."""

import json

from flask import Blueprint, abort, current_app, render_template, request
from flask_babel import gettext as _
from invenio_i18n.ext import current_i18n
from invenio_records_ui.signals import record_viewed

from sonar.modules.collections.api import Record as CollectionRecord
from sonar.modules.documents.utils import (
    has_external_urls_for_files,
    populate_files_properties,
)
from sonar.modules.utils import (
    format_date,
    get_bibliographic_code_from_language,
    get_language_value,
)

from .utils import publication_statement_text

blueprint = Blueprint(
    "documents",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/",
)
"""Blueprint used for loading templates and static assets

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""


@blueprint.route("/<org_code:view>/search/documents")
def search(view):
    """Search results page."""
    # Load collection if arg is in URL.
    collection = None
    if request.args.get("collection_view"):
        collection = CollectionRecord.get_record_by_pid(request.args["collection_view"])

    return render_template("sonar/search.html", collection=collection, view=view)


def detail(pid, record, template=None, **kwargs):
    r"""Document detailed view.

    Sends record_viewed signal and renders template.

    :param pid: PID object.
    :param record: Record object.
    :param template: Template to render.
    :param \*\*kwargs: Additional view arguments based on URL rule.
    :returns: The rendered template.
    """
    # Add restriction, link and thumbnail to files
    if record.get("_files"):
        # Check if organisation's record forces to point file to an external
        # url
        record["external_url"] = has_external_urls_for_files(record)

        populate_files_properties(record)

    # Import is here to avoid a circular reference error.
    from sonar.modules.documents.serializers import google_scholar_v1, schemaorg_v1

    # Get schema org data
    schema_org_data = json.dumps(schemaorg_v1.transform_record(record["pid"], record))

    # Get scholar data
    google_scholar_data = google_scholar_v1.transform_record(record["pid"], record)

    # Resolve $ref properties
    record = record.resolve()

    # Record is masked
    if record.is_masked:
        abort(403)

    # Send signal when record is viewed
    record_viewed.send(
        current_app._get_current_object(),
        pid=pid,
        record=record,
    )

    return render_template(
        template,
        pid=pid,
        record=record,
        view=kwargs.get("view"),
        schema_org_data=schema_org_data,
        google_scholar_data=google_scholar_data,
    )


@blueprint.app_template_filter()
def title_format(title, language):
    """Format title for template.

    :param list title: List of titles.
    :param str language: Language to retreive title from.
    """
    language = get_bibliographic_code_from_language(language)

    preferred_languages = get_preferred_languages(language)

    def get_value(items):
        """Return the value for the given language."""
        if not items:
            return None

        for preferred_language in preferred_languages:
            for item in items:
                if item["language"] == preferred_language:
                    return item["value"]

        return items[0]["value"]

    output = []
    main_title = get_value(title.get("mainTitle", []))
    if main_title:
        output.append(main_title)

    subtitle = get_value(title.get("subtitle", []))
    if subtitle:
        output.append(subtitle)

    return " : ".join(output)


@blueprint.app_template_filter()
def create_publication_statement(provision_activity):
    """Create publication statement from place, agent and date values."""
    return publication_statement_text(provision_activity)


@blueprint.app_template_filter()
def file_size(size):
    """Return file size human readable.

    :param size: integer representing the size of the file.
    """
    return str(round(size / (1024 * 1024), 2)) + "Mb"


@blueprint.app_template_filter()
def part_of_format(part_of):
    """Format partOf property for display.

    :param part_of: Object representing partOf property
    """
    items = []
    document = part_of.get("document", {})
    if document.get("title"):
        items.append(document["title"])

    if "contribution" in document:
        formated_contribs = []
        first_contrib = document["contribution"][0]
        other_contribs = document["contribution"][1:]
        if other_contribs:
            formated_contribs.append(f" / {first_contrib} ; ")
            formated_contribs.append(" ; ".join(other_contribs))
        else:
            formated_contribs.append(f" / {first_contrib}")
        items.append("".join(formated_contribs))
    if items:
        items.append(". ")

    if "publication" in document and "statement" in document["publication"]:
        items.append("- {value}.".format(value=document["publication"]["statement"]))

    item = "".join(items).strip() if items else ""

    numbers = []
    if "numberingYear" in part_of:
        numbers.append(part_of["numberingYear"])

    if "numberingVolume" in part_of:
        numbers.append("{label} {value}".format(label=_("vol."), value=part_of["numberingVolume"]))

    if "numberingIssue" in part_of:
        numbers.append("{label} {value}".format(label=_("no."), value=part_of["numberingIssue"]))

    if "numberingPages" in part_of:
        numbers.append("{label} {value}".format(label=_("p."), value=part_of["numberingPages"]))
    if item and numbers:
        item += " - "
    if numbers:
        item += ", ".join(numbers)
    return item


@blueprint.app_template_filter()
def contributors(record, meeting=False):
    """Get ordered list of contributors."""
    if not record.get("contribution"):
        return []

    if list(filter(lambda d: "agent" in d, record.get("contribution"))):
        contributors = list(
            filter(
                lambda d: (d["agent"]["type"] == "bf:Meeting" if meeting else d["agent"]["type"] != "bf:Meeting"),
                record.get("contribution"),
            )
        )
    else:
        contributors = record.get("contribution")

    priorities = ["cre", "ctb", "dgs", "dgc", "edt", "prt"]

    return sorted(contributors, key=lambda i: priorities.index(i["role"][0]))


@blueprint.app_template_filter()
def abstracts(record):
    """Get ordered list of abstracts."""
    if not record.get("abstracts"):
        return []

    language = get_bibliographic_code_from_language(current_i18n.locale.language)
    preferred_languages = get_preferred_languages(language)

    abstract_language = []
    abstract_code = []
    for abstract in record["abstracts"]:
        if abstract["language"] in preferred_languages:
            abstract_language.append(abstract)
        else:
            abstract_code.append(abstract)
    abstract_sorted_language = sorted(
        abstract_language,
        key=lambda abstract: preferred_languages.index(abstract["language"]),
    )
    abstract_sorted_code = sorted(abstract_code, key=lambda abstract: abstract["language"])
    return abstract_sorted_language + abstract_sorted_code


@blueprint.app_template_filter()
def dissertation(record):
    """Get dissertation text."""
    if not record.get("dissertation"):
        return None

    dissertation_text = [record["dissertation"]["degree"]]

    # Dissertation has grantingInstitution or date
    if record["dissertation"].get("grantingInstitution") or record["dissertation"].get("date"):
        dissertation_text.append(": ")

        # Add grantingInstitution
        if record["dissertation"].get("grantingInstitution"):
            dissertation_text.append(record["dissertation"]["grantingInstitution"])

        # Add date
        if record["dissertation"].get("date"):
            dissertation_text.append(", {date}".format(date=format_date(record["dissertation"]["date"])))

    # Add jury note
    if record["dissertation"].get("jury_note"):
        dissertation_text.append(
            " ({label}: {note})".format(label=_("Jury note").lower(), note=record["dissertation"]["jury_note"])
        )

    return "".join(dissertation_text)


@blueprint.app_template_filter()
def contribution_text(contribution):
    """Display contribution row text.

    :param contribution: Dict representing the contribution.
    :returns: Formatted text.
    """
    data = [contribution["agent"]["preferred_name"]]

    # Meeting
    if contribution["agent"]["type"] == "bf:Meeting" and (meeting := meeting_text(contribution)):
        data.append(f"({meeting})")

    # Person
    if contribution["agent"]["type"] == "bf:Person" and contribution["role"][0] != "cre":
        data.append("({role})".format(role=_("contribution_role_{role}".format(role=contribution["role"][0])).lower()))  # noqa: INT002

    return " ".join(data)


@blueprint.app_template_filter()
def meeting_text(contribution):
    """Format the meeting field for display.

    :param contribution: Dict representing the contribution.
    :returns: Formatted text.
    """
    contrib = contribution["agent"]
    return " : ".join([contrib[key] for key in ["number", "date", "place"] if key in contrib])


@blueprint.app_template_filter()
def get_custom_field_label(record, custom_field_index):
    """Get the label of a custom field.

    :param record: Record object.
    :param custom_field_index: Index position of the custom field.
    :returns: The label found or None.
    """
    if record.get("organisation") and record["organisation"][0].get(
        "documentsCustomField" + str(custom_field_index), {}
    ).get("label"):
        return get_language_value(record["organisation"][0]["documentsCustomField" + str(custom_field_index)]["label"])

    return None


def get_language_from_bibliographic_code(language_code):
    """Return language code from bibliographic language.

    For example, get_language_code_from_bibliographic_language('ger') will
    return 'de'

    :param language_code: Bibliographic language
    :return str
    """
    languages_map = current_app.config.get("SONAR_APP_LANGUAGES_MAP")

    if language_code not in languages_map:
        raise Exception(f'Language code not found for "{language_code}"')
    code = languages_map.get(language_code)
    return code or ""

    return code


def get_preferred_languages(force_language=None):
    """Get the ordered list of preferred languages.

    :param forceLanguage: String, force a language to be the first.
    """
    preferred_languages = current_app.config.get("SONAR_APP_PREFERRED_LANGUAGES", []).copy()

    if force_language:
        preferred_languages.insert(0, force_language)

    return list(dict.fromkeys(preferred_languages))
