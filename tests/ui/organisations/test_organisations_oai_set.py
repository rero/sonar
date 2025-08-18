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

"""Test OAI sets corresponding to organisation."""

import re

from invenio_oaiserver.models import OAISet


def test_oai_set(organisation, document):
    """Test OAI set synchronisation with organisation."""
    # Document has a `_oai` property
    assert document["_oai"]["id"] == f"oai:sonar.ch:{document['pid']}"
    assert document["_oai"]["sets"] == ["org"]
    assert re.match(
        r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:" r"[0-9]{2}:[0-9]{2}\.[0-9]{6}\+00:00$",
        document["_oai"]["updated"],
    )

    # Set for organisation exists
    sets = OAISet.query.all()
    assert len(sets) == 1
    assert sets[0].spec == "org"
    assert sets[0].name == "org"

    # New name is updated
    organisation.update({"code": "org", "name": "New name"})
    sets = OAISet.query.all()
    assert len(sets) == 1
    assert sets[0].spec == "org"
    assert sets[0].name == "New name"
