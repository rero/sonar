# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Test Google Scholar marshmallow schema."""

from io import BytesIO

import pytest

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.serializers import google_scholar_v1


@pytest.fixture()
def minimal_document(db, bucket_location, organisation):
    record = DocumentRecord.create(
        {
            "pid": "1000",
            "title": [
                {
                    "type": "bf:Title",
                    "mainTitle": [
                        {"language": "eng", "value": "Title of the document"}
                    ],
                }
            ],
            "organisation": [{"$ref": "https://sonar.ch/api/organisations/org"}],
        },
        dbcommit=True,
        with_bucket=True,
    )
    record.commit()
    db.session.commit()
    return record


@pytest.fixture()
def contributors():
    return [
        {
            "agent": {"preferred_name": "Creator 1"},
            "role": ["cre"],
        },
        {
            "agent": {
                "preferred_name": "Creator 2",
                "number": "123",
                "date": "2019",
                "place": "Martigny",
            },
            "role": ["cre"],
        },
        {
            "agent": {"preferred_name": "Contributor 1"},
            "role": ["ctb"],
        },
        {
            "agent": {
                "preferred_name": "Contributor 2",
                "number": "999",
                "date": "2010",
                "place": "Sion",
            },
            "role": ["ctb"],
        },
        {
            "agent": {"preferred_name": "Degree supervisor"},
            "role": ["dgs"],
        },
        {
            "agent": {"preferred_name": "Printer"},
            "role": ["prt"],
        },
        {
            "agent": {"preferred_name": "Editor"},
            "role": ["edt"],
        },
    ]


def test_title(minimal_document):
    """Test name."""
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert '<meta name="citation_title" content="Title of the document">' in result

    # No title
    minimal_document.pop("title", None)
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_title" not in result


def test_language(minimal_document):
    """Test inLanguage serialization."""
    # No language
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_language" not in result

    # Take the first language
    minimal_document["language"] = [{"value": "eng"}, {"value": "fre"}]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert '<meta name="citation_language" content="en">' in result


def test_publication_date(minimal_document):
    """Test publication date."""
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_publication_date" not in result

    minimal_document.update(
        {
            "provisionActivity": [
                {"type": "bf:Agent", "startDate": "2019"},
                {
                    "type": "bf:Publication",
                },
                {"type": "bf:Publication", "startDate": "2019"},
                {"type": "bf:Publication", "startDate": "2020-01-01"},
            ]
        }
    )
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert '<meta name="citation_publication_date" content="2019">' in result


def test_keywords(minimal_document):
    """Test subjects serialization."""
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_keywords" not in result

    minimal_document["subjects"] = [
        {"label": {"language": "eng", "value": ["Subject 1", "Subject 2"]}},
        {"label": {"language": "fre", "value": ["Sujet 1", "Sujet 2"]}},
    ]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert (
        '<meta name="citation_keywords" content="Subject 1 ; Subject 2 ; '
        'Sujet 1 ; Sujet 2">' in result
    )


def test_pdf_url(minimal_document):
    """Test PDF URL serialization."""
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_pdf_url" not in result

    minimal_document.files["test.pdf"] = BytesIO(b"File content")
    minimal_document.files["test.pdf"]["type"] = "file"
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert (
        '<meta name="citation_pdf_url" content="http://localhost/documents'
        '/1000/files/test.pdf">' in result
    )

    minimal_document.files["test.pdf"]["force_external_url"] = True
    minimal_document.files["test.pdf"]["external_url"] = "https://some.domain/file.pdf"
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert (
        '<meta name="citation_pdf_url" content="https://some.domain/'
        'file.pdf">' in result
    )


def test_authors(minimal_document, contributors):
    """Test authors serialization."""
    minimal_document.update({"contribution": contributors})
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )

    for author in ["Creator 1", "Creator 2"]:
        assert (
            '<meta name="citation_author" content="{author}">'.format(author=author)
            in result
        )


def test_doi(minimal_document):
    """Test DOI serialization."""
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_doi" not in result

    minimal_document["identifiedBy"] = [{"type": "bf:Doi", "value": "111111"}]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert '<meta name="citation_doi" content="111111">' in result


def test_abstract_html_url(minimal_document):
    """Test HTML URL serialization."""
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert (
        '<meta name="citation_abstract_html_url" content="http://'
        'localhost/global/documents/1000">' in result
    )


def test_pages(app, minimal_document):
    """Test pages."""
    # No part of
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_pages" not in result

    # No pages
    minimal_document["partOf"] = [{"document": {"title": "Host document"}}]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_pages" not in result

    # OK
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123-125"}
    ]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert '<meta name="citation_pages" content="123-125">' in result


def test_first_page(app, minimal_document):
    """Test first page."""
    # No partOf
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_firstpage" not in result

    # No pages
    minimal_document["partOf"] = [{"document": {"title": "Host document"}}]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_firstpage" not in result

    # Only one page
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123"}
    ]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert '<meta name="citation_firstpage" content="123">' in result

    # Set of pages
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123-130"}
    ]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert '<meta name="citation_firstpage" content="123">' in result

    # Exotic formatting
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123, 134-135"}
    ]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert '<meta name="citation_firstpage" content="123">' in result

    # Page start not found
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "pages"}
    ]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_firstpage" not in result


def test_last_page(app, minimal_document):
    """Test last page."""
    # No partOf
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_lastpage" not in result

    # No pages
    minimal_document["partOf"] = [{"document": {"title": "Host document"}}]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_lastpage" not in result

    # Only one page
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123"}
    ]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_lastpage" not in result

    # Set of pages
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123-130"}
    ]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert '<meta name="citation_lastpage" content="130">' in result

    # Exotic formatting
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123, 134-135"}
    ]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_lastpage" not in result

    # Page end not found
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "pages"}
    ]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_lastpage" not in result


def test_volume(app, minimal_document):
    """Test volume."""
    # No partOf
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_volume" not in result

    # No volume
    minimal_document["partOf"] = [{"document": {"title": "Host document"}}]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_volume" not in result

    # Only one page
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingVolume": "1"}
    ]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert '<meta name="citation_volume" content="1">' in result


def test_journal_title(app, minimal_document):
    """Test journal title."""
    # No partOf
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert "citation_journal_title" not in result

    minimal_document["partOf"] = [{"document": {"title": "Host document"}}]
    result = google_scholar_v1.transform_record(
        minimal_document["pid"], minimal_document
    )
    assert '<meta name="citation_journal_title" content="Host document">' in result
