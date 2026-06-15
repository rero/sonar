# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test REST endpoint for collections."""

from flask import url_for


def test_get_content(app, client, collection_with_file):
    """Test get existing file content."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)

    file_name = "test1.pdf"

    # get the pdf file
    url_file_content = url_for(
        "invenio_records_files.coll_object_api",
        pid_value=collection_with_file.get("pid"),
        key=file_name,
    )
    res = client.get(url_file_content)
    assert res.status_code == 200
    assert res.content_type == "application/octet-stream"
    assert res.content_length > 0


def test_get_metadata(app, client, collection_with_file):
    """Test get existing file metadata."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)

    # get all files metadata of a given collection
    url_files = url_for(
        "invenio_records_files.coll_bucket_api",
        pid_value=collection_with_file.get("pid"),
    )
    res = client.get(url_files)
    assert res.status_code == 200
    file_keys = ["test1.pdf"]
    assert set(file_keys) == {f.get("key") for f in res.json.get("contents")}

    # get a specific file metadata of a given collection
    for f_key in file_keys:
        url_file = url_for(
            "invenio_records_files.coll_bucket_api",
            pid_value=collection_with_file.get("pid"),
            key=f_key,
        )
        res = client.get(url_file)
        assert res.status_code == 200


def test_put_delete(app, client, collection, pdf_file):
    """Test create and delete a file."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    file_name = "test.pdf"

    # upload the file
    url_file_content = url_for(
        "invenio_records_files.coll_object_api",
        pid_value=collection.get("pid"),
        key=file_name,
    )
    with open(pdf_file, "rb") as f:
        res = client.put(url_file_content, input_stream=f)
        assert res.status_code == 200

    # get the version id
    url_file = url_for(
        "invenio_records_files.coll_bucket_api",
        pid_value=collection.get("pid"),
        key=file_name,
    )
    res = client.get(url_file)
    content = res.json.get("contents")

    assert len(content) == 1
    content = content.pop()
    version_id = content.get("version_id")

    # upload a second version
    url_file_content = url_for(
        "invenio_records_files.coll_object_api",
        pid_value=collection.get("pid"),
        key=file_name,
    )
    with open(pdf_file, "rb") as f:
        res = client.put(url_file_content, input_stream=f)
        assert res.status_code == 200

    # get the new version id
    url_file = url_for(
        "invenio_records_files.coll_bucket_api",
        pid_value=collection.get("pid"),
        key=file_name,
    )
    res = client.get(url_file)
    content = res.json.get("contents")

    assert len(content) == 1
    content = content.pop()
    assert version_id != content.get("version_id")

    # delete the file
    url_delete_file_content = url_for(
        "invenio_records_files.coll_object_api",
        pid_value=collection.get("pid"),
        key=file_name,
    )
    res = client.delete(url_delete_file_content)
    assert res.status_code == 204

    # the file does not exist anymore
    res = client.get(url_file_content)
    assert res.status_code == 404

    # the file does not exist anymore
    url_file = url_for(
        "invenio_records_files.coll_bucket_api",
        pid_value=collection.get("pid"),
        key=file_name,
    )
    res = client.get(url_file)
    assert res.status_code == 200
    content = res.json.get("contents")
    # fulltext, thumbnail: file has been removed
    # TODO: is it the right approach? Do we need to remove files and
    # the bucket?
    assert len(content) == 0
