# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test HEG record."""

from sonar.heg.record import HEGRecord


def test_serialize(app):
    """Test record serialize."""
    record = HEGRecord(
        {
            "identified_affiliations": [
                {
                    "i_aff": "7",
                    "aff": "University of Bern",
                }
            ],
            "RERO_ids": [],
            "CrossRef_record": {"_id": "crossref_id"},
            "Medline_record": {"_id": "medline_id"},
        }
    )
    assert record.serialize() == {
        "documentType": "coar:c_6501",
        "identifiedBy": [{"type": "bf:Doi", "value": "medline_id"}],
        "language": [{"type": "bf:Language", "value": "eng"}],
        "title": [
            {
                "mainTitle": [{"language": "eng", "value": "Unknown title"}],
                "type": "bf:Title",
            }
        ],
    }
