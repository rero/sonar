# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""BibTeX serializer."""

import re
import string

from invenio_records_rest.serializers.base import SerializerMixinInterface

from .common import (
    extract_abstract,
    extract_authors,
    extract_dissertation,
    extract_editors,
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
    "coar:c_46ec": "phdthesis",
    "coar:c_7a1f": "mastersthesis",
    "coar:c_db06": "phdthesis",
    "coar:c_bdcc": "mastersthesis",
    "habilitation_thesis": "phdthesis",
    "advanced_studies_thesis": "mastersthesis",
    "other_thesis": "phdthesis",
    "coar:c_8042": "techreport",
    "coar:c_1843": "misc",
    "coar:R60J-J5BD": "misc",
    "coar:c_ba08": "misc",
}


def _bibtex_entry_type(doc_type):
    """Return BibTeX entry type for a COAR document type."""
    return _COAR_TO_BIBTEX.get(doc_type, "misc")


def _bibtex_key(metadata):
    """Generate a BibTeX cite key from first author and year."""
    authors = extract_authors(metadata)
    last_name = authors[0].split(",")[0].strip() if authors else "unknown"
    # BibTeX keys cannot contain whitespace: collapse multi-word last names
    # like "van der Berg" into a single token.
    name = re.sub(r"\s+", "", last_name)
    return f"{name}{extract_year(metadata) or ''}"


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


def serialize_record_to_bibtex(metadata, used_keys=None):
    """Serialize a document metadata dict to a BibTeX entry string.

    :param used_keys: Optional set of cite keys already emitted in the same
        export (e.g. a search result with several entries). When the
        generated key collides with one already in the set, a letter suffix
        ("a", "b", ...) is appended to keep cite keys unique, as BibTeX
        consumers can otherwise reject or silently overwrite one entry.
    """
    doc_type = metadata.get("documentType", "")
    entry_type = _bibtex_entry_type(doc_type)
    key = _bibtex_key(metadata)

    if used_keys is not None:
        base_key = key
        suffix_index = 0
        while key in used_keys:
            key = f"{base_key}{string.ascii_lowercase[suffix_index]}"
            suffix_index += 1
        used_keys.add(key)

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
    _, place, publisher = extract_publication_info(metadata)
    if year := extract_year(metadata):
        fields.append(_bibtex_field("year", year))
    if place:
        fields.append(_bibtex_field("address", place))
    if publisher:
        fields.append(_bibtex_field("publisher", publisher))

    # Thesis: granting institution -> school
    if entry_type in ("phdthesis", "mastersthesis"):
        _, school, _ = extract_dissertation(metadata)
        if school:
            fields.append(_bibtex_field("school", school))

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
    doi, isbn, issn = extract_identifiers(metadata)
    if doi:
        fields.append(_bibtex_field("doi", doi, escape=False))
    if isbn:
        fields.append(_bibtex_field("isbn", isbn, escape=False))
    if issn:
        fields.append(_bibtex_field("issn", issn, escape=False))

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
        used_keys = set()
        entries = [
            serialize_record_to_bibtex(unwrap_metadata(hit["_source"]), used_keys=used_keys)
            for hit in search_result["hits"]["hits"]
        ]
        return "\n\n".join(entries)
