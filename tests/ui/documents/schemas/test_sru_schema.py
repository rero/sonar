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

"""Test SRU dojson transformation."""

from __future__ import absolute_import, print_function

from sonar.modules.documents.loaders.schemas.sru import SRUSchema


def test_title():
    """Test title."""

    # No 245
    xml = """
    <record></record>
    """
    assert SRUSchema().dump(xml) == {}

    # No 245$a
    xml = """
    <record>
        <datafield tag="245" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="a">Title</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "title": [{"mainTitle": [{"language": "eng", "value": "Title"}], "type": "bf:Title"}]
    }

    # With language
    xml = """
    <record>
        <controlfield tag="008">201011s1980    xxk||||| |||| 00| ||ger d</controlfield>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="a">Title</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "language": [{"type": "bf:Language", "value": "ger"}],
        "provisionActivity": [{"startDate": "1980", "type": "bf:Publication"}],
        "title": [{"mainTitle": [{"language": "ger", "value": "Title"}], "type": "bf:Title"}],
    }

    # With subtitle
    xml = """
    <record>
        <datafield tag="245" ind1=" " ind2=" ">
            <subfield code="a">Title</subfield>
            <subfield code="b">Subtitle</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "title": [
            {
                "mainTitle": [{"language": "eng", "value": "Title"}],
                "subtitle": [{"language": "eng", "value": "Subtitle"}],
                "type": "bf:Title",
            }
        ]
    }


def test_language():
    """Test language."""

    # No 008
    xml = """
    <record></record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <controlfield tag="008">201011s1980    xxk||||| |||| 00| ||ger d</controlfield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "language": [{"type": "bf:Language", "value": "ger"}],
        "provisionActivity": [{"startDate": "1980", "type": "bf:Publication"}],
    }


def test_identified_by():
    """Test identified by."""
    # No 001
    xml = """
    <record></record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <controlfield tag="001">1111</controlfield>
    </record>
    """
    assert SRUSchema().dump(xml) == {"identifiedBy": [{"type": "bf:Local", "value": "1111", "source": "swisscovery"}]}

    # ISBN, but no $a
    xml = """
    <record>
        <datafield tag="020" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # ISBN, OK
    xml = """
    <record>
        <datafield tag="020" ind1=" " ind2=" ">
            <subfield code="a">ISBN NUMBER</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {"identifiedBy": [{"type": "bf:Isbn", "value": "ISBN NUMBER"}]}

    # ISSN, but no $a and no $l
    xml = """
    <record>
        <datafield tag="022" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # ISSN, OK
    xml = """
    <record>
        <datafield tag="022" ind1=" " ind2=" ">
            <subfield code="a">ISSN NUMBER</subfield>
            <subfield code="l">ISSNL NUMBER</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "identifiedBy": [
            {"type": "bf:Issn", "value": "ISSN NUMBER"},
            {"type": "bf:IssnL", "value": "ISSNL NUMBER"},
        ]
    }

    # 024, but no $a
    xml = """
    <record>
        <datafield tag="024" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # 024, OK
    xml = """
    <record>
        <datafield tag="024" ind1=" " ind2=" ">
            <subfield code="a">DOI</subfield>
            <subfield code="2">doi</subfield>
        </datafield>
        <datafield tag="024" ind1=" " ind2=" ">
            <subfield code="a">URN</subfield>
            <subfield code="2">urn</subfield>
        </datafield>
        <datafield tag="024" ind1=" " ind2=" ">
            <subfield code="a">URI</subfield>
            <subfield code="2">uri</subfield>
        </datafield>
        <datafield tag="024" ind1=" " ind2=" ">
            <subfield code="a">OTHER</subfield>
            <subfield code="2">other</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "identifiedBy": [
            {"type": "bf:Doi", "value": "DOI"},
            {"type": "bf:Urn", "value": "URN"},
            {"type": "uri", "value": "URI"},
            {"type": "bf:Local", "value": "OTHER", "source": "other"},
        ]
    }

    # 027, but no $a
    xml = """
    <record>
        <datafield tag="027" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # 027, OK
    xml = """
    <record>
        <datafield tag="027" ind1=" " ind2=" ">
            <subfield code="a">Identifier</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {"identifiedBy": [{"type": "bf:Strn", "value": "Identifier"}]}

    # 088, but no $a
    xml = """
    <record>
        <datafield tag="088" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # 088, OK
    xml = """
    <record>
        <datafield tag="088" ind1=" " ind2=" ">
            <subfield code="a">Identifier</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {"identifiedBy": [{"type": "bf:ReportNumber", "value": "Identifier"}]}


def test_abstracts():
    """Test abstracts."""
    # No 520
    xml = """
    <record></record>
    """
    assert SRUSchema().dump(xml) == {}

    # 520, but no $a
    xml = """
    <record>
        <datafield tag="520" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK, default language
    xml = """
    <record>
        <datafield tag="520" ind1=" " ind2=" ">
            <subfield code="a">Record summary</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {"abstracts": [{"value": "Record summary", "language": "eng"}]}


def test_content_notes():
    """Test content notes."""
    # No 505
    xml = """
    <record></record>
    """
    assert SRUSchema().dump(xml) == {}

    # 505, but no $a
    xml = """
    <record>
        <datafield tag="505" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <datafield tag="505" ind1=" " ind2=" ">
            <subfield code="a">Note 1</subfield>
        </datafield>
        <datafield tag="505" ind1=" " ind2=" ">
            <subfield code="a">Note 2</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {"contentNote": ["Note 1", "Note 2"]}


def test_contribution():
    """Test contribution."""
    # 100, but no $a
    xml = """
    <record>
        <datafield tag="100" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK, field 100
    xml = """
    <record>
        <datafield tag="100" ind1=" " ind2=" ">
            <subfield code="a">Thilmany, Christian.</subfield>
            <subfield code="b">Herrmann</subfield>
            <subfield code="d">1710-1767.,</subfield>
            <subfield code="4">dsr</subfield>
            <subfield code="4">http://id.loc.gov/voc/relators/dsr</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "contribution": [
            {
                "agent": {
                    "type": "bf:Person",
                    "preferred_name": "Thilmany, Christian. Herrmann",
                    "date_of_birth": "1710",
                    "date_of_death": "1767",
                },
                "role": ["cre"],
            }
        ]
    }

    # OK, field 700
    xml = """
    <record>
        <datafield tag="700" ind1=" " ind2=" ">
            <subfield code="a">Thilmany, Christian.</subfield>
            <subfield code="b">Herrmann</subfield>
            <subfield code="d">1710-1767.,</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "contribution": [
            {
                "agent": {
                    "type": "bf:Person",
                    "preferred_name": "Thilmany, Christian. Herrmann",
                    "date_of_birth": "1710",
                    "date_of_death": "1767",
                },
                "role": ["cre"],
            }
        ]
    }

    # Field 710
    xml = """
    <record>
        <datafield tag="710" ind1=" " ind2=" ">
            <subfield code="a">Commission européenne</subfield>
            <subfield code="b">Direction générale Emploi</subfield>
            <subfield code="b">Another b</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "contribution": [
            {
                "agent": {
                    "type": "bf:Organization",
                    "preferred_name": "Commission européenne. Direction générale Emploi. Another b",
                },
                "role": ["ctb"],
            }
        ]
    }

    # Field 711
    xml = """
    <record>
        <datafield tag="711" ind1=" " ind2=" ">
            <subfield code="a">Forage and Grassland Conference</subfield>
            <subfield code="b">Sub</subfield>
            <subfield code="c">Hamburg</subfield>
            <subfield code="d">2011-02-02</subfield>
            <subfield code="n">1</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "contribution": [
            {
                "agent": {
                    "type": "bf:Meeting",
                    "preferred_name": "Forage and Grassland Conference. Sub",
                    "place": "Hamburg",
                    "date": "2011-02-02",
                    "number": "1",
                },
                "role": ["ctb"],
            }
        ]
    }


def test_extent():
    """Test extent."""
    # 300, but no $a
    xml = """
    <record>
        <datafield tag="300" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <datafield tag="300" ind1=" " ind2=" ">
            <subfield code="a">1 Bd.</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {"extent": "1 Bd."}


def test_dissertation():
    """Test dissertation."""
    # 502, but no $a
    xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Diss. Claremont</subfield>
            <subfield code="b">Complément</subfield>
            <subfield code="c">Granting</subfield>
            <subfield code="d">2019</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "dissertation": {
            "degree": "Diss. Claremont. Complément",
            "grantingInstitution": "Granting",
            "date": "2019",
        }
    }

    # Wrong date
    xml = """
    <record>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="a">Diss. Claremont</subfield>
            <subfield code="b">Complément</subfield>
            <subfield code="c">Granting</subfield>
            <subfield code="d">wrong</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "dissertation": {
            "degree": "Diss. Claremont. Complément",
            "grantingInstitution": "Granting",
        }
    }


def test_additional_materials():
    """Test additional materials."""
    # 300, but no $e
    xml = """
    <record>
        <datafield tag="300" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <datafield tag="300" ind1=" " ind2=" ">
            <subfield code="a">1 Bd.</subfield>
            <subfield code="e">30 pl.</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {"extent": "1 Bd.", "additionalMaterials": "30 pl."}


def test_formats():
    """Test formats."""
    # 300, but no $c
    xml = """
    <record>
        <datafield tag="300" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <datafield tag="300" ind1=" " ind2=" ">
            <subfield code="a">1 Bd.</subfield>
            <subfield code="c">24 cm</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {"extent": "1 Bd.", "formats": ["24 cm"]}


def test_other_material_characteristics():
    """Test other material characteristics."""
    # 300, but no $b
    xml = """
    <record>
        <datafield tag="300" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <datafield tag="300" ind1=" " ind2=" ">
            <subfield code="a">1 Bd.</subfield>
            <subfield code="b">Other material characteristics</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "extent": "1 Bd.",
        "otherMaterialCharacteristics": "Other material characteristics",
    }


def test_edition_statement():
    """Test edition statement."""
    # 250, but no $a
    xml = """
    <record>
        <datafield tag="250" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <datafield tag="250" ind1=" " ind2=" ">
            <subfield code="a">1st edition</subfield>
            <subfield code="b">Resp.</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "editionStatement": {
            "editionDesignation": {"value": "1st edition"},
            "responsibility": {"value": "Resp."},
        }
    }


def test_document_type():
    """Test document type."""
    # Still image
    xml = """
    <record>
        <leader>02935nkm a2200253 c 4500</leader>
    </record>
    """
    assert SRUSchema().dump(xml) == {"documentType": "coar:c_ecc8"}

    # Musical notation
    xml = """
    <record>
        <leader>02935ncm a2200253 c 4500</leader>
    </record>
    """
    assert SRUSchema().dump(xml) == {"documentType": "coar:c_18cw"}

    # Cartographic material
    xml = """
    <record>
        <leader>02935nfm a2200253 c 4500</leader>
    </record>
    """
    assert SRUSchema().dump(xml) == {"documentType": "coar:c_12cc"}

    # Moving image
    xml = """
    <record>
        <leader>02935ngm a2200253 c 4500</leader>
    </record>
    """
    assert SRUSchema().dump(xml) == {"documentType": "coar:c_8a7e"}

    # Sound
    xml = """
    <record>
        <leader>02935njm a2200253 c 4500</leader>
    </record>
    """
    assert SRUSchema().dump(xml) == {"documentType": "coar:c_18cc"}

    # Dataset
    xml = """
    <record>
        <leader>02935nmm a2200253 c 4500</leader>
    </record>
    """
    assert SRUSchema().dump(xml) == {"documentType": "coar:c_ddb1"}

    # Contribution to journal
    xml = """
    <record>
        <leader>02935nab a2200253 c 4500</leader>
    </record>
    """
    assert SRUSchema().dump(xml) == {"documentType": "coar:c_3e5a"}

    # Book part
    xml = """
    <record>
        <leader>02935naa a2200253 c 4500</leader>
    </record>
    """
    assert SRUSchema().dump(xml) == {"documentType": "coar:c_3248"}

    # Periodical
    xml = """
    <record>
        <leader>02935nas a2200253 c 4500</leader>
    </record>
    """
    assert SRUSchema().dump(xml) == {"documentType": "coar:c_2659"}

    # Bachelor thesis
    xml = """
    <record>
        <leader>02935nam a2200253 c 4500</leader>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="b">bachelor thesis</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "documentType": "coar:c_7a1f",
        "dissertation": {"degree": "bachelor thesis"},
    }

    # Master thesis
    xml = """
    <record>
        <leader>02935nam a2200253 c 4500</leader>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="b">master thesis</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "documentType": "coar:c_bdcc",
        "dissertation": {"degree": "master thesis"},
    }

    # Doctoral thesis
    xml = """
    <record>
        <leader>02935nam a2200253 c 4500</leader>
        <datafield tag="502" ind1=" " ind2=" ">
            <subfield code="b">thèse</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "documentType": "coar:c_db06",
        "dissertation": {"degree": "thèse"},
    }

    # Thesis
    xml = """
    <record>
        <leader>02935nam a2200253 c 4500</leader>
        <datafield tag="502" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {"documentType": "coar:c_46ec"}

    # Book
    xml = """
    <record>
        <leader>02935nam a2200253 c 4500</leader>
    </record>
    """
    assert SRUSchema().dump(xml) == {"documentType": "coar:c_2f33"}

    # Other
    xml = """
    <record>
        <leader>02935nzz a2200253 c 4500</leader>
    </record>
    """
    assert SRUSchema().dump(xml) == {"documentType": "coar:c_1843"}


def test_provision_activity():
    """Test provision activity."""
    xml = """
    <record>
        <controlfield tag="008">201011s19801990xxk||||| |||| 00| ||ger d</controlfield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "language": [{"type": "bf:Language", "value": "ger"}],
        "provisionActivity": [{"type": "bf:Publication", "startDate": "1980", "endDate": "1990"}],
    }

    # 264
    xml = """
    <record>
        <datafield tag="264" ind1=" " ind2="1">
            <subfield code="a">Place 1</subfield>
            <subfield code="a">Place 2</subfield>
            <subfield code="b">Agent 1</subfield>
            <subfield code="b">Agent 2</subfield>
            <subfield code="c">2019</subfield>
        </datafield>
        <datafield tag="264" ind1=" " ind2="3">
            <subfield code="a">Place 3</subfield>
            <subfield code="a">Place 4</subfield>
            <subfield code="b">Agent 3</subfield>
            <subfield code="b">Agent 4</subfield>
            <subfield code="c">2020</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "provisionActivity": [
            {
                "type": "bf:Publication",
                "statement": [
                    {"type": "bf:Place", "label": {"value": "Place 1"}},
                    {"type": "bf:Place", "label": {"value": "Place 2"}},
                    {"type": "bf:Agent", "label": {"value": "Agent 1"}},
                    {"type": "bf:Agent", "label": {"value": "Agent 2"}},
                    {"type": "Date", "label": {"value": "2019"}},
                ],
            },
            {
                "type": "bf:Manufacture",
                "statement": [
                    {"type": "bf:Place", "label": {"value": "Place 3"}},
                    {"type": "bf:Place", "label": {"value": "Place 4"}},
                    {"type": "bf:Agent", "label": {"value": "Agent 3"}},
                    {"type": "bf:Agent", "label": {"value": "Agent 4"}},
                    {"type": "Date", "label": {"value": "2020"}},
                ],
            },
        ]
    }


def test_notes():
    """Test notes."""
    # no $a
    xml = """
    <record>
        <datafield tag="500" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <datafield tag="500" ind1=" " ind2=" ">
            <subfield code="a">Note 1</subfield>
        </datafield>
        <datafield tag="504" ind1=" " ind2=" ">
            <subfield code="a">Note 2</subfield>
        </datafield>
        <datafield tag="508" ind1=" " ind2=" ">
            <subfield code="a">Note 3</subfield>
        </datafield>
        <datafield tag="510" ind1=" " ind2=" ">
            <subfield code="a">Note 4</subfield>
        </datafield>
        <datafield tag="511" ind1=" " ind2=" ">
            <subfield code="a">Note 5</subfield>
        </datafield>
        <datafield tag="530" ind1=" " ind2=" ">
            <subfield code="a">Note 6</subfield>
        </datafield>
        <datafield tag="545" ind1=" " ind2=" ">
            <subfield code="a">Note 7</subfield>
        </datafield>
        <datafield tag="555" ind1=" " ind2=" ">
            <subfield code="a">Note 8</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "notes": [
            "Note 1",
            "Note 2",
            "Note 3",
            "Note 4",
            "Note 5",
            "Note 6",
            "Note 7",
            "Note 8",
        ]
    }


def test_series():
    """Test series."""
    # no $a
    xml = """
    <record>
        <datafield tag="490" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <datafield tag="490" ind1=" " ind2=" ">
            <subfield code="a">Serie 1</subfield>
            <subfield code="v">12</subfield>
        </datafield>
        <datafield tag="490" ind1=" " ind2=" ">
            <subfield code="a">Serie 2</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {"series": [{"name": "Serie 1", "number": "12"}, {"name": "Serie 2"}]}


def test_part_of():
    """Test part of."""
    # no $t
    xml = """
    <record>
        <datafield tag="773" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="a">Contributor 1</subfield>
            <subfield code="a">Contributor 2</subfield>
            <subfield code="t">Document title 1</subfield>
            <subfield code="g">Vol. 22 (2004), Nr. 4, S. 485-512</subfield>
        </datafield>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="t">Document title 2</subfield>
            <subfield code="g">vol. 22 (2004), no 4</subfield>
            <subfield code="x">ISSN</subfield>
            <subfield code="z">ISBN</subfield>
        </datafield>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="t">Document title 3</subfield>
            <subfield code="g">S. 243-263</subfield>
        </datafield>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="t">Document title 4</subfield>
            <subfield code="g">yr:2011</subfield>
            <subfield code="g">no:16</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "partOf": [
            {
                "document": {
                    "title": "Document title 1",
                    "contribution": ["Contributor 1", "Contributor 2"],
                },
                "numberingVolume": "22",
                "numberingIssue": "4",
                "numberingPages": "485-512",
                "numberingYear": "2004",
            },
            {
                "document": {
                    "title": "Document title 2",
                    "identifiedBy": [
                        {"type": "bf:Issn", "value": "ISSN"},
                        {"type": "bf:Isbn", "value": "ISBN"},
                    ],
                },
                "numberingVolume": "22",
                "numberingIssue": "4",
                "numberingYear": "2004",
            },
            {
                "document": {
                    "title": "Document title 3",
                },
                "numberingPages": "243-263",
            },
            {
                "document": {"title": "Document title 4"},
                "numberingIssue": "16",
                "numberingYear": "2011",
            },
        ]
    }


def test_part_of_800():
    """Test part of."""
    # no $t
    xml = """
    <record>
        <datafield tag="800" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <datafield tag="800" ind1=" " ind2=" ">
            <subfield code="a">Contributor 1</subfield>
            <subfield code="a">Contributor 2</subfield>
            <subfield code="t">Document title 1</subfield>
            <subfield code="v">1234</subfield>
            <subfield code="x">ISSN</subfield>
            <subfield code="z">ISBN</subfield>
        </datafield>
        <datafield tag="800" ind1=" " ind2=" ">
            <subfield code="t">Document title 2</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "partOf": [
            {
                "document": {
                    "title": "Document title 1",
                    "contribution": ["Contributor 1", "Contributor 2"],
                    "identifiedBy": [
                        {"type": "bf:Issn", "value": "ISSN"},
                        {"type": "bf:Isbn", "value": "ISBN"},
                    ],
                },
                "numberingVolume": "1234",
            },
            {"document": {"title": "Document title 2"}},
        ]
    }


def test_part_of_830():
    """Test part of."""
    # no $a
    xml = """
    <record>
        <datafield tag="830" ind1=" " ind2=" ">
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {}

    # OK
    xml = """
    <record>
        <datafield tag="830" ind1=" " ind2=" ">
            <subfield code="a">Document title 1</subfield>
            <subfield code="p">Some subtitle</subfield>
            <subfield code="v">1234</subfield>
            <subfield code="x">ISSN</subfield>
            <subfield code="z">ISBN</subfield>
        </datafield>
        <datafield tag="830" ind1=" " ind2=" ">
            <subfield code="a">Document title 2</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "partOf": [
            {
                "document": {
                    "title": "Document title 1. Some subtitle",
                    "identifiedBy": [
                        {"type": "bf:Issn", "value": "ISSN"},
                        {"type": "bf:Isbn", "value": "ISBN"},
                    ],
                },
                "numberingVolume": "1234",
            },
            {"document": {"title": "Document title 2"}},
        ]
    }


def test_part_of_all():
    """Test multiple partOf."""
    xml = """
    <record>
        <datafield tag="773" ind1=" " ind2=" ">
            <subfield code="a">Contributor 1</subfield>
            <subfield code="a">Contributor 2</subfield>
            <subfield code="t">Document title 1</subfield>
            <subfield code="g">Vol. 22 (2004), Nr. 4, S. 485-512</subfield>
        </datafield>
        <datafield tag="800" ind1=" " ind2=" ">
            <subfield code="a">Contributor 1</subfield>
            <subfield code="a">Contributor 2</subfield>
            <subfield code="t">Document title 2</subfield>
            <subfield code="v">1234</subfield>
            <subfield code="x">ISSN</subfield>
            <subfield code="z">ISBN</subfield>
        </datafield>
        <datafield tag="830" ind1=" " ind2=" ">
            <subfield code="a">Document title 3</subfield>
            <subfield code="v">1234</subfield>
        </datafield>
    </record>
    """
    assert SRUSchema().dump(xml) == {
        "partOf": [
            {
                "document": {
                    "title": "Document title 1",
                    "contribution": ["Contributor 1", "Contributor 2"],
                },
                "numberingVolume": "22",
                "numberingIssue": "4",
                "numberingPages": "485-512",
                "numberingYear": "2004",
            },
            {
                "document": {
                    "title": "Document title 2",
                    "contribution": ["Contributor 1", "Contributor 2"],
                    "identifiedBy": [
                        {"type": "bf:Issn", "value": "ISSN"},
                        {"type": "bf:Isbn", "value": "ISBN"},
                    ],
                },
                "numberingVolume": "1234",
            },
            {"document": {"title": "Document title 3"}, "numberingVolume": "1234"},
        ]
    }
