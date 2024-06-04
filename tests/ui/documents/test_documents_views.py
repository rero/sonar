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

"""Test documents views."""

import pytest
from flask import g, render_template_string, url_for

import sonar.modules.documents.views as views


def test_contribution_text():
    """Test contribution text formatting."""
    # Just creator
    assert (
        views.contribution_text(
            {
                "agent": {"type": "bf:Person", "preferred_name": "John Doe"},
                "role": ["cre"],
            }
        )
        == "John Doe"
    )

    # Contributor
    assert (
        views.contribution_text(
            {
                "agent": {"type": "bf:Person", "preferred_name": "John Doe"},
                "role": ["ctb"],
            }
        )
        == "John Doe (contribution_role_ctb)"
    )

    # Meeting with only number
    assert (
        views.contribution_text(
            {
                "agent": {
                    "type": "bf:Meeting",
                    "preferred_name": "Meeting",
                    "number": "1234",
                }
            }
        )
        == "Meeting (1234)"
    )

    # Meeting with number and date
    assert (
        views.contribution_text(
            {
                "agent": {
                    "type": "bf:Meeting",
                    "preferred_name": "Meeting",
                    "number": "1234",
                    "date": "2019",
                }
            }
        )
        == "Meeting (1234 : 2019)"
    )

    # Meeting with number, date and place
    assert (
        views.contribution_text(
            {
                "agent": {
                    "type": "bf:Meeting",
                    "preferred_name": "Meeting",
                    "number": "1234",
                    "date": "2019",
                    "place": "Place",
                }
            }
        )
        == "Meeting (1234 : 2019 : Place)"
    )


def test_store_organisation(client, db, organisation):
    """Test store organisation in globals."""
    # Default view, no organisation stored.
    assert client.get(url_for("index", view="global")).status_code == 200
    assert not g.get("organisation")

    # Existing organisation stored, with shared view
    assert client.get(url_for("index", view="org")).status_code == 200
    assert g.organisation["code"] == "org"
    assert g.organisation["isShared"]

    # Non-existing organisation
    g.pop("organisation")
    assert client.get(url_for("index", view="non-existing")).status_code == 404
    assert not g.get("organisation")

    # Existing organisation without shared view
    organisation["isShared"] = False
    organisation.commit()
    db.session.commit()
    assert client.get(url_for("index", view="org")).status_code == 404
    assert not g.get("organisation")


def test_index(client):
    """Test frontpage."""
    assert client.get("/").status_code == 200


def test_search(app, client, organisation, collection):
    """Test search."""
    assert (
        client.get(
            url_for("documents.search", view="global", resource_type="documents")
        ).status_code
        == 200
    )

    # Test search with collection
    result = client.get(
        url_for(
            "documents.search",
            view=organisation["pid"],
            collection_view=collection["pid"],
            resource_type="documents",
        )
    )
    assert result.status_code == 200
    assert result.data.find(b"<h3>Collection name</h3>") != -1

    assert (
        client.get(
            url_for("documents.search", view="not-existing", resource_type="documents")
        ).status_code
        == 404
    )


def test_detail(app, client, organisation, document_with_file):
    """Test document detail page."""
    res = client.get(
        url_for(
            "invenio_records_ui.doc", view="global", pid_value=document_with_file["pid"]
        )
    )
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(res.data, "html.parser")
    assert organisation.get("pid") in soup.find(id="organisation").contents[0]

    assert res.status_code == 200

    assert (
        client.get(
            url_for("invenio_records_ui.doc", view="global", pid_value="not-existing")
        ).status_code
        == 404
    )


def test_title_format(document):
    """Test title format for display it in template."""
    # No title
    assert views.title_format({"mainTitle": [], "subtitle": []}, "en") == ""

    # Take the first one as fallback
    assert (
        views.title_format(
            {"mainTitle": [{"language": "spa", "value": "Title ES"}]}, "fr"
        )
        == "Title ES"
    )

    title = {
        "mainTitle": [
            {"language": "ger", "value": "Title DE"},
            {"language": "eng", "value": "Title EN"},
            {"language": "fre", "value": "Title FR"},
        ],
        "subtitle": [
            {"language": "ita", "value": "Subtitle IT"},
            {"language": "fre", "value": "Subtitle FR"},
            {"language": "eng", "value": "Subtitle EN"},
        ],
    }

    assert views.title_format(title, "en") == "Title EN : Subtitle EN"
    assert views.title_format(title, "fr") == "Title FR : Subtitle FR"
    assert views.title_format(title, "de") == "Title DE : Subtitle EN"
    assert views.title_format(title, "it") == "Title EN : Subtitle IT"


def test_create_publication_statement(document):
    """Test create publication statement."""
    publication_statement = views.create_publication_statement(
        document["provisionActivity"][0]
    )
    assert publication_statement
    assert (
        publication_statement["default"]
        == "Bienne : Impr. Weber, [2006] ; Lausanne ; Rippone : "
        "Impr. Coustaud"
    )


def test_nl2br(app):
    """Test nl2br conversion."""
    assert (
        render_template_string("{{ 'Multiline text\nMultiline text' | nl2br | safe}}")
        == "Multiline text<br>Multiline text"
    )


def test_get_code_from_bibliographic_language(app):
    """Test bibliographic language code to alpha 2 code conversion."""
    assert views.get_language_from_bibliographic_code("ger") == "de"

    assert views.get_language_from_bibliographic_code("ace") == ""

    with pytest.raises(Exception) as e:
        views.get_language_from_bibliographic_code("zzz")
    assert str(e.value) == 'Language code not found for "zzz"'


def test_get_preferred_languages(app):
    """Test getting the list of prefererred languages."""
    assert views.get_preferred_languages() == ["eng", "fre", "ger", "ita"]
    assert views.get_preferred_languages("fre") == ["fre", "eng", "ger", "ita"]


def test_file_size(app):
    """Test converting file size to a human readable size."""
    assert views.file_size(2889638) == "2.76Mb"


def test_has_external_urls_for_files(app):
    """Test if record has to point files to external URL or not."""
    assert views.has_external_urls_for_files(
        {"pid": 1, "organisation": [{"pid": "csal"}]}
    )

    assert not views.has_external_urls_for_files(
        {"pid": 1, "organisation": [{"pid": "usi"}]}
    )

    assert not views.has_external_urls_for_files({"pid": 1, "organisation": []})

    assert not views.has_external_urls_for_files({"pid": 1})


def test_part_of_format():
    """Test part of format for displaying."""
    assert (
        views.part_of_format(
            {
                "document": {
                    "title": "Mehr oder weniger Staat?",
                    "publication": {"statement": "doc statement"},
                    "contribution": ["contrib 1", "contrib 2", "contrib 3"],
                },
                "numberingYear": "2015",
                "numberingVolume": "28",
                "numberingIssue": "2",
                "numberingPages": "469-480",
            }
        )
        == "Mehr oder weniger Staat? / contrib 1 ; contrib 2 ; contrib 3. "
        "- doc statement. - 2015, vol. 28, no. 2, p. 469-480"
    )

    assert (
        views.part_of_format(
            {
                "document": {
                    "title": "Mehr oder weniger Staat?",
                    "publication": {"statement": "doc statement"},
                    "contribution": ["contrib 1"],
                },
                "numberingYear": "2015",
                "numberingVolume": "28",
                "numberingIssue": "2",
                "numberingPages": "469-480",
            }
        )
        == "Mehr oder weniger Staat? / contrib 1. - doc statement. "
        "- 2015, vol. 28, no. 2, p. 469-480"
    )

    assert (
        views.part_of_format(
            {
                "document": {
                    "title": "Mehr oder weniger Staat?",
                    "publication": {"statement": "doc statement"},
                },
                "numberingYear": "2015",
                "numberingVolume": "28",
                "numberingIssue": "2",
                "numberingPages": "469-480",
            }
        )
        == "Mehr oder weniger Staat?. - doc statement. - 2015, vol. 28, no. 2, p. 469-480"
    )

    assert (
        views.part_of_format(
            {
                "document": {
                    "title": "Mehr oder weniger Staat?",
                    "publication": {"statement": "doc statement"},
                }
            }
        )
        == "Mehr oder weniger Staat?. - doc statement."
    )

    assert (
        views.part_of_format(
            {
                "document": {"title": "Mehr oder weniger Staat?"},
                "numberingYear": "2015",
                "numberingVolume": "28",
                "numberingIssue": "2",
                "numberingPages": "469-480",
            }
        )
        == "Mehr oder weniger Staat?. - 2015, vol. 28, no. 2, p. 469-480"
    )

    assert (
        views.part_of_format(
            {
                "numberingYear": "2015",
                "numberingVolume": "28",
                "numberingIssue": "2",
                "numberingPages": "469-480",
            }
        )
        == "2015, vol. 28, no. 2, p. 469-480"
    )

    assert (
        views.part_of_format({"numberingVolume": "28", "numberingIssue": "2"})
        == "vol. 28, no. 2"
    )

    assert views.part_of_format({"numberingYear": "2015"}) == "2015"


def test_abstracts(app):
    """Test getting ordered abstracts."""
    # Abstracts are ordered, english first.
    abstracts = [
        {"language": "fre", "value": "Résumé"},
        {"language": "eng", "value": "Summary"},
    ]
    assert views.abstracts({"abstracts": abstracts})[0]["language"] == "eng"

    # No abstract
    assert views.abstracts({}) == []

    # Abstract with not defined key on preferred languages
    abstracts = [
        {"language": "fre", "value": "Résumé"},
        {"language": "eng", "value": "Summary"},
        {"language": "roh", "value": "Romancio"},
    ]
    abstracts_sort = views.abstracts({"abstracts": abstracts})
    assert ["eng", "fre", "roh"] == [abs["language"] for abs in abstracts_sort]

    abstracts = [
        {"language": "fre", "value": "Résumé"},
        {"language": "roh", "value": "Romancio"},
        {"language": "eng", "value": "Summary"},
        {"language": "kin", "value": "kin Summary"},
    ]
    abstracts_sort = views.abstracts({"abstracts": abstracts})
    assert ["eng", "fre", "kin", "roh"] == [abs["language"] for abs in abstracts_sort]


def test_contributors():
    """Test ordering and filtering contributors."""
    contributors = [
        {"role": ["dgs"]},
        {"role": ["dgc"]},
        {"role": ["ctb"]},
        {"role": ["prt"]},
        {"role": ["edt"]},
        {"role": ["cre"]},
    ]

    priorities = ["cre", "ctb", "dgs", "dgc", "edt", "prt"]

    for index, contributor in enumerate(
        views.contributors({"contribution": contributors})
    ):
        assert contributor["role"][0] == priorities[index]

    # No contributors
    assert views.contributors({}) == []

    contributors = [
        {"agent": {"preferred_name": "name 1", "type": "bf:Person"}, "role": ["cre"]},
        {"agent": {"preferred_name": "name 2", "type": "bf:Person"}, "role": ["cre"]},
        {"agent": {"preferred_name": "name 3", "type": "bf:Person"}, "role": ["cre"]},
        {
            "agent": {"preferred_name": "org 1", "type": "bf:Organization"},
            "role": ["cre"],
        },
        {
            "agent": {"preferred_name": "metting 1", "type": "bf:Meeting"},
            "role": ["cre"],
        },
    ]
    assert 4 == len(views.contributors({"contribution": contributors}))
    assert 1 == len(views.contributors({"contribution": contributors}, True))


def test_dissertation():
    """Test formatting of dissertation text."""
    # No dissertation
    assert not views.dissertation({})

    # Only degree property
    assert (
        views.dissertation({"dissertation": {"degree": "Thèse de doctorat"}})
        == "Thèse de doctorat"
    )

    #  With jury notes
    assert (
        views.dissertation(
            {"dissertation": {"degree": "Thèse de doctorat", "jury_note": "Jury note"}}
        )
        == "Thèse de doctorat (jury note: Jury note)"
    )

    # With granting institution
    assert (
        views.dissertation(
            {
                "dissertation": {
                    "degree": "Thèse de doctorat",
                    "jury_note": "Jury note",
                    "grantingInstitution": "Università della Svizzera italiana",
                }
            }
        )
        == "Thèse de doctorat: Università della Svizzera italiana (jury note: "
        "Jury note)"
    )

    # With date
    assert (
        views.dissertation(
            {
                "dissertation": {
                    "degree": "Thèse de doctorat",
                    "jury_note": "Jury note",
                    "grantingInstitution": "Università della Svizzera italiana",
                    "date": "2010-01-01",
                }
            }
        )
        == "Thèse de doctorat: Università della Svizzera italiana, 01.01.2010 "
        "(jury note: Jury note)"
    )


def test_project_detail(app, client, project):
    """Test project detail page."""
    assert (
        client.get(
            url_for("invenio_records_ui.proj", view="global", pid_value=project.id)
        ).status_code
        == 200
    )
    assert (
        client.get(
            url_for("invenio_records_ui.proj", view="global", pid_value="not-existing")
        ).status_code
        == 404
    )
    assert (
        client.get(
            url_for(
                "invenio_records_ui.proj", view="not-existing", pid_value=project.id
            )
        ).status_code
        == 404
    )


def test_language_value(app):
    """Test language value."""
    values = [
        {"language": "eng", "value": "Value ENG"},
        {"language": "fre", "value": "Value FRE"},
    ]
    assert (
        render_template_string("{{ values | language_value }}", values=values)
        == "Value ENG"
    )


def test_get_custom_field_label(app):
    """Test custom field label."""
    record = {
        "organisation": [
            {
                "documentsCustomField1": {
                    "label": [
                        {"language": "eng", "value": "Test ENG"},
                        {"language": "fre", "value": "Test FRE"},
                    ]
                }
            }
        ]
    }
    assert (
        render_template_string(
            "{{ record | get_custom_field_label(1) }}", record=record
        )
        == "Test ENG"
    )

    # No organisation
    record = {}
    assert (
        render_template_string(
            "{{ record | get_custom_field_label(1) }}", record=record
        )
        == "None"
    )

    # No index for custom field
    record = {
        "organisation": [
            {
                "documentsCustomField1": {
                    "label": [
                        {"language": "eng", "value": "Test ENG"},
                        {"language": "fre", "value": "Test FRE"},
                    ]
                }
            }
        ]
    }
    assert (
        render_template_string(
            "{{ record | get_custom_field_label(2) }}", record=record
        )
        == "None"
    )

    # No label
    record = {"organisation": [{"documentsCustomField1": {}}]}
    assert (
        render_template_string(
            "{{ record | get_custom_field_label(1) }}", record=record
        )
        == "None"
    )


def test_markdown_filter(app):
    """Test markdown to HTML conversion."""
    assert (
        render_template_string(
            "{{ 'Markdown text\nwith **strong** and *italic*' | markdown_filter"
            " | safe}}"
        )
        == "<p>Markdown text\nwith <strong>strong</strong> and <em>italic</em>"
        "</p>"
    )
