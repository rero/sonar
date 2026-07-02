# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""RIS serializer."""

from invenio_records_rest.serializers.base import SerializerMixinInterface

from .common import (
    extract_abstract,
    extract_authors,
    extract_editors,
    extract_journal_info,
    extract_publication_info,
    extract_title,
)

# Mapping from COAR resource types to RIS type tags.
# https://purl.org/coar/resource_type
_COAR_TO_RIS = {
    "coar:c_2f33": "BOOK",  # book
    "coar:c_3248": "CHAP",  # book part
    "coar:c_5794": "JOUR",  # journal article
    "coar:c_18cp": "CONF",  # conference paper
    "coar:c_6670": "CHAP",  # book chapter
    "coar:c_816b": "THES",  # master thesis
    "coar:c_db06": "THES",  # doctoral thesis
    "coar:c_7a1f": "THES",  # thesis
    "coar:c_bdcc": "THES",  # master thesis (other)
    "coar:c_46ec": "THES",  # thesis (generic)
    "coar:c_8042": "RPRT",  # technical report
}


def _ris_type(doc_type):
    """Return RIS type tag for a COAR document type."""
    return _COAR_TO_RIS.get(doc_type, "GEN")


def serialize_record_to_ris(metadata):
    """Serialize a document metadata dict to a RIS entry string."""
    lines = [f"TY  - {_ris_type(metadata.get('documentType', ''))}"]

    # Authors
    if authors := extract_authors(metadata):
        lines.extend(f"AU  - {name}" for name in authors)

    # Editors (only if no authors)
    if not authors:
        lines.extend(f"ED  - {name}" for name in extract_editors(metadata))

    # Title
    if title := extract_title(metadata):
        lines.append(f"TI  - {title}")

    # Publication info
    year, place, publisher = extract_publication_info(metadata)
    if year:
        lines.append(f"PY  - {year}")
    if place:
        lines.append(f"CY  - {place}")
    if publisher:
        lines.append(f"PB  - {publisher}")

    # Journal / partOf
    journal, volume, issue, pages = extract_journal_info(metadata)
    if journal:
        lines.append(f"JO  - {journal}")
    if volume:
        lines.append(f"VL  - {volume}")
    if issue:
        lines.append(f"IS  - {issue}")
    if pages:
        page_range = pages.split("-")
        lines.append(f"SP  - {page_range[0].strip()}")
        if len(page_range) == 2:
            lines.append(f"EP  - {page_range[1].strip()}")

    # Identifiers
    for identifier in metadata.get("identifiedBy", []):
        if identifier.get("type") == "bf:Doi":
            lines.append(f"DO  - {identifier['value']}")
        elif identifier.get("type") in ("bf:Isbn", "bf:Issn"):
            lines.append(f"SN  - {identifier['value']}")

    # Abstract
    if abstract := extract_abstract(metadata):
        lines.append(f"AB  - {abstract}")

    # Language
    for language in metadata.get("language", []):
        if language.get("value"):
            lines.append(f"LA  - {language['value']}")
            break

    lines.append("ER  - ")
    return "\n".join(lines)


class RISSerializer(SerializerMixinInterface):
    """RIS serializer for document records."""

    mimetype = "application/x-research-info-systems"

    def serialize(self, pid, record, links_factory=None):
        """Serialize a single record to RIS."""
        return serialize_record_to_ris(record.get("metadata", record))

    def serialize_search(self, pid_fetcher, search_result, links=None, item_links_factory=None):
        """Serialize search results to RIS (one entry per hit)."""
        entries = [
            serialize_record_to_ris(hit["_source"].get("metadata", hit["_source"]))
            for hit in search_result["hits"]["hits"]
        ]
        return "\n\n".join(entries)
