# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test RIS serializer."""

from sonar.modules.documents.serializers.ris import RISSerializer, serialize_record_to_ris


def test_ris_issn_identifier():
    """ISSN identifiers are exported the same way as ISBN."""
    metadata = {"identifiedBy": [{"type": "bf:Issn", "value": "1234-5678"}]}
    assert "SN  - 1234-5678" in serialize_record_to_ris(metadata)


def test_ris_serialize_search_unwraps_metadata():
    """serialize_search unwraps the record envelope like serialize does."""
    metadata = {"identifiedBy": [{"type": "bf:Issn", "value": "1234-5678"}]}
    search_result = {"hits": {"hits": [{"_source": {"metadata": metadata}}]}}
    result = RISSerializer().serialize_search(None, search_result)
    assert "SN  - 1234-5678" in result
