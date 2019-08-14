# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""Test institutions jsonresolvers."""

import pytest
from flask import url_for

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.institutions.api import InstitutionRecord


def test_institution_resolver(client):
    """Test institution resolver."""
    InstitutionRecord.create({
        "pid": "usi",
        "name": "Università della Svizzera italiana"
    })

    record = DocumentRecord.create({
        "title": "The title of the record",
        "institution": {"$ref": "https://sonar.ch/api/institutions/usi"}
    })

    assert record.replace_refs().get('institution')['name'] == 'Università ' \
        'della Svizzera italiana'
