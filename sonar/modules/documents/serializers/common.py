# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Shared metadata extraction helpers for citation serializers (BibTeX, RIS)."""


def unwrap_metadata(record):
    """Return a record's metadata dict, keeping "pid"/"permalink" reachable.

    Most callers pass the document's own metadata (no "metadata" key), but a
    record can also arrive as an envelope {"metadata": {...}, "pid": ...,
    "permalink": ...} with those two fields as siblings rather than nested
    inside "metadata" (e.g. an ES search hit's _source). extract_url()
    needs "pid"/"permalink" to build the permalink, so they are copied into
    the returned dict when missing there, instead of being silently dropped.
    """
    metadata = record.get("metadata", record)
    if metadata is record:
        return metadata
    for key in ("pid", "permalink"):
        if key not in metadata and key in record:
            metadata = {**metadata, key: record[key]}
    return metadata


def extract_authors(metadata):
    """Return preferred names of contributors with the "cre" (creator) role.

    Meetings are events, not names, so a bf:Meeting agent is never returned
    even if it carries the "cre" role.
    """
    return [
        c["agent"]["preferred_name"]
        for c in metadata.get("contribution", [])
        if "cre" in c.get("role", [])
        and c.get("agent", {}).get("type") != "bf:Meeting"
        and c.get("agent", {}).get("preferred_name")
    ]


def extract_editors(metadata):
    """Return preferred names of contributors with the "edt" (editor) role.

    Meetings are events, not names, so a bf:Meeting agent is never returned
    even if it carries the "edt" role.
    """
    return [
        c["agent"]["preferred_name"]
        for c in metadata.get("contribution", [])
        if "edt" in c.get("role", [])
        and c.get("agent", {}).get("type") != "bf:Meeting"
        and c.get("agent", {}).get("preferred_name")
    ]


def extract_title(metadata):
    """Return the main title, combined with its subtitle if any."""
    for title_entry in metadata.get("title", []):
        if main_titles := title_entry.get("mainTitle", []):
            title = main_titles[0]["value"]
            subtitle = title_entry.get("subtitle", [{}])[0].get("value") if title_entry.get("subtitle") else None
            return f"{title}: {subtitle}" if subtitle else title
    return None


def extract_publication_info(metadata):
    """Return publication year, place and publisher from the "bf:Publication" activity."""
    year = place = publisher = None
    for activity in metadata.get("provisionActivity", []):
        if activity.get("type") != "bf:Publication":
            continue
        if activity.get("startDate"):
            year = activity["startDate"][:4]
        for stmt in activity.get("statement", []):
            label = stmt.get("label")
            value = label[0]["value"] if isinstance(label, list) and label else (label or {}).get("value", "")
            if stmt.get("type") == "bf:Place":
                place = value
            elif stmt.get("type") == "bf:Agent":
                publisher = value
        break
    return year, place, publisher


def extract_journal_info(metadata):
    """Return journal title, volume, issue and pages from the first "partOf" entry."""
    parts = metadata.get("partOf", [])
    if not parts:
        return None, None, None, None
    part = parts[0]
    journal = part.get("document", {}).get("title")
    return journal, part.get("numberingVolume"), part.get("numberingIssue"), part.get("numberingPages")


def extract_abstract(metadata):
    """Return the first non-empty abstract value."""
    for abstract in metadata.get("abstracts", []):
        if abstract.get("value"):
            return abstract["value"]
    return None


def extract_year(metadata):
    """Return the publication year.

    Prefer the "bf:Publication" activity start date, then fall back to the host
    document numbering year ("partOf"), where journal articles and other
    host-based types store their year (provisionActivity is optional for them).
    """
    year, _, _ = extract_publication_info(metadata)
    if year:
        return year
    for part in metadata.get("partOf", []):
        if part.get("numberingYear"):
            return part["numberingYear"]
    return None


def extract_dissertation(metadata):
    """Return (degree, granting institution, jury note) from the "dissertation" field."""
    dissertation = metadata.get("dissertation", {})
    return dissertation.get("degree"), dissertation.get("grantingInstitution"), dissertation.get("jury_note")


def extract_identifiers(metadata):
    """Return DOI, ISBN and ISSN, falling back to the host document (partOf).

    A journal's ISSN or a host book's ISBN is stored in partOf for articles
    and book chapters, not at the top level. The top level wins when present.
    """
    result = {}
    sources = [metadata.get("identifiedBy", [])]
    sources += [p.get("document", {}).get("identifiedBy", []) for p in metadata.get("partOf", [])]
    type_map = {"bf:Doi": "doi", "bf:Isbn": "isbn", "bf:Issn": "issn", "bf:IssnL": "issn"}
    for identifiers in sources:
        for identifier in identifiers:
            key = type_map.get(identifier.get("type"))
            if key and identifier.get("value") and key not in result:
                result[key] = identifier["value"]
    return result.get("doi"), result.get("isbn"), result.get("issn")


def extract_url(metadata):
    """Return the record's permanent link.

    Search hits already carry "permalink" in the ES source; for a single
    record it is computed from the PID.
    """
    if metadata.get("permalink"):
        return metadata["permalink"]
    if not metadata.get("pid"):
        return None
    from flask import request

    from sonar.modules.documents.api import DocumentRecord

    return DocumentRecord.get_permanent_link(request.host_url, metadata["pid"])
