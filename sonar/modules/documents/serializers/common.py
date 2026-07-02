# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Shared metadata extraction helpers for citation serializers (BibTeX, RIS)."""


def extract_authors(metadata):
    """Return preferred names of contributors with the "cre" (creator) role."""
    return [
        c["agent"]["preferred_name"]
        for c in metadata.get("contribution", [])
        if "cre" in c.get("role", []) and c.get("agent", {}).get("preferred_name")
    ]


def extract_editors(metadata):
    """Return preferred names of contributors with the "edt" (editor) role."""
    return [
        c["agent"]["preferred_name"]
        for c in metadata.get("contribution", [])
        if "edt" in c.get("role", []) and c.get("agent", {}).get("preferred_name")
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
