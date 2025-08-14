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

"""Test documents API."""

from copy import deepcopy

from flask import url_for
from invenio_stats.tasks import aggregate_events, process_events

from sonar.modules.documents.api import DocumentRecord


def test_get_record_by_identifier(app, db, document):
    """Test getting record by its identifier."""
    # Record found
    record = DocumentRecord.get_record_by_identifier(
        [
            {"value": "111111", "type": "bf:Local", "source": "RERO DOC"},
            {"value": "R003415713", "type": "bf:Local", "source": "RERO"},
        ]
    )
    assert record["pid"] == document["pid"]

    # Not matching complete identifier
    record = DocumentRecord.get_record_by_identifier(
        [
            {"value": "111111", "type": "bf:Local", "source": "Unmatching"},
            {"value": "R003415713", "type": "bf:Local", "source": "RERO"},
        ]
    )
    assert not record

    # Mixing identifier data
    record = DocumentRecord.get_record_by_identifier(
        [{"value": "R003415713", "type": "bf:Local", "source": "RERO DOC"}]
    )
    assert not record

    # Record not found, cause juste `bf:Doi` and `bf:Local` are analyzed.
    record = DocumentRecord.get_record_by_identifier(
        [{"value": "oai:unknown", "type": "bf:Identifier"}]
    )
    assert not record


def test_get_next_file_order(db, document_with_file, document):
    """Test getting next file position."""
    # One file with order 1
    assert document_with_file.get_next_file_order() == 2

    # Adding a new file
    document_with_file.add_file(b"File content", "file2.pdf")
    assert document_with_file.get_next_file_order() == 3

    # No order properties
    for file in document_with_file.files:
        document_with_file.files[file.key].data.pop("order", None)
    assert document_with_file.get_next_file_order() == 2

    # No files
    assert document.get_next_file_order() == 1


def test_get_files_list(db, document, pdf_file):
    """Test getting the list of files, filtered and orderd."""
    document.add_file(b"file 1", "test1.pdf", order=2)
    document.add_file(b"file 2", "test2.pdf", order=1)
    document.add_file(b"file 3", "test3.pdf", order=3)
    document.add_file(b"file 4", "test4.pdf", order=4, type="not-file")
    files = document.get_files_list()
    assert len(files) == 3
    assert files[0]["order"] == 1


def test_get_documents_by_project(db, project, document):
    """ "Test getting documents by a project."""
    document["projects"] = [{"$ref": f"https://sonar.ch/api/projects/{project.id}"}]
    document.commit()
    document.reindex()
    db.session.commit()

    documents = DocumentRecord.get_documents_by_project(project.id)
    assert documents[0]["pid"] == document["pid"]
    assert documents[0]["permalink"] == "https://n2t.net/ark:/99999/ffk32"


def test_is_open_access(db, document, embargo_date):
    """Test if document is open access."""
    assert not document.is_open_access()

    # No restriction --> open access
    document.add_file(b"Test", "test1.pdf")
    assert document.is_open_access()

    # Restricted --> not open access
    document.files["test1.pdf"]["access"] = "coar:c_16ec"
    assert not document.is_open_access()

    # Open access --> open access
    document.files["test1.pdf"]["access"] = "coar:c_abf2"
    assert document.is_open_access()

    # Embargo access with no date --> not open access
    document.files["test1.pdf"]["access"] = "coar:c_f1cf"
    assert not document.is_open_access()

    # Embargo access with future date --> not open access
    document.files["test1.pdf"]["access"] = "coar:c_f1cf"
    document.files["test1.pdf"]["embargo_date"] = embargo_date.isoformat()
    assert not document.is_open_access()

    # Embargo access with past date --> open access
    document.files["test1.pdf"]["access"] = "coar:c_f1cf"
    document.files["test1.pdf"]["embargo_date"] = "2021-01-01"
    assert document.is_open_access()

    # Embargo access with wrong date --> not open access
    document.files["test1.pdf"]["access"] = "coar:c_f1cf"
    document.files["test1.pdf"]["embargo_date"] = "WRONG"
    assert not document.is_open_access()


def test_stats(app, db, client, document_with_file, es, event_queues):
    """Test get existing stats for file downloads."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)

    # read the record detailed view
    assert (
        client.get(
            url_for(
                "invenio_records_ui.doc",
                view="global",
                pid_value=document_with_file["pid"],
            )
        ).status_code
        == 200
    )

    # download the file
    assert (
        client.get(
            url_for(
                "invenio_records_ui.doc_files",
                pid_value=document_with_file["pid"],
                filename="test1.pdf",
            )
        ).status_code
        == 200
    )

    # download the thumbnail
    assert (
        client.get(
            url_for(
                "invenio_records_ui.doc_files",
                pid_value=document_with_file["pid"],
                filename="test1-pdf.jpg",
            )
        ).status_code
        == 200
    )

    # process the task
    process_events(["file-download", "record-view"])
    es.indices.refresh(index="events-stats-file-download")
    es.indices.refresh(index="events-stats-record-view")

    aggregate_events(["file-download-agg", "record-view-agg"])
    es.indices.refresh(index="stats-file-download")
    es.indices.refresh(index="stats-record-view")
    assert document_with_file.statistics["record-view"] == 1
    assert document_with_file.statistics["file-download"]["test1.pdf"] == 1
    # the thumbnail should not be in the statistics
    assert "test1-pdf.jpg" not in document_with_file.statistics["file-download"]


def test_affiliations(db, document):
    """Test controlled affiliation."""
    data = deepcopy(dict(document))
    data["contribution"][0]["affiliation"] = "foo"
    document.update(data)
    assert "controlledAffiliation" not in document["contribution"][0]

    data["contribution"][0][
        "affiliation"
    ] = "Uni of Geneva and HUG, Uni of Lausanne and CHUV"
    document.update(data)
    assert len(document["contribution"][0]["controlledAffiliation"]) == 2

    data["contribution"][0].pop("affiliation", None)
    document.update(data)
    assert "controlledAffiliation" not in document["contribution"][0]
