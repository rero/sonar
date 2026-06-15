# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test stats API."""

from sonar.modules.stats.api import Record
from sonar.modules.stats.tasks import collect_stats


def test_collect_task(db, document, document_with_file, search_clear):
    """Test collect stats."""
    assert collect_stats().startswith("New stat has been created with a pid of: ")


def test_collect(db, document, document_with_file, search_clear):
    """Test collect stats."""
    record = Record.collect()
    assert len(record["values"]) == 1
    assert record["values"][0]["full_text"] == 1
    assert record["values"][0]["organisation"] == "org"
    assert record["values"][0]["type"] == "shared"
    assert len(record["values"][0]["pids"]) == 2


def test_get_documents_pids(db, organisation, document):
    """Test get documents pids for organisation."""
    documents = list(Record.get_documents(organisation["pid"]))
    assert len(documents) == 1
    assert documents[0]["pid"] == "1"
