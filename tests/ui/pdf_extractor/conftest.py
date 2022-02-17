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

"""Pytest fixtures and plugins for PDF extractor tests."""

from __future__ import absolute_import, print_function

import os

import pytest
import requests


@pytest.fixture(scope='function')
def mock_grobid_response(monkeypatch):
    """Mock a grobid response for full text extraction."""
    with open(
            os.path.dirname(os.path.abspath(__file__)) + '/data/postprint.xml',
            'r') as file:
        output = file.read()

    class MockResponse:
        """Mock response."""

        status_code = 200
        text = output
    monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse)


@pytest.fixture(scope='function')
def mock_grobid_error_response(monkeypatch):
    """Mock a grobid response with a failed status code."""
    class MockResponse:
        """Mock response."""

        status_code = 503
        text = ''

    monkeypatch.setattr(requests, 'post', lambda *args, **kwargs: MockResponse)


@pytest.fixture(scope='module')
def pdf_file():
    """Return test PDF file path."""
    return os.path.dirname(os.path.abspath(__file__)) + '/data/postprint.pdf'


@pytest.fixture(scope='module')
def xml_file():
    """Return test XML output file path."""
    return os.path.dirname(os.path.abspath(__file__)) + '/data/postprint.xml'
