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

"""Test application recievers."""

from invenio_files_rest.models import ObjectVersion

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.receivers import file_listener


def test_file_listener(db, document_with_file):
    """Test file listener when file is modified."""
    # Remove files
    document_with_file['_files'] = []
    document_with_file.commit()
    db.session.commit()

    # Reload record
    record = DocumentRecord.get_record_by_pid(document_with_file['pid'])
    assert not record['_files']

    object_version = ObjectVersion.get_by_bucket(document_with_file['_bucket'])
    file_listener(object_version)

    assert len(document_with_file.files) == 3
