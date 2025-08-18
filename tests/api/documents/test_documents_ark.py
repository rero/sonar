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

"""Test documents query."""

from flask import url_for


def test_ark_query(db, client, organisation, document, search_clear):
    """Test ark search query."""

    # an empty query: the document should be in the results
    res = client.get(url_for("invenio_records_rest.doc_list", view="global"))
    assert res.status_code == 200
    assert res.json["hits"]["total"]["value"] == 1

    # check the ark fields in the search output
    doc = res.json["hits"]["hits"][0]["metadata"]
    assert "ark" in doc["permalink"]
    assert "ark" in doc["identifiers"]["ark"][0]

    # the ark identifier field should exists
    ark = document.get_ark()
    res = client.get(url_for("invenio_records_rest.doc_list", view="global", q="_exists_:identifiers.ark"))
    assert res.json["hits"]["total"]["value"] == 1

    # search with the field name
    res = client.get(url_for("invenio_records_rest.doc_list", view="global", q=f'identifiers.ark:"{ark}"'))
    assert res.json["hits"]["total"]["value"] == 1

    # search everywhere
    res = client.get(url_for("invenio_records_rest.doc_list", view="global", q=f'"{ark}"'))
    assert res.json["hits"]["total"]["value"] == 1
