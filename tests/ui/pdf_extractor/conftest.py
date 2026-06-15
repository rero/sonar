# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Pytest fixtures and plugins for PDF extractor tests."""

import os

import pytest
import requests


@pytest.fixture(scope="module")
def pdf_file():
    """Return test PDF file path."""
    return os.path.join(os.path.dirname(__file__), "data", "postprint.pdf")


@pytest.fixture(scope="module")
def xml_file():
    """Return test XML output file path."""
    return os.path.join(os.path.dirname(__file__), "data", "postprint.xml")


@pytest.fixture(scope="function")
def mock_grobid_response(monkeypatch, xml_file):
    """Mock a grobid response for full text extraction."""
    with open(xml_file) as file:
        output = file.read()

    class MockResponse:
        """Mock response."""

        status_code = 200
        text = output

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: MockResponse)


@pytest.fixture(scope="function")
def mock_grobid_error_response(monkeypatch):
    """Mock a grobid response with a failed status code."""

    class MockResponse:
        """Mock response."""

        status_code = 503
        text = ""

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: MockResponse)
