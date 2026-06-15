# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test application recievers."""

from invenio_files_rest.models import Bucket, ObjectVersion
from six import BytesIO

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.receivers import (
    file_deleted_listener,
    file_uploaded_listener,
    sync_record_files,
)


def test_file_listener(db, document_with_file):
    """Test file listener when file is modified."""
    # Remove files
    document_with_file["_files"] = []
    document_with_file.commit()
    db.session.commit()

    # Reload record
    record = DocumentRecord.get_record_by_pid(document_with_file["pid"])
    assert not record["_files"]

    object_version = ObjectVersion.get_by_bucket(document_with_file["_bucket"])
    file_uploaded_listener("", object_version)

    assert len(document_with_file.files) == 3

    object_version = ObjectVersion.get_by_bucket(document_with_file["_bucket"])
    file_deleted_listener("", object_version)


def test_sync_record_files(db, document_with_file, bucket_location):
    """Test sync record files receiver."""
    assert len(document_with_file.files) == 3

    # File is not associated to document's bucket, nothing change
    new_bucket = Bucket.create(bucket_location)
    new_file = ObjectVersion.create(new_bucket, "new_file.pdf", stream=BytesIO(b"new file content"))
    db.session.commit()
    sync_record_files(new_file)
    assert len(document_with_file.files) == 3

    # Add file to same bucket as the document's one
    new_file = ObjectVersion.create(
        document_with_file.files["test1.pdf"].bucket,
        "new_file.pdf",
        stream=BytesIO(b"new file content"),
    )
    db.session.commit()
    sync_record_files(new_file)
    assert len(document_with_file.files) == 4
