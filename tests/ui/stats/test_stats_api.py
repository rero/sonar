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

"""Test stats API."""

from sonar.modules.stats.api import Record
from sonar.modules.stats.tasks import collect_stats


def test_collect_task(document, document_with_file, es_clear):
    """Test collect stats."""
    assert collect_stats().startswith("New stat has been created with a pid of: ")


def test_collect(document, document_with_file, es_clear):
    """Test collect stats."""
    record = Record.collect()
    assert len(record["values"]) == 1
    assert record["values"][0]["full_text"] == 1
    assert record["values"][0]["organisation"] == "org"
    assert record["values"][0]["type"] == "shared"
    assert len(record["values"][0]["pids"]) == 2


def test_get_documents_pids(organisation, document):
    """Test get documents pids for organisation."""
    documents = list(Record.get_documents(organisation["pid"]))
    assert len(documents) == 1
    assert documents[0]["pid"] == "1"
