# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Mapping from a SONAR document record to a CSL-JSON item."""

import re

from .type_mapping import TYPE_MAPPING


def _get_title(record, lang=None):
    """Return the main title, optionally filtered by language."""
    for title_entry in record.get("title", []):
        main_titles = title_entry.get("mainTitle", [])
        if lang:
            for t in main_titles:
                if t.get("language") == lang:
                    return t["value"]
        if main_titles:
            return main_titles[0]["value"]
    return ""


def _get_subtitle(record, lang=None):
    """Return the subtitle, optionally filtered by language."""
    for title_entry in record.get("title", []):
        subtitles = title_entry.get("subtitle", [])
        if lang:
            for s in subtitles:
                if s.get("language") == lang:
                    return s["value"]
        if subtitles:
            return subtitles[0]["value"]
    return ""


def _get_full_title(record, lang=None):
    """Return title combined with subtitle when present."""
    title = _get_title(record, lang)
    subtitle = _get_subtitle(record, lang)
    return f"{title}: {subtitle}" if subtitle else title


#: Maps a SONAR contribution role to its CSL name variable. Roles with no
#: mapping (dgc, dgs, prt) are not surfaced in any of our vendored styles.
_ROLE_TO_CSL = {
    "cre": "author",
    "edt": "editor",
    "ctb": "contributor",
}


def _agent_to_csl_name(agent):
    """Return a CSL name entry for a contribution agent.

    Person names are free text following the library "Family, Given"
    convention, split so CSL can render initials (e.g. "Smith, J."). Corporate
    bodies (and any other agent type) are emitted as a single "literal" name
    and must never be split on a comma ("Company, Inc." is not a
    family/given pair).
    """
    preferred_name = agent.get("preferred_name", "")
    if agent.get("type") == "bf:Person":
        family, sep, given = preferred_name.partition(",")
        if sep:
            return {"family": family.strip(), "given": given.strip()}
    return {"literal": preferred_name}


def _get_names(record):
    """Return CSL name variables (author/editor/contributor) by role.

    Unlike a creator-or-editor fallback, every role present is kept: a
    document can have both an author and an editor at once. Meetings are
    events, not names, so they must not land in author/editor/contributor.
    """
    names = {}
    for contribution in record.get("contribution", []):
        agent = contribution.get("agent", {})
        if agent.get("type") == "bf:Meeting" or not agent.get("preferred_name"):
            continue
        csl_name = _agent_to_csl_name(agent)
        for role in contribution.get("role", []):
            if csl_variable := _ROLE_TO_CSL.get(role):
                names.setdefault(csl_variable, []).append(csl_name)
    return names


def _get_year(value):
    """Return a 4-digit year string from a free-text date, if valid."""
    year = (value or "")[:4]
    return year if year.isdigit() else None


def _get_date_parts(value):
    """Return CSL date-parts [year, month, day] from a "YYYY" or "YYYY-MM-DD" string.

    SONAR dates may carry the full day precision, and CSL styles (e.g. APA,
    MLA) render the month/day themselves for the document types where their
    convention calls for it, so the full date is passed through whenever
    available instead of truncating to the year.
    """
    if not (year := _get_year(value)):
        return None
    parts = [int(year)]
    rest = value[4:]
    if re.match(r"^-\d{2}-\d{2}$", rest):
        parts.extend(int(p) for p in rest[1:].split("-"))
    return parts


def _get_publication(record):
    """Return (date_parts, place, publisher) from the bf:Publication activity.

    provisionActivity is not required for most article and book chapter
    types, so missing date-parts fall back to partOf[0].numberingYear
    (year-only), then to dissertation.date for theses (which, like
    startDate, may carry full day precision).
    """
    place = None
    publisher = None
    date_parts = None
    for activity in record.get("provisionActivity", []):
        if activity.get("type") != "bf:Publication":
            continue
        date_parts = _get_date_parts(activity.get("startDate"))
        for stmt in activity.get("statement", []):
            label = stmt.get("label")
            value = label[0]["value"] if isinstance(label, list) and label else (label or {}).get("value")
            if stmt.get("type") == "bf:Place" and not place:
                place = value
            elif stmt.get("type") == "bf:Agent" and not publisher:
                publisher = value
        break

    if not date_parts:
        parts = record.get("partOf", [])
        # numberingYear is year-only by definition, unlike the other sources.
        year = _get_year(parts[0].get("numberingYear")) if parts else None
        date_parts = [int(year)] if year else None
    if not date_parts:
        date_parts = _get_date_parts(record.get("dissertation", {}).get("date"))

    return date_parts, place, publisher


def _get_part_of(record):
    """Return (journal_title, volume, issue, pages) from partOf."""
    parts = record.get("partOf", [])
    if not parts:
        return None, None, None, None
    part = parts[0]
    return (
        part.get("document", {}).get("title"),
        part.get("numberingVolume"),
        part.get("numberingIssue"),
        part.get("numberingPages"),
    )


def _get_identifiers(record):
    """Return DOI/ISBN/ISSN values found in identifiedBy."""
    csl_key_by_type = {"bf:Doi": "DOI", "bf:Isbn": "ISBN", "bf:Issn": "ISSN"}
    identifiers = {}
    for identifier in record.get("identifiedBy", []):
        csl_key = csl_key_by_type.get(identifier.get("type"))
        if csl_key and csl_key not in identifiers:
            identifiers[csl_key] = identifier["value"]
    return identifiers


def _get_url(record, host_url):
    """Return the document's permanent link (ARK if available), if a pid is known.

    Styles already prefer DOI over URL when both are present, so this is a
    plain fallback link to the document on SONAR, not a duplicate display.
    """
    if not record.get("pid") or not host_url:
        return None
    from sonar.modules.documents.api import DocumentRecord

    return DocumentRecord.get_permanent_link(host_url, record["pid"])


def _get_edition(record):
    """Return the edition designation, if any."""
    return record.get("editionStatement", {}).get("editionDesignation", {}).get("value")


def _get_series(record):
    """Return (name, number) from the first series entry, if any."""
    if series := record.get("series", []):
        return series[0].get("name"), series[0].get("number")
    return None, None


def _get_meeting(record):
    """Return (name, place, date) from a bf:Meeting contribution, if any."""
    for contribution in record.get("contribution", []):
        agent = contribution.get("agent", {})
        if agent.get("type") == "bf:Meeting":
            return agent.get("preferred_name"), agent.get("place"), agent.get("date")
    return None, None, None


def _get_number_of_pages(record):
    """Return the page count extracted from the free-text extent field.

    extent has no fixed format (e.g. "103 p", "XII, 250 p."), so this takes
    the first integer found rather than assuming a specific pattern.
    """
    extent = record.get("extent") or ""
    match = re.search(r"\d+", extent)
    return match.group() if match else None


def record_to_csl(record, lang=None, host_url=None):
    """Return a CSL-JSON item dict for the given SONAR document record.

    :param record: Document record dict.
    :param lang: Optional ISO 639-1 language code used to pick the matching
        title/subtitle translation. It does not affect the citation style's
        own rendering language, which stays tied to the citation style.
    :param host_url: Optional base URL used to build the document's
        permanent link. Passed in explicitly, rather than read from Flask's
        request context, so this module stays usable outside of a request
        (CLI tools, background jobs, tests without a request context).
    """
    csl_type = TYPE_MAPPING.get(record.get("documentType"), "document")
    item = {
        "id": record.get("pid") or "item",
        "type": csl_type,
        "title": _get_full_title(record, lang),
    }
    item.update(_get_names(record))

    date_parts, place, publisher = _get_publication(record)
    if date_parts:
        item["issued"] = {"date-parts": [date_parts]}
    if place:
        item["publisher-place"] = place
    if publisher:
        item["publisher"] = publisher

    journal, volume, issue, pages = _get_part_of(record)
    if journal:
        item["container-title"] = journal
    if volume:
        item["volume"] = volume
    if issue:
        item["issue"] = issue
    if pages:
        item["page"] = pages

    item.update(_get_identifiers(record))

    if url := _get_url(record, host_url):
        item["URL"] = url

    if edition := _get_edition(record):
        item["edition"] = edition

    series_name, series_number = _get_series(record)
    if series_name:
        item["collection-title"] = series_name
    if series_number:
        item["collection-number"] = series_number

    meeting_name, meeting_place, meeting_date = _get_meeting(record)
    if meeting_name:
        item["event"] = meeting_name
    if meeting_place:
        item["event-place"] = meeting_place
    if meeting_date_parts := _get_date_parts(meeting_date):
        item["event-date"] = {"date-parts": [meeting_date_parts]}

    if number_of_pages := _get_number_of_pages(record):
        item["number-of-pages"] = number_of_pages

    if csl_type == "thesis":
        dissertation = record.get("dissertation", {})
        if dissertation.get("degree"):
            item["genre"] = dissertation["degree"]
        if dissertation.get("grantingInstitution"):
            item["publisher"] = dissertation["grantingInstitution"]

    return item
