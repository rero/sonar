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

"""Test REST endpoint for deposits."""

from flask import url_for


def test_get_content(app, client, deposit):
    """Test get existing file content."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)

    file_name = "main.pdf"

    # get the pdf file
    url_file_content = url_for(
        "invenio_records_files.depo_object_api",
        pid_value=deposit.get("pid"),
        key=file_name,
    )
    res = client.get(url_file_content)
    assert res.status_code == 200
    assert res.content_type == "application/octet-stream"
    assert res.content_length > 0


def test_get_metadata(app, client, deposit):
    """Test get existing file metadata."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)

    # get all files metadata of a given deposit
    url_files = url_for("invenio_records_files.depo_bucket_api", pid_value=deposit.get("pid"))
    res = client.get(url_files)
    assert res.status_code == 200
    file_keys = ["main.pdf", "additional.pdf"]
    assert set(file_keys) == set([f.get("key") for f in res.json.get("contents")])

    # get a specific file metadata of a given deposit
    for f_key in file_keys:
        url_file = url_for(
            "invenio_records_files.depo_bucket_api",
            pid_value=deposit.get("pid"),
            key=f_key,
        )
        res = client.get(url_file)
        assert res.status_code == 200


def test_put_delete(app, client, deposit, pdf_file):
    """Test create and delete a file."""
    app.config.update(SONAR_APP_DISABLE_PERMISSION_CHECKS=True)
    file_name = "test.pdf"

    # upload the file
    url_file_content = url_for(
        "invenio_records_files.depo_object_api",
        pid_value=deposit.get("pid"),
        key=file_name,
    )
    res = client.put(url_file_content, input_stream=open(pdf_file, "rb"))
    assert res.status_code == 200

    # get the version id
    url_file = url_for(
        "invenio_records_files.depo_bucket_api",
        pid_value=deposit.get("pid"),
        key=file_name,
    )
    res = client.get(url_file)
    content = res.json.get("contents")

    assert len(content) == 3
    content = content.pop()
    version_id = content.get("version_id")

    # upload a second version
    url_file_content = url_for(
        "invenio_records_files.depo_object_api",
        pid_value=deposit.get("pid"),
        key=file_name,
    )
    res = client.put(url_file_content, input_stream=open(pdf_file, "rb"))
    assert res.status_code == 200

    # get the new version id
    url_file = url_for(
        "invenio_records_files.depo_bucket_api",
        pid_value=deposit.get("pid"),
        key=file_name,
    )
    res = client.get(url_file)
    content = res.json.get("contents")

    assert len(content) == 3
    content = content.pop()
    assert version_id != content.get("version_id")

    # delete the file
    url_delete_file_content = url_for(
        "invenio_records_files.depo_object_api",
        pid_value=deposit.get("pid"),
        key=file_name,
    )
    res = client.delete(url_delete_file_content)
    assert res.status_code == 204

    # the file does not exist anymore
    res = client.get(url_file_content)
    assert res.status_code == 404

    # the file does not exist anymore
    url_file = url_for(
        "invenio_records_files.depo_bucket_api",
        pid_value=deposit.get("pid"),
        key=file_name,
    )
    res = client.get(url_file)
    assert res.status_code == 200
    content = res.json.get("contents")
    # fulltext, thumbnail: file has been removed
    # TODO: is it the right approach? Do we need to remove files and
    # the bucket?
    assert len(content) == 2
