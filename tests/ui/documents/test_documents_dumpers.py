# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test documents recievers."""

import random

from sonar.modules.documents.dumpers import IndexerDumper


def test_document_indexer_dumper(document, pdf_file):
    """Test add full text to document."""
    with open(pdf_file, "rb") as file:
        content = file.read()

    # Successful file add
    document.add_file(content, "test1.pdf", type="file")
    assert document.files["test1.pdf"]
    assert document.files["test1-pdf.txt"]

    data = document.dumps(IndexerDumper())

    assert len(data["fulltext"]) == 1
    assert "PHYSICAL REVIEW B 99" in data["fulltext"][0]
    assert data["_updated"]
    assert "ips" in data["organisation"][0]
    assert "isOpenAccess" in data
    assert "identifiers" in data
    assert {"field": "customField1", "value": "Test"} in data["suggestions"]


def test_document_indexer_dumper_identifiers(document):
    """Test the additional identifiers produced by the dumper."""
    types = [
        "bf:AudioIssueNumber",
        "bf:Doi",
        "bf:Ean",
        "bf:Gtin14Number",
        "ark",
        "bf:Identifier",
        "bf:Isan",
        "bf:Isbn",
        "bf:Ismn",
        "bf:Isrc",
        "bf:Issn",
        "bf:Local",
        "bf:IssnL",
        "bf:MatrixNumber",
        "bf:MusicDistributorNumber",
        "bf:MusicPlate",
        "bf:MusicPublisherNumber",
        "bf:PublisherNumber",
        "bf:Upc",
        "bf:Urn",
        "bf:VideoRecordingNumber",
        "uri",
        "bf:ReportNumber",
        "bf:Strn",
    ]
    n = 0
    document["identifiedBy"] = []
    res = {}
    for t in types:
        key = t.split(":")[-1].lower()
        for _ in range(random.randint(1, 5)):
            value = f"value{n}"
            document["identifiedBy"].append({"type": t, "value": value})
            res.setdefault(key, []).append(value)
            n += 1

    data = document.dumps(IndexerDumper())
    assert data["identifiers"] == res
