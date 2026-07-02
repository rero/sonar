# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test BibTeX serializer."""

from sonar.modules.documents.serializers.bibtex import BibTeXSerializer, serialize_record_to_bibtex


def test_bibtex_issn_identifier():
    """ISSN identifiers are exported the same way as ISBN."""
    metadata = {"identifiedBy": [{"type": "bf:Issn", "value": "1234-5678"}]}
    assert "isbn         = {1234-5678}," in serialize_record_to_bibtex(metadata)


def test_bibtex_serialize_search_unwraps_metadata():
    """serialize_search unwraps the record envelope like serialize does."""
    metadata = {"identifiedBy": [{"type": "bf:Issn", "value": "1234-5678"}]}
    search_result = {"hits": {"hits": [{"_source": {"metadata": metadata}}]}}
    result = BibTeXSerializer().serialize_search(None, search_result)
    assert "isbn         = {1234-5678}," in result
