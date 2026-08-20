# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""RIS serializer."""

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

# Mapping from COAR resource types to RIS type tags, mirroring the COAR
# classification already established in
# sonar/modules/documents/serializers/schemas/schemaorg.py. Types with no
# clean RIS equivalent (images, video, software, maps, ...) fall back to
# "GEN" rather than a close-but-wrong type tag.
# https://purl.org/coar/resource_type
_COAR_TO_RIS = {
    "coar:c_2f33": "BOOK",
    "coar:c_3248": "CHAP",
    "coar:c_c94f": "GEN",
    "coar:c_5794": "CONF",
    "coar:c_18cp": "CONF",
    "coar:c_6670": "CONF",
    "coar:c_18co": "CONF",
    "coar:c_f744": "CONF",
    "coar:c_ddb1": "DATA",
    "coar:c_3e5a": "JOUR",
    "coar:c_beb9": "JOUR",
    "coar:c_6501": "JOUR",
    "coar:c_998f": "NEWS",
    "coar:c_dcae04bc": "JOUR",
    "coar:c_8544": "SLIDE",
    "non_textual_object": "GEN",
    "coar:c_8a7e": "VIDEO",
    "coar:c_ecc8": "ART",
    "coar:c_12cc": "MAP",
    "coar:c_18cc": "SOUND",
    "coar:c_18cw": "MUSIC",
    "coar:c_5ce6": "COMP",
    "coar:c_15cd": "PAT",
    "coar:c_2659": "JFULL",
    "coar:c_0640": "JFULL",
    "coar:c_2cd9": "JFULL",
    "coar:c_2fe3": "NEWS",
    "coar:c_816b": "JOUR",
    "coar:c_93fc": "RPRT",
    "coar:c_18ww": "RPRT",
    "coar:c_18wz": "RPRT",
    "coar:c_18wq": "RPRT",
    "coar:c_186u": "RPRT",
    "coar:c_18op": "RPRT",
    "coar:c_ba1f": "RPRT",
    "coar:c_18hj": "RPRT",
    "coar:c_18ws": "RPRT",
    "coar:c_18gh": "RPRT",
    "coar:c_46ec": "THES",
    "coar:c_7a1f": "THES",
    "coar:c_db06": "THES",
    "coar:c_bdcc": "THES",
    "habilitation_thesis": "THES",
    "advanced_studies_thesis": "THES",
    "other_thesis": "THES",
    "coar:c_8042": "RPRT",
    "coar:c_1843": "GEN",
    "coar:R60J-J5BD": "CONF",
    "coar:c_ba08": "JOUR",
}


def _ris_type(doc_type):
    """Return RIS type tag for a COAR document type."""
    return _COAR_TO_RIS.get(doc_type, "GEN")


def _ris_line(tag, value):
    """Return a formatted RIS field line.

    RIS is a line-based format: any embedded newline in a value would be
    read back as a malformed extra line, so newlines are collapsed to spaces.
    """
    return f"{tag}  - {' '.join(str(value).split())}"


def serialize_record_to_ris(metadata):
    """Serialize a document metadata dict to a RIS entry string."""
    doc_type = _ris_type(metadata.get("documentType", ""))
    lines = [_ris_line("TY", doc_type)]

    # Authors
    if authors := extract_authors(metadata):
        lines.extend(_ris_line("AU", name) for name in authors)

    # Editors (only if no authors)
    if not authors:
        lines.extend(_ris_line("ED", name) for name in extract_editors(metadata))

    # Title
    if title := extract_title(metadata):
        lines.append(_ris_line("TI", title))

    # Publication info: a hosted item's place/publisher are those of its
    # container, which does not always state its place: the record's own is
    # then kept.
    _, place, publisher = extract_publication_info(metadata)
    host_place, host_publisher = extract_host_publication(metadata)
    if host_publisher:
        place, publisher = host_place or place, host_publisher
    if year := extract_year(metadata):
        lines.append(_ris_line("PY", year))
    if place:
        lines.append(_ris_line("CY", place))

    # Thesis: PB is a single slot, so the granting institution overrides the
    # generic publisher there; M3 states the degree.
    if metadata.get("documentType") in THESIS_DOCUMENT_TYPES:
        degree, institution, _ = extract_dissertation(metadata)
        if issuer := institution or publisher:
            lines.append(_ris_line("PB", issuer))
        if degree:
            lines.append(_ris_line("M3", degree))
    elif publisher:
        lines.append(_ris_line("PB", publisher))

    # Host document: JO for journals, T2 (secondary title) for chapters/proceedings
    journal, volume, issue, pages = extract_journal_info(metadata)
    if journal:
        host_tag = "T2" if doc_type in ("CHAP", "CONF") else "JO"
        lines.append(_ris_line(host_tag, journal))
    if volume:
        lines.append(_ris_line("VL", volume))
    if issue:
        lines.append(_ris_line("IS", issue))
    if pages and (page_numbers := re.findall(r"\d+", pages)):
        lines.append(_ris_line("SP", page_numbers[0]))
        if len(page_numbers) > 1:
            lines.append(_ris_line("EP", page_numbers[1]))

    # Identifiers
    doi, isbn, issn, other_identifiers = extract_identifiers(metadata)
    if doi:
        lines.append(_ris_line("DO", doi))
    if isbn:
        lines.append(_ris_line("SN", isbn))
    if issn:
        lines.append(_ris_line("SN", issn))
    # RIS has no dedicated tag for ark/URN/local/report-number-style
    # identifiers: export them as labeled notes instead of dropping them.
    lines.extend(_ris_line("N1", f"{label.upper()}: {value}") for label, value in other_identifiers)

    # Abstract
    if abstract := extract_abstract(metadata):
        lines.append(_ris_line("AB", abstract))

    # Language
    lines.extend(
        _ris_line("LA", language["value"]) for language in metadata.get("language", []) if language.get("value")
    )

    # Permalink
    if url := extract_url(metadata):
        lines.append(_ris_line("UR", url))

    lines.append("ER  - ")
    return "\n".join(lines)


class RISSerializer(SerializerMixinInterface):
    """RIS serializer for document records."""

    mimetype = "application/x-research-info-systems"

    def serialize(self, pid, record, links_factory=None):
        """Serialize a single record to RIS."""
        return serialize_record_to_ris(unwrap_metadata(record))

    def serialize_search(self, pid_fetcher, search_result, links=None, item_links_factory=None):
        """Serialize search results to RIS (one entry per hit)."""
        entries = [serialize_record_to_ris(unwrap_metadata(hit["_source"])) for hit in search_result["hits"]["hits"]]
        return "\n\n".join(entries)
