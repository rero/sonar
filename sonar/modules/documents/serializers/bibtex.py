# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""BibTeX serializer."""

import re

from invenio_records_rest.serializers.base import SerializerMixinInterface

from .common import (
    THESIS_DOCUMENT_TYPES,
    extract_abstract,
    extract_authors,
    extract_dissertation,
    extract_editors,
    extract_host_publication,
    extract_identifiers,
    extract_journal_info,
    extract_publication_info,
    extract_title,
    extract_url,
    extract_year,
    unwrap_metadata,
)

# Mapping from COAR resource types to BibTeX entry types, mirroring the COAR
# classification already established in
# sonar/modules/documents/serializers/schemas/schemaorg.py. Types with no
# clean BibTeX equivalent (images, video, software, maps, ...) fall back to
# "misc" rather than a close-but-wrong entry type.
# https://purl.org/coar/resource_type
_COAR_TO_BIBTEX = {
    "coar:c_2f33": "book",
    "coar:c_3248": "incollection",
    "coar:c_c94f": "misc",
    "coar:c_5794": "inproceedings",
    "coar:c_18cp": "inproceedings",
    "coar:c_6670": "misc",
    "coar:c_18co": "misc",
    "coar:c_f744": "proceedings",
    "coar:c_ddb1": "misc",
    "coar:c_3e5a": "article",
    "coar:c_beb9": "article",
    "coar:c_6501": "article",
    "coar:c_998f": "article",
    "coar:c_dcae04bc": "article",
    "coar:c_8544": "misc",
    "non_textual_object": "misc",
    "coar:c_8a7e": "misc",
    "coar:c_ecc8": "misc",
    "coar:c_12cc": "misc",
    "coar:c_18cc": "misc",
    "coar:c_18cw": "misc",
    "coar:c_5ce6": "misc",
    "coar:c_15cd": "misc",
    "coar:c_2659": "misc",
    "coar:c_0640": "misc",
    "coar:c_2cd9": "misc",
    "coar:c_2fe3": "misc",
    "coar:c_816b": "article",
    "coar:c_93fc": "techreport",
    "coar:c_18ww": "techreport",
    "coar:c_18wz": "techreport",
    "coar:c_18wq": "techreport",
    "coar:c_186u": "techreport",
    "coar:c_18op": "techreport",
    "coar:c_ba1f": "techreport",
    "coar:c_18hj": "techreport",
    "coar:c_18ws": "techreport",
    "coar:c_18gh": "techreport",
    # Only PHD thesis has a matching entry type. Every other level
    # rides on "mastersthesis", whose "type" field replaces the printed label.
    "coar:c_46ec": "mastersthesis",
    "coar:c_7a1f": "mastersthesis",
    "coar:c_db06": "phdthesis",
    "coar:c_bdcc": "mastersthesis",
    "habilitation_thesis": "mastersthesis",
    "advanced_studies_thesis": "mastersthesis",
    "other_thesis": "mastersthesis",
    "coar:c_8042": "techreport",
    "coar:c_1843": "misc",
    "coar:R60J-J5BD": "misc",
    "coar:c_ba08": "misc",
}


def _bibtex_entry_type(doc_type):
    """Return BibTeX entry type for a COAR document type."""
    return _COAR_TO_BIBTEX.get(doc_type, "misc")


def _bibtex_key(metadata):
    """Generate a BibTeX cite key from first author (or editor), year and pid.

    The pid keeps keys unique across independent calls (e.g. paginated
    exports), which share no collision state.
    """
    names = extract_authors(metadata) or extract_editors(metadata)
    last_name = names[0].split(",")[0].strip() if names else "unknown"
    # BibTeX keys cannot contain whitespace: collapse multi-word last names
    # like "van der Berg" into a single token.
    name = re.sub(r"\s+", "", last_name)
    base = f"{name}{extract_year(metadata) or ''}"
    pid = metadata.get("pid")
    return f"{base}-{pid}" if pid else base


_BIBTEX_ESCAPE = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}
_BIBTEX_ESCAPE_RE = re.compile("|".join(re.escape(char) for char in _BIBTEX_ESCAPE))


def _bibtex_escape(value):
    r"""Escape LaTeX special characters in a free-text field value.

    A single-pass regex substitution is required: replacing characters one
    at a time (e.g. "\\" then "{") would re-escape the braces just inserted
    by the backslash replacement, producing double-escaped output.
    """
    return _BIBTEX_ESCAPE_RE.sub(lambda match: _BIBTEX_ESCAPE[match.group()], str(value))


def _bibtex_field(name, value, escape=True):
    """Return a formatted BibTeX field line."""
    text = _bibtex_escape(value) if escape else str(value)
    return f"  {name:<12} = {{{text}}}"


def serialize_record_to_bibtex(metadata):
    """Serialize a document metadata dict to a BibTeX entry string."""
    doc_type = metadata.get("documentType", "")
    entry_type = _bibtex_entry_type(doc_type)
    is_thesis = doc_type in THESIS_DOCUMENT_TYPES
    key = _bibtex_key(metadata)

    fields = []

    # Authors
    if authors := extract_authors(metadata):
        fields.append(_bibtex_field("author", " and ".join(authors)))

    # Editors (only if no authors)
    editors = extract_editors(metadata)
    if editors and not authors:
        fields.append(_bibtex_field("editor", " and ".join(editors)))

    # Title
    if title := extract_title(metadata):
        fields.append(_bibtex_field("title", title))

    _, place, publisher = extract_publication_info(metadata)
    # A hosted item's publisher/address are those of its container, which does
    # not always state its place: the record's own is then kept.
    host_place, host_publisher = extract_host_publication(metadata)
    if host_publisher:
        place, publisher = host_place or place, host_publisher
    if year := extract_year(metadata):
        fields.append(_bibtex_field("year", year))
    if place:
        fields.append(_bibtex_field("address", place))

    # Thesis: "school" is the publisher slot of a thesis entry.
    # "type" states the precise degree.
    if is_thesis:
        degree, institution, _ = extract_dissertation(metadata)
        if school := institution or publisher:
            fields.append(_bibtex_field("school", school))
        if degree:
            fields.append(_bibtex_field("type", degree))
    elif publisher:
        fields.append(_bibtex_field("publisher", publisher))

    # Host document: journal for articles, book/proceedings title otherwise
    journal, volume, issue, pages = extract_journal_info(metadata)
    if journal:
        host_field = "booktitle" if entry_type in ("incollection", "inproceedings", "proceedings") else "journal"
        fields.append(_bibtex_field(host_field, journal))
    if volume:
        fields.append(_bibtex_field("volume", volume))
    if issue:
        fields.append(_bibtex_field("number", issue))
    if pages:
        fields.append(_bibtex_field("pages", pages))

    # Identifiers
    doi, isbn, issn, other_identifiers = extract_identifiers(metadata)
    if doi:
        fields.append(_bibtex_field("doi", doi, escape=False))
    if isbn:
        fields.append(_bibtex_field("isbn", isbn, escape=False))
    if issn:
        fields.append(_bibtex_field("issn", issn, escape=False))
    # BibTeX field names must be unique within an entry: number repeated
    # "other" identifier labels instead of overwriting the earlier field.
    label_counts = {}
    for label, value in other_identifiers:
        label_counts[label] = label_counts.get(label, 0) + 1
        field_name = label if label_counts[label] == 1 else f"{label}{label_counts[label]}"
        fields.append(_bibtex_field(field_name, value, escape=False))

    # Abstract
    if abstract := extract_abstract(metadata):
        fields.append(_bibtex_field("abstract", abstract))

    # Permalink
    if url := extract_url(metadata):
        fields.append(_bibtex_field("url", url, escape=False))

    lines = [f"@{entry_type}{{{key},"] + [f"{f}," for f in fields] + ["}"]
    return "\n".join(lines)


class BibTeXSerializer(SerializerMixinInterface):
    """BibTeX serializer for document records."""

    mimetype = "application/x-bibtex"

    def serialize(self, pid, record, links_factory=None):
        """Serialize a single record to BibTeX."""
        return serialize_record_to_bibtex(unwrap_metadata(record))

    def serialize_search(self, pid_fetcher, search_result, links=None, item_links_factory=None):
        """Serialize search results to BibTeX (one entry per hit)."""
        entries = [serialize_record_to_bibtex(unwrap_metadata(hit["_source"])) for hit in search_result["hits"]["hits"]]
        return "\n\n".join(entries)
