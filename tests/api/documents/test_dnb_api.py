# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2022 RERO
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

"""Test DnbUrnService rest API."""


import requests_mock

from sonar.modules.documents.dnb import DnbUrnService


def test_dnb_rest_api_verify_exist(app):
    """Test dnb rest api verify code exist."""
    with requests_mock.mock() as response:
        response.head(requests_mock.ANY, status_code=200)
        urn_code = 'urn:nbn:ch:rero-006-119656'
        assert DnbUrnService.verify(urn_code)


def test_dnb_rest_api_verify_not_exist(app):
    """Test dnb rest api verify code does not exist."""
    with requests_mock.mock() as response:
        response.head(requests_mock.ANY, status_code=404)
        urn_code = 'urn:nbn:ch:rero-006-119654__'
        assert not DnbUrnService.verify(urn_code)


def test_dnb_rest_api_register(app, minimal_thesis_document):
    """Test dnb rest api register new code."""
    with requests_mock.mock() as response:
        response.post(requests_mock.ANY, status_code=404)
        urn_code = 'urn:nbn:ch:rero-006-17'
        assert not DnbUrnService.register(urn_code)
