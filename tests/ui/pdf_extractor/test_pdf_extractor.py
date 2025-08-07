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

"""Test PDF extractor class."""

import os
import tempfile

import pytest

from sonar.modules.pdf_extractor.pdf_extractor import PDFExtractor


def test_load_config(app, monkeypatch):
    """Test configuration loading."""
    monkeypatch.setattr(PDFExtractor, "api_is_alive", lambda *args: False)
    with pytest.raises(ConnectionRefusedError):
        PDFExtractor()


def test_process(app, mock_grobid_response, pdf_file):
    """Test process method."""
    pdf_extractor = PDFExtractor()

    # Test output as XML
    output = pdf_extractor.process(pdf_file, dict_output=False)
    assert output.startswith('<?xml version="1.0" encoding="UTF-8"?>')

    # Test output as dictionary
    output = pdf_extractor.process(pdf_file, dict_output=True)
    assert "teiHeader" in output

    # Test output as XML in a file
    with tempfile.NamedTemporaryFile(mode="w+b", suffix=".pdf") as temp_file:
        pdf_extractor.process(pdf_file, output_file=temp_file.name)

        with open(temp_file.name, "r") as output_file:
            output = output_file.read()
            assert output.startswith('<?xml version="1.0" encoding="UTF-8"?>')


def test_process_raw(app, mock_grobid_response, pdf_file):
    """Test process with raw content."""
    with open(pdf_file, "rb") as file:
        content = file.read()

    pdf_extractor = PDFExtractor()
    output = pdf_extractor.process_raw(content)
    assert "teiHeader" in output


def test_extract_metadata(app, mock_grobid_response, pdf_file):
    """Test metadata extraction."""
    pdf_extractor = PDFExtractor()

    # Test valid extraction
    output = pdf_extractor.extract_metadata(pdf_file)
    assert output.startswith('<?xml version="1.0" encoding="UTF-8"?>')

    # Test non existing file
    with pytest.raises(ValueError) as exception:
        pdf_extractor.extract_metadata("not_existing_file.pdf")
    assert str(exception.value) == "Input file does not exist"

    # Test non valid pdf
    input_file = os.path.join(os.path.dirname(__file__), "data", "test.doc")
    with pytest.raises(ValueError) as exception:
        pdf_extractor.extract_metadata(input_file)
    assert str(exception.value) == "Input file is not a valid PDF file"


def test_extract_metadata_api_error_response(app, mock_grobid_error_response, pdf_file):
    """Test metadata extraction with error on API."""
    pdf_extractor = PDFExtractor()

    # Test error on api during extraction
    with pytest.raises(Exception) as exception:
        pdf_extractor.extract_metadata(pdf_file)
    assert str(exception.value) == "Metadata extraction failed"


def test_api_is_alive(app, monkeypatch):
    """Test if api is alive."""
    pdf_extractor = PDFExtractor()

    # Test API is up
    assert pdf_extractor.api_is_alive()

    # Test API is down
    monkeypatch.setattr(PDFExtractor, "do_request", lambda *args: ("", 503))
    assert not pdf_extractor.api_is_alive()

    # Test API raise exception
    monkeypatch.setattr(PDFExtractor, "do_request", lambda *args: Exception)
    assert not pdf_extractor.api_is_alive()


def test_do_request(app, mock_grobid_response, pdf_file):
    """Test request to API."""
    pdf_extractor = PDFExtractor()
    # Test valid call
    assert pdf_extractor.do_request("isalive", "get") == (b"true", 200)

    # Test unexisting endpoint
    assert pdf_extractor.do_request("unexisting", "get")[1] == 404

    # Test invalid request type
    with pytest.raises(ValueError):
        pdf_extractor.do_request("isalive", "invalid")

    # Test post request
    assert (
        pdf_extractor.do_request(
            "processFulltextDocument",
            "post",
            files={"input": (pdf_file, open(pdf_file, "rb"), "application/pdf")},
        )[1]
        == 200
    )
