# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test HEG schema."""

from sonar.heg.serializers.schemas.heg import HEGSchema


def test_heg_schema(app):
    """Test HEG schema."""
    data = {"_id": "111", "language": "en"}
    assert HEGSchema().dump(data) == {
        "documentType": "coar:c_6501",
        "identifiedBy": [{"type": "bf:Doi", "value": "111"}],
        "language": [{"type": "bf:Language", "value": "eng"}],
    }

    # With spanish language
    data = {"_id": "111", "language": "es"}
    assert HEGSchema().dump(data) == {
        "documentType": "coar:c_6501",
        "identifiedBy": [{"type": "bf:Doi", "value": "111"}],
        "language": [{"type": "bf:Language", "value": "spa"}],
    }

    # Without language
    data = {"_id": "111"}
    assert HEGSchema().dump(data) == {
        "documentType": "coar:c_6501",
        "identifiedBy": [{"type": "bf:Doi", "value": "111"}],
        "language": [{"type": "bf:Language", "value": "eng"}],
    }

    # With files
    data = {"_id": "111", "pdf": "https://some.domain/some.pdf"}
    assert HEGSchema().dump(data) == {
        "documentType": "coar:c_6501",
        "identifiedBy": [{"type": "bf:Doi", "value": "111"}],
        "language": [{"type": "bf:Language", "value": "eng"}],
    }
