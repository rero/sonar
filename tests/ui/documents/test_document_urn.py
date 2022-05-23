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

"""Test Dublic Core marshmallow schema."""



from invenio_pidstore.models import PersistentIdentifier, PIDStatus

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.urn import Urn
from sonar.modules.utils import wait_empty_tasks


def test_urn_create(db, bucket_location, organisation):
    """Test create URN identifier."""
    record = DocumentRecord.create(
        {
            "title": [
                {
                    "type": "bf:Title",
                    "mainTitle": [
                        {
                            "language": "eng",
                            "value": "Title of the document"
                        }
                    ],
                }
            ],
            "documentType": "coar:c_db06",
            "organisation": [
                {"$ref": "https://sonar.ch/api/organisations/org"}],
            "identifiedBy": [
                {"type": "bf:Local", "value": "10.1186"},
            ],
        },
        dbcommit=True,
        with_bucket=True,
    )
    record.commit()
    db.session.commit()
    record.reindex()
    wait_empty_tasks(delay=3, verbose=True)
    urn_code = DocumentRecord.get_urn_codes(record)[0]
    assert urn_code == 'urn:nbn:ch:rero-006-17'
    urn_pid = PersistentIdentifier.get('urn', urn_code)
    assert urn_pid.status == PIDStatus.REGISTERED
    urns = Urn.get_unregistered_urns()
    assert 'urn:nbn:ch:rero-006-17' not in urns
