# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Test marc21 to json converter."""

import pytest
from dojson.contrib.marc21.utils import create_record

import sonar.modules.documents.dojson.contrib.marc21tojson.model as model
from sonar.modules.documents.dojson.contrib.marc21tojson import marc21tojson


def test_remove_punctuation():
    """Test remove punctuation from string."""
    assert model.remove_punctuation("lorem ipsum - / ; :,") == "lorem ipsum"


def test_get_mef_person_link():
    """Test getting MEF link."""
    assert model.get_mef_person_link(None, "", "") is None

    assert (
        model.get_mef_person_link("(RERO)A012327677", "", "")[:28]
        == "https://mef.rero.ch/api/mef/"
    )


def test_marc21_to_type():
    """
    Test dojson marc21_to_type.
    Books: LDR/6-7: am
    Journals: LDR/6-7: as
    Articles: LDR/6-7: aa + add field 773 (journal title)
    Scores: LDR/6: c|d
    Videos: LDR/6: g + 007/0: m|v
    Sounds: LDR/6: i|j
    E-books (imported from Cantook)
    """

    marc21xml = """
    <record>
        <leader>00501nam a2200133 a 4500</leader>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("type") == "book"

    marc21xml = """
    <record>
        <leader>00501nas a2200133 a 4500</leader>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("type") == "journal"

    marc21xml = """
    <record>
        <leader>00501naa a2200133 a 4500</leader>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("type") == "article"

    marc21xml = """
    <record>
        <leader>00501nca a2200133 a 4500</leader>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("type") == "score"
    marc21xml = """
    <record>
        <leader>00501nda a2200133 a 4500</leader>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("type") == "score"

    marc21xml = """
    <record>
        <leader>00501nia a2200133 a 4500</leader>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("type") == "sound"
    marc21xml = """
    <record>
        <leader>00501nja a2200133 a 4500</leader>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("type") == "sound"

    marc21xml = """
    <record>
        <leader>00501nga a2200133 a 4500</leader>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("type") == "video"


def test_marc21_to_title():
    """Test dojson marc21_to_title."""

    # subfields $a $b $c
    marc21xml = """
    <record>
      <datafield tag="245" ind1="1" ind2="0">
        <subfield code="a">main title :</subfield>
        <subfield code="b">subtitle /</subfield>
        <subfield code="c">responsability</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("title") == "main title : subtitle"
    # subfields $a $c
    marc21xml = """
    <record>
      <datafield tag="245" ind1="1" ind2="0">
        <subfield code="a">main title</subfield>
        <subfield code="c">responsability</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("title") == "main title"
    # subfield $a
    marc21xml = """
    <record>
      <datafield tag="245" ind1="1" ind2="0">
        <subfield code="a">main title</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("title") == "main title"


def test_marc21_to_titlesProper():
    """Test dojson marc21titlesProper."""

    marc21xml = """
    <record>
      <datafield tag="730" ind1="1" ind2="0">
        <subfield code="a">proper title</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("titlesProper") == ["proper title"]

    marc21xml = """
    <record>
      <datafield tag="730" ind1=" " ind2=" ">
        <subfield code="a">proper title</subfield>
      </datafield>
      <datafield tag="730" ind1=" " ind2=" ">
         <subfield code="a">other proper title</subfield>
       </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("titlesProper") == ["proper title", "other proper title"]


def test_marc21_to_languages():
    """Test dojson marc21languages."""

    marc21xml = """
    <record>
      <controlfield tag="008">
        881005s1984    xxu|||||| ||||00|| |ara d
      <controlfield>
      <datafield tag="041" ind1=" " ind2=" ">
        <subfield code="a">eng</subfield>
        <subfield code="h">ita</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("languages") == [{"language": "ara"}, {"language": "eng"}]
    assert data.get("translatedFrom") == ["ita"]

    marc21xml = """
    <record>
      <controlfield tag="008">
        881005s1984    xxu|||||| ||||00|| |ara d
      <controlfield>
      <datafield tag="041" ind1=" " ind2=" ">
        <subfield code="a">eng</subfield>
        <subfield code="a">fre</subfield>
        <subfield code="h">ita</subfield>
        <subfield code="h">ger</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("languages") == [
        {"language": "ara"},
        {"language": "eng"},
        {"language": "fre"},
    ]
    assert data.get("translatedFrom") == ["ita", "ger"]

    marc21xml = """
    <record>
      <controlfield tag="008">
        881005s1984    xxu|||||| ||||00|| |ara d
      <controlfield>
      <datafield tag="041" ind1=" " ind2=" ">
        <subfield code="a">eng</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("languages") == [{"language": "ara"}, {"language": "eng"}]
    assert "translatedFrom" not in data


def test_marc21_to_authors():
    """Test dojson marc21_to_authors."""

    marc21xml = """
    <record>
      <datafield tag="100" ind1=" " ind2=" ">
        <subfield code="a">Jean-Paul</subfield>
        <subfield code="b">II</subfield>
        <subfield code="c">Pape</subfield>
        <subfield code="d">1954-</subfield>
      </datafield>
      <datafield tag="700" ind1=" " ind2=" ">
        <subfield code="a">Dumont, Jean</subfield>
        <subfield code="c">Historien</subfield>
        <subfield code="d">1921-2014</subfield>
      </datafield>
      <datafield tag="710" ind1=" " ind2=" ">
        <subfield code="a">RERO</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    authors = data.get("authors")
    assert authors == [
        {
            "name": "Jean-Paul II",
            "type": "person",
            "date": "1954-",
            "qualifier": "Pape",
        },
        {
            "name": "Dumont, Jean",
            "type": "person",
            "date": "1921-2014",
            "qualifier": "Historien",
        },
        {"name": "RERO", "type": "organisation"},
    ]
    marc21xml = """
    <record>
      <datafield tag="100" ind1=" " ind2=" ">
        <subfield code="a">Jean-Paul</subfield>
        <subfield code="b">II</subfield>
        <subfield code="c">Pape</subfield>
        <subfield code="d">1954-</subfield>
      </datafield>
      <datafield tag="700" ind1=" " ind2="2">
        <subfield code="a">Dumont, Jean</subfield>
        <subfield code="c">Historien</subfield>
        <subfield code="d">1921-2014</subfield>
      </datafield>
      <datafield tag="710" ind1=" " ind2=" ">
        <subfield code="a">RERO</subfield>
        <subfield code="c">Martigny</subfield>
        <subfield code="d">1971</subfield>
      </datafield>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    authors = data.get("authors")
    assert authors == [
        {
            "name": "Jean-Paul II",
            "type": "person",
            "date": "1954-",
            "qualifier": "Pape",
        },
        {"name": "RERO", "type": "organisation"},
    ]


def test_marc21_to_publishers_publicationDate():
    """Test dojson publishers publicationDate."""

    marc21xml = """
    <record>
      <datafield tag="260" ind1=" " ind2=" ">
        <subfield code="a">Lausanne :</subfield>
        <subfield code="b">Payot,</subfield>
        <subfield code="c">2015</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("publishers") == [
        {"place": ["Lausanne"], "name": ["Payot"]}
    ]
    assert data.get("publicationYear") == 2015

    marc21xml = """
    <record>
      <datafield tag="260" ind1=" " ind2=" ">
        <subfield code="a">Paris ;</subfield>
        <subfield code="a">Lausanne :</subfield>
        <subfield code="b">Payot,</subfield>
        <subfield code="c">1920</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("publishers") == [
        {"place": ["Paris", "Lausanne"], "name": ["Payot"]}
    ]
    assert data.get("publicationYear") == 1920

    marc21xml = """
    <record>
      <datafield tag="260" ind1=" " ind2=" ">
        <subfield code="a">Paris :</subfield>
        <subfield code="b">Champion ;</subfield>
        <subfield code="a">Genève :</subfield>
        <subfield code="b">Droz,</subfield>
        <subfield code="c">1912-1955</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("publishers") == [
        {"place": ["Paris"], "name": ["Champion"]},
        {"place": ["Genève"], "name": ["Droz"]},
    ]
    assert data.get("freeFormedPublicationDate") == "1912-1955"
    assert data.get("publicationYear") == 1912


def test_marc21_to_description():
    """Test dojson extent, otherMaterialCharacteristics, formats."""
    marc21xml = """
    <record>
      <datafield tag="300" ind1=" " ind2=" ">
        <subfield code="d">test</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert not data

    marc21xml = """
    <record>
      <datafield tag="300" ind1=" " ind2=" ">
        <subfield code="a">116 p.</subfield>
        <subfield code="b">ill.</subfield>
        <subfield code="c">22 cm</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("extent") == "116 p."
    assert data.get("otherMaterialCharacteristics") == "ill."
    assert data.get("formats") == ["22 cm"]

    marc21xml = """
    <record>
      <datafield tag="300" ind1=" " ind2=" ">
        <subfield code="a">116 p.</subfield>
        <subfield code="b">ill.</subfield>
        <subfield code="c">22 cm</subfield>
        <subfield code="c">12 x 15</subfield>
      </datafield>
      <datafield tag="300" ind1=" " ind2=" ">
        <subfield code="a">200 p.</subfield>
        <subfield code="b">ill.</subfield>
        <subfield code="c">19 cm</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("extent") == "116 p."
    assert data.get("otherMaterialCharacteristics") == "ill."
    assert data.get("formats") == ["22 cm", "12 x 15"]


def test_marc21_to_series():
    """Test dojson series."""

    marc21xml = """
    <record>
      <datafield tag="490" ind1=" " ind2=" ">
        <subfield code="a">Collection One</subfield>
        <subfield code="v">5</subfield>
      </datafield>
      <datafield tag="490" ind1=" " ind2=" ">
        <subfield code="a">Collection Two</subfield>
        <subfield code="v">123</subfield>
      </datafield>    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("series") == [
        {"name": "Collection One", "number": "5"},
        {"name": "Collection Two", "number": "123"},
    ]


def test_marc21_to_abstract():
    """Test dojson abstract."""

    marc21xml = """
    <record>
      <datafield tag="520" ind1=" " ind2=" ">
        <subfield code="a">This book is about</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("abstracts") == ["This book is about"]


def test_marc21_to_identifiers():
    """Test dojson identifiers."""
    marc21xml = """
    <record>
      <datafield tag="020" ind1=" " ind2=" ">
        <subfield code="b">9782370550163</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("identifiers") is None

    marc21xml = """
    <record>
      <datafield tag="035" ind1=" " ind2=" ">
        <subfield code="a">R123456789</subfield>
      </datafield>
      <datafield tag="020" ind1=" " ind2=" ">
        <subfield code="a">9782370550163</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("identifiers") == {
        "reroID": "R123456789",
        "isbn": "9782370550163",
    }


def test_marc21_to_notes():
    """Test dojson notes."""

    marc21xml = """
    <record>
      <datafield tag="500" ind1=" " ind2=" ">
        <subfield code="a">note 1</subfield>
      </datafield>
      <datafield tag="500" ind1=" " ind2=" ">
        <subfield code="a">note 2</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("notes") == ["note 1", "note 2"]


def test_marc21_to_is_part_of():
    """Test dojson is_part_of."""

    marc21xml = """
    <record>
      <datafield tag="773" ind1="1" ind2=" ">
        <subfield code="t">Stuart Hall : critical dialogues</subfield>
        <subfield code="g">411</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("is_part_of") == "Stuart Hall : critical dialogues"


def test_marc21_to_subjects():
    """Test dojson subjects."""

    marc21xml = """
    <record>
      <datafield tag="666" ind1=" " ind2=" ">
        <subfield code="a">subject 1 ; subject 2</subfield>
      </datafield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("subjects") == ["subject 1", "subject 2"]


def test_marc21_to_pid():
    """Test dojson pid."""
    marc21xml = """
    <record>
      <controlfield tag="001">4316</controlfield>
    </record>
    """
    marc21json = create_record(marc21xml)
    data = marc21tojson.do(marc21json)
    assert data.get("pid") == "4316"
