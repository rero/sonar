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

"""Test schema.org marshmallow schema."""

from io import BytesIO

import pytest

from sonar.modules.documents.serializers import schemaorg_v1


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


def test_type(minimal_document):
    """Test @type serialization."""
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["@type"] == "CreativeWork"

    minimal_document["documentType"] = "coar:c_2f33"
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["@type"] == "Book"


def test_context(minimal_document):
    """Test @context serialization."""
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["@context"] == "http://schema.org/"


def test_abstract(minimal_document):
    """Test abstract serialization."""
    # No abstract
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "abstract" not in result

    # Take the first
    minimal_document["abstracts"] = [
        {"value": "Description 1"},
        {"value": "Description 2"},
    ]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["abstract"] == "Description 1"


def test_description(minimal_document):
    """Test description serialization."""
    # No abstract
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "description" not in result

    # Take the first
    minimal_document["abstracts"] = [
        {"value": "Description 1"},
        {"value": "Description 2"},
    ]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["description"] == "Description 1"


def test_in_language(minimal_document):
    """Test inLanguage serialization."""
    # No language
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "inLanguage" not in result

    # Take the first language
    minimal_document["language"] = [{"value": "eng"}, {"value": "fre"}]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["inLanguage"] == "eng"


def test_name(minimal_document):
    """Test name."""
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["name"] == "Title of the document"

    # No title
    minimal_document.pop("title", None)
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "name" not in result


def test_headline(minimal_document):
    """Test headline."""
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["headline"] == "Title of the document"


def test_creator(minimal_document, contributors):
    """Test creator serialization."""
    minimal_document.update({"contribution": contributors})
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["creator"] == [
        {"@type": "Person", "name": "Creator 1"},
        {"@type": "Person", "name": "Creator 2"},
    ]


def test_date_published(minimal_document):
    """Test date published serialization."""
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "datePublished" not in result

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
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["datePublished"] == "2019"


def test_url(minimal_document):
    """Test URL serialization."""
    minimal_document.files["test.pdf"] = BytesIO(b"File content")
    minimal_document.files["test.pdf"]["type"] = "file"
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["url"] == ["http://localhost/documents/1000/files/test.pdf"]

    # External file
    minimal_document.files["test.pdf"]["force_external_url"] = True
    minimal_document.files["test.pdf"]["external_url"] = "https://some.domain/file.pdf"
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["url"] == ["https://some.domain/file.pdf"]

    # Multiple files
    minimal_document.files["test2.pdf"] = BytesIO(b"File content")
    minimal_document.files["test2.pdf"]["type"] = "file"
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["url"] == [
        "https://some.domain/file.pdf",
        "http://localhost/documents/1000/files/test2.pdf",
    ]


def test_identifier(minimal_document):
    """Test identifier serialization."""
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["identifier"] == "https://n2t.net/ark:/99999/ffk31000"


def test_id(minimal_document):
    """Test @id serialization."""
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["@id"] == "https://n2t.net/ark:/99999/ffk31000"


def test_keywords(minimal_document):
    """Test subjects serialization."""
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "keywords" not in result

    minimal_document["subjects"] = [
        {"label": {"language": "eng", "value": ["Subject 1", "Subject 2"]}},
        {"label": {"language": "fre", "value": ["Sujet 1", "Sujet 2"]}},
    ]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["keywords"] == ["Subject 1", "Subject 2", "Sujet 1", "Sujet 2"]


def test_license(app, minimal_document):
    """Test license serialization."""
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "license" not in result

    minimal_document["usageAndAccessPolicy"] = {"license": "CC BY-NC-SA"}
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["license"] == "CC BY-NC-SA"

    minimal_document["usageAndAccessPolicy"] = {
        "license": "License undefined",
        "label": "Custom license",
    }
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["license"] == "License undefined, Custom license"


def test_image(app, minimal_document):
    """Test image serialization."""
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "image" not in result

    minimal_document.files["test.pdf"] = BytesIO(b"File content")
    minimal_document.files["test.pdf"]["type"] = "file"
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["image"] == "http://localhoststatic/images/no-image.png"


def test_pagination(app, minimal_document):
    """Test pagination."""
    # No part of
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "pagination" not in result

    # No pages
    minimal_document["partOf"] = [{"document": {"title": "Host document"}}]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "pagination" not in result

    # OK
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123-125"}
    ]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["pagination"] == "123-125"


def test_page_start(app, minimal_document):
    """Test page start."""
    # No partOf
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "pageStart" not in result

    # No pages
    minimal_document["partOf"] = [{"document": {"title": "Host document"}}]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "pageStart" not in result

    # Only one page
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123"}
    ]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["pageStart"] == "123"

    # Set of pages
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123-130"}
    ]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["pageStart"] == "123"

    # Exotic formatting
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123, 134-135"}
    ]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["pageStart"] == "123"

    # Page start not found
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "pages"}
    ]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "pageStart" not in result


def test_page_end(app, minimal_document):
    """Test page end."""
    # No partOf
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "pageEnd" not in result

    # No pages
    minimal_document["partOf"] = [{"document": {"title": "Host document"}}]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "pageEnd" not in result

    # Only one page
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123"}
    ]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "pageEnd" not in result

    # Set of pages
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123-130"}
    ]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert result["pageEnd"] == "130"

    # Exotic formatting
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "123, 134-135"}
    ]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "pageEnd" not in result

    # Page end not found
    minimal_document["partOf"] = [
        {"document": {"title": "Host document"}, "numberingPages": "pages"}
    ]
    result = schemaorg_v1.transform_record(minimal_document["pid"], minimal_document)
    assert "pageEnd" not in result
