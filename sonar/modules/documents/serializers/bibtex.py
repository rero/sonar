# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""BibTeX serializer."""

from invenio_records_rest.serializers.base import SerializerMixinInterface

from .common import (
    extract_abstract,
    extract_authors,
    extract_editors,
    extract_journal_info,
    extract_publication_info,
    extract_title,
)

# Mapping from COAR resource types to BibTeX entry types.
# https://purl.org/coar/resource_type
_COAR_TO_BIBTEX = {
    "coar:c_2f33": "book",  # book
    "coar:c_3248": "book",  # book part → use book as fallback
    "coar:c_5794": "article",  # journal article
    "coar:c_18cp": "inproceedings",  # conference paper
    "coar:c_6670": "incollection",  # book chapter
    "coar:c_816b": "mastersthesis",  # master thesis
    "coar:c_db06": "phdthesis",  # doctoral thesis
    "coar:c_7a1f": "phdthesis",  # thesis
    "coar:c_bdcc": "mastersthesis",  # master thesis (other)
    "coar:c_46ec": "phdthesis",  # thesis (generic)
    "coar:c_8042": "techreport",  # technical report
}


def _bibtex_entry_type(doc_type):
    """Return BibTeX entry type for a COAR document type."""
    return _COAR_TO_BIBTEX.get(doc_type, "misc")


def _bibtex_key(metadata):
    """Generate a BibTeX cite key from first author and year."""
    authors = extract_authors(metadata)
    name = authors[0].split(",")[0].strip() if authors else "unknown"
    year, _, _ = extract_publication_info(metadata)
    return f"{name}{year or ''}"


def _bibtex_field(name, value):
    """Return a formatted BibTeX field line."""
    return f"  {name:<12} = {{{value}}}"


def serialize_record_to_bibtex(metadata):
    """Serialize a document metadata dict to a BibTeX entry string."""
    doc_type = metadata.get("documentType", "")
    entry_type = _bibtex_entry_type(doc_type)
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

    # Publication info
    year, place, publisher = extract_publication_info(metadata)
    if year:
        fields.append(_bibtex_field("year", year))
    if place:
        fields.append(_bibtex_field("address", place))
    if publisher:
        fields.append(_bibtex_field("publisher", publisher))

    # Journal / partOf
    journal, volume, issue, pages = extract_journal_info(metadata)
    if journal:
        fields.append(_bibtex_field("journal", journal))
    if volume:
        fields.append(_bibtex_field("volume", volume))
    if issue:
        fields.append(_bibtex_field("number", issue))
    if pages:
        fields.append(_bibtex_field("pages", pages))

    # Identifiers
    for identifier in metadata.get("identifiedBy", []):
        if identifier.get("type") == "bf:Doi":
            fields.append(_bibtex_field("doi", identifier["value"]))
        elif identifier.get("type") in ("bf:Isbn", "bf:Issn"):
            fields.append(_bibtex_field("isbn", identifier["value"]))

    # Abstract
    if abstract := extract_abstract(metadata):
        fields.append(_bibtex_field("abstract", abstract))

    lines = [f"@{entry_type}{{{key},"] + [f"{f}," for f in fields] + ["}"]
    return "\n".join(lines)


class BibTeXSerializer(SerializerMixinInterface):
    """BibTeX serializer for document records."""

    mimetype = "application/x-bibtex"

    def serialize(self, pid, record, links_factory=None):
        """Serialize a single record to BibTeX."""
        return serialize_record_to_bibtex(record.get("metadata", record))

    def serialize_search(self, pid_fetcher, search_result, links=None, item_links_factory=None):
        """Serialize search results to BibTeX (one entry per hit)."""
        entries = [
            serialize_record_to_bibtex(hit["_source"].get("metadata", hit["_source"]))
            for hit in search_result["hits"]["hits"]
        ]
        return "\n\n".join(entries)
