# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Unit tests for citation formatting."""

import pytest

from sonar.modules.documents.citations import citation_registry
from sonar.modules.documents.citations.csl_mapping import _get_date_parts, record_to_csl

ARTICLE = {
    "documentType": "coar:c_6501",
    "title": [{"type": "bf:Title", "mainTitle": [{"language": "eng", "value": "The Art of Testing"}]}],
    "contribution": [
        {"agent": {"type": "bf:Person", "preferred_name": "Smith, John"}, "role": ["cre"]},
        {"agent": {"type": "bf:Person", "preferred_name": "Doe, Jane"}, "role": ["cre"]},
    ],
    "provisionActivity": [
        {
            "type": "bf:Publication",
            "startDate": "2023",
            "statement": [
                {"type": "bf:Place", "label": [{"value": "London"}]},
                {"type": "bf:Agent", "label": [{"value": "Academic Press"}]},
            ],
        }
    ],
    "partOf": [
        {
            "document": {"title": "Journal of Research"},
            "numberingVolume": "10",
            "numberingIssue": "2",
            "numberingPages": "45-67",
        }
    ],
    "identifiedBy": [{"type": "bf:Doi", "value": "10.1000/xyz123"}],
}

BOOK = {
    "documentType": "coar:c_2f33",
    "title": [
        {
            "type": "bf:Title",
            "mainTitle": [{"language": "eng", "value": "Deep Learning"}],
            "subtitle": [{"language": "eng", "value": "A Practical Approach"}],
        }
    ],
    "contribution": [
        {"agent": {"type": "bf:Person", "preferred_name": "Lecun, Yann"}, "role": ["cre"]},
    ],
    "provisionActivity": [
        {
            "type": "bf:Publication",
            "startDate": "2021",
            "statement": [
                {"type": "bf:Place", "label": [{"value": "New York"}]},
                {"type": "bf:Agent", "label": [{"value": "MIT Press"}]},
            ],
        }
    ],
}

EDITOR_ONLY = {
    "documentType": "coar:c_2f33",
    "title": [{"type": "bf:Title", "mainTitle": [{"language": "eng", "value": "Collected Essays"}]}],
    "contribution": [
        {"agent": {"type": "bf:Person", "preferred_name": "Brown, Alice"}, "role": ["edt"]},
        {"agent": {"type": "bf:Person", "preferred_name": "Green, Bob"}, "role": ["edt"]},
    ],
    "provisionActivity": [
        {
            "type": "bf:Publication",
            "startDate": "2020",
            "statement": [
                {"type": "bf:Place", "label": [{"value": "Oxford"}]},
                {"type": "bf:Agent", "label": [{"value": "Oxford UP"}]},
            ],
        }
    ],
}

BOOK_WITH_CONTRIBUTOR = {
    **BOOK,
    "contribution": [
        {"agent": {"type": "bf:Person", "preferred_name": "Doe, Jane"}, "role": ["cre"]},
        {"agent": {"type": "bf:Person", "preferred_name": "Brown, Alan"}, "role": ["ctb"]},
    ],
}

BOOK_WITH_MEETING = {
    **BOOK,
    "contribution": [
        *BOOK["contribution"],
        {
            "agent": {
                "type": "bf:Meeting",
                "preferred_name": "International Conference on Testing",
                "place": "Geneva",
                "date": "2019",
            }
        },
    ],
}

MULTILANG = {
    "title": [
        {
            "type": "bf:Title",
            "mainTitle": [
                {"language": "fre", "value": "La science des données"},
                {"language": "eng", "value": "Data Science"},
            ],
        }
    ],
    "contribution": [
        {"agent": {"type": "bf:Person", "preferred_name": "Martin, Pierre"}, "role": ["cre"]},
    ],
    "provisionActivity": [
        {
            "type": "bf:Publication",
            "startDate": "2022",
            "statement": [{"type": "bf:Agent", "label": [{"value": "Dunod"}]}],
        }
    ],
}


def test_unsupported_style():
    """Unsupported style raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported citation style"):
        citation_registry.format(ARTICLE, "bibtex")


# --- APA ---


def test_apa_article():
    """APA journal article citation.

    The space before the DOI is a regression guard: citeproc-py 0.10.0 had
    a spacing bug that dropped it (fixed upstream in 0.10.1, see the
    registry module docstring).
    """
    result = citation_registry.format(ARTICLE, "apa_7")
    assert "Smith, J." in result
    assert "Doe, J." in result
    assert "(2023)" in result
    assert "The Art of Testing" in result
    assert "<i>Journal of Research</i>" in result
    assert "<i>10</i>(2)" in result
    assert "45" in result and "67" in result
    assert " https://doi.org/10.1000/xyz123" in result


def test_apa_book():
    """APA book citation with subtitle."""
    result = citation_registry.format(BOOK, "apa_7")
    assert "Lecun, Y." in result
    assert "(2021)" in result
    assert "Deep Learning: A Practical Approach" in result
    assert "MIT Press" in result


def test_apa_editors():
    """APA falls back to editors with (eds.) suffix, CSL-native."""
    result = citation_registry.format(EDITOR_ONLY, "apa_7")
    assert "Brown, A." in result
    assert "(eds.)" in result


# --- Chicago ---


def test_chicago_article():
    """Chicago journal article citation, including a page range.

    A page range in the source data is a deliberate regression guard: the
    upstream chicago-author-date.csl revision published after this file was
    vendored sets page-range-format="chicago-16", a value citeproc-py 0.10.0
    does not handle, which crashes on any cited page range. See the pinning
    note in registry.py.
    """
    result = citation_registry.format(ARTICLE, "chicago_17")
    assert "Smith, John" in result
    assert "2023" in result
    assert "“The Art of Testing”" in result
    assert "<i>Journal of Research</i>" in result


def test_chicago_book():
    """Chicago book citation."""
    result = citation_registry.format(BOOK, "chicago_17")
    assert "<i>Deep Learning: A Practical Approach</i>" in result
    assert "Lecun, Yann" in result
    assert "New York" in result
    assert "MIT Press" in result


def test_chicago_editors():
    """Chicago falls back to editors with eds. suffix, CSL-native."""
    result = citation_registry.format(EDITOR_ONLY, "chicago_17")
    assert "Brown, Alice" in result
    assert "eds." in result


# --- MLA ---


def test_mla_article():
    """MLA journal article citation."""
    result = citation_registry.format(ARTICLE, "mla_9")
    assert "Smith, J." in result
    assert "“The Art of Testing”" in result
    assert "<i>Journal of Research</i>" in result
    assert "pp. 45" in result and "67" in result
    assert "2023" in result


def test_mla_three_authors_et_al():
    """MLA uses et al. for 3+ authors."""
    record = {
        **ARTICLE,
        "contribution": [
            {"agent": {"type": "bf:Person", "preferred_name": "A, One"}, "role": ["cre"]},
            {"agent": {"type": "bf:Person", "preferred_name": "B, Two"}, "role": ["cre"]},
            {"agent": {"type": "bf:Person", "preferred_name": "C, Three"}, "role": ["cre"]},
        ],
    }
    result = citation_registry.format(record, "mla_9")
    assert "et al." in result


def test_mla_book():
    """MLA book citation."""
    result = citation_registry.format(BOOK, "mla_9")
    assert "<i>Deep Learning: A Practical Approach</i>" in result
    assert "MIT Press" in result


# --- Harvard ---


def test_harvard_article():
    """Harvard journal article citation."""
    result = citation_registry.format(ARTICLE, "harvard_12")
    assert "Smith, J." in result
    assert "(2023)" in result
    assert "“The Art of Testing”" in result
    assert "<i>Journal of Research</i>" in result


def test_harvard_book():
    """Harvard book citation."""
    result = citation_registry.format(BOOK, "harvard_12")
    assert "Lecun, Y." in result
    assert "(2021)" in result
    assert "<i>Deep Learning: A Practical Approach</i>" in result
    assert "New York: MIT Press" in result


def test_harvard_editors():
    """Harvard falls back to editors with (eds.) suffix, CSL-native."""
    result = citation_registry.format(EDITOR_ONLY, "harvard_12")
    assert "Brown, A." in result
    assert "(eds.)" in result


# --- Language selection ---


def test_lang_param_selects_title():
    """Lang param selects the matching mainTitle."""
    assert "La science des données" in citation_registry.format(MULTILANG, "apa_7", lang="fre")
    assert "Data Science" in citation_registry.format(MULTILANG, "apa_7", lang="eng")


def test_lang_param_fallback_to_first():
    """Unknown lang falls back to first mainTitle."""
    result = citation_registry.format(MULTILANG, "apa_7", lang="deu")
    assert "La science des données" in result


# --- Edge cases ---


def test_no_authors():
    """Record with no contribution produces a citation without author."""
    record = {**BOOK, "contribution": []}
    result = citation_registry.format(record, "apa_7")
    assert "Deep Learning" in result


def test_no_publication_date():
    """Missing publication date uses n.d."""
    record = {**BOOK, "provisionActivity": []}
    result = citation_registry.format(record, "apa_7")
    assert "(n.d.)" in result


def test_year_fallback_to_part_of_numbering_year():
    """Missing provisionActivity falls back to partOf[0].numberingYear.

    provisionActivity is not required for most article and book chapter
    types, so the year must still be found via partOf when absent.
    """
    record = {
        "documentType": "coar:c_6501",
        "title": [{"type": "bf:Title", "mainTitle": [{"language": "eng", "value": "An article without dates"}]}],
        "contribution": [{"agent": {"type": "bf:Person", "preferred_name": "Doe, Jane"}, "role": ["cre"]}],
        "partOf": [{"document": {"title": "Some Journal"}, "numberingYear": "2018", "numberingVolume": "3"}],
    }
    assert record_to_csl(record)["issued"] == {"date-parts": [[2018]]}
    assert "(2018)" in citation_registry.format(record, "apa_7")


def test_year_fallback_to_dissertation_date():
    """Missing provisionActivity falls back to dissertation.date for theses.

    dissertation.date may carry full day precision, like startDate, so the
    full date is preserved rather than truncated to the year.
    """
    record = {
        "documentType": "coar:c_46ec",
        "title": [
            {"type": "bf:Title", "mainTitle": [{"language": "eng", "value": "A thesis without provisionActivity"}]}
        ],
        "contribution": [{"agent": {"type": "bf:Person", "preferred_name": "Roe, Richard"}, "role": ["cre"]}],
        "dissertation": {
            "degree": "PhD thesis",
            "grantingInstitution": "University of Somewhere",
            "date": "2017-05-05",
        },
    }
    assert record_to_csl(record)["issued"] == {"date-parts": [[2017, 5, 5]]}
    assert "(2017)" in citation_registry.format(record, "apa_7")


def test_year_provision_activity_takes_precedence():
    """A year in provisionActivity wins over partOf.numberingYear."""
    record = {
        "documentType": "coar:c_6501",
        "title": [{"type": "bf:Title", "mainTitle": [{"language": "eng", "value": "An article"}]}],
        "provisionActivity": [{"type": "bf:Publication", "startDate": "2020", "statement": []}],
        "partOf": [{"document": {"title": "Some Journal"}, "numberingYear": "2018"}],
    }
    assert record_to_csl(record)["issued"] == {"date-parts": [[2020]]}


def test_full_date_preserved_when_available():
    """A full startDate (year-month-day) is preserved, not truncated to year.

    APA and MLA render the month/day themselves for document types where
    their convention calls for it (e.g. newspaper articles), so the full
    date must be passed through in date-parts.
    """
    record = {
        "documentType": "coar:c_998f",
        "title": [{"type": "bf:Title", "mainTitle": [{"language": "eng", "value": "Breaking news"}]}],
        "contribution": [{"agent": {"type": "bf:Person", "preferred_name": "Doe, Jane"}, "role": ["cre"]}],
        "provisionActivity": [{"type": "bf:Publication", "startDate": "2020-05-15", "statement": []}],
    }
    assert record_to_csl(record)["issued"] == {"date-parts": [[2020, 5, 15]]}
    assert "(2020, May 15)" in citation_registry.format(record, "apa_7")


def test_year_only_date_still_works():
    """A year-only startDate still produces a year-only date-parts."""
    record = {
        "documentType": "coar:c_998f",
        "title": [{"type": "bf:Title", "mainTitle": [{"language": "eng", "value": "Breaking news"}]}],
        "provisionActivity": [{"type": "bf:Publication", "startDate": "2020", "statement": []}],
    }
    assert record_to_csl(record)["issued"] == {"date-parts": [[2020]]}


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2020", [2020]),
        ("2020-05-15", [2020, 5, 15]),
        ("2020-5-15", [2020]),
        (None, None),
        ("", None),
    ],
)
def test_get_date_parts(value, expected):
    """_get_date_parts parses year or full date, and rejects malformed input."""
    assert _get_date_parts(value) == expected


# --- Document types ---


def test_thesis_fields():
    """Thesis-specific fields (degree, granting institution) are rendered."""
    record = {
        "documentType": "coar:c_46ec",
        "title": [{"type": "bf:Title", "mainTitle": [{"language": "eng", "value": "A Thesis About Things"}]}],
        "contribution": [{"agent": {"type": "bf:Person", "preferred_name": "Roe, Richard"}, "role": ["cre"]}],
        "provisionActivity": [{"type": "bf:Publication", "startDate": "2021", "statement": []}],
        "dissertation": {"degree": "PhD thesis", "grantingInstitution": "University of Somewhere"},
    }
    result = citation_registry.format(record, "chicago_17")
    assert "PhD thesis" in result
    assert "University of Somewhere" in result


# --- Names by role ---


def test_creator_and_editor_both_present():
    """A document with both a creator and an editor keeps both, not a fallback."""
    record = {
        **BOOK,
        "contribution": [
            {"agent": {"type": "bf:Person", "preferred_name": "Doe, Jane"}, "role": ["cre"]},
            {"agent": {"type": "bf:Person", "preferred_name": "Smith, John"}, "role": ["edt"]},
        ],
    }
    csl = record_to_csl(record)
    assert csl["author"] == [{"family": "Doe", "given": "Jane"}]
    assert csl["editor"] == [{"family": "Smith", "given": "John"}]


def test_contributor_role_mapped():
    """A ctb contribution maps to the CSL contributor variable."""
    assert record_to_csl(BOOK_WITH_CONTRIBUTOR)["contributor"] == [{"family": "Brown", "given": "Alan"}]


def test_meeting_excluded_from_names():
    """A bf:Meeting contribution never lands in author/editor/contributor."""
    csl = record_to_csl(BOOK_WITH_MEETING)
    names = [name for names in ("author", "editor", "contributor") for name in csl.get(names, [])]
    assert {"literal": "International Conference on Testing"} not in names
    assert csl["event"] == "International Conference on Testing"


def test_organisation_name_not_split():
    """A corporate author is passed as a single literal name, never split on a comma."""
    record = {
        **BOOK,
        "contribution": [
            {"agent": {"type": "bf:Organisation", "preferred_name": "ACME, Inc."}, "role": ["cre"]},
        ],
    }
    assert record_to_csl(record)["author"] == [{"literal": "ACME, Inc."}]


@pytest.mark.parametrize("style", ["apa_7", "chicago_17", "mla_9", "harvard_12"])
def test_contributor_does_not_crash_apa_or_mla(style):
    """A ctb-only contribution on a book (no editor) does not crash APA/MLA.

    citeproc-py 0.10.0 does not know the CSL "contributor" variable and
    crashes when a style tries to render it for a book/report with no
    editor. The registry must drop it for the affected styles.
    """
    assert "Doe" in citation_registry.format(BOOK_WITH_CONTRIBUTOR, style)


# --- Additional CSL-JSON fields ---


def test_csl_mapping_edition():
    """editionStatement.editionDesignation.value maps to CSL edition."""
    record = {**BOOK, "editionStatement": {"editionDesignation": {"value": "3rd ed."}}}
    assert record_to_csl(record)["edition"] == "3rd ed."


def test_csl_mapping_no_edition():
    """Missing editionStatement produces no edition field."""
    assert "edition" not in record_to_csl(BOOK)


def test_csl_mapping_series():
    """series[].name/number map to CSL collection-title/collection-number."""
    record = {**BOOK, "series": [{"name": "Some Series", "number": "5"}]}
    csl = record_to_csl(record)
    assert csl["collection-title"] == "Some Series"
    assert csl["collection-number"] == "5"


def test_csl_mapping_series_without_number():
    """A series entry without a number maps only collection-title."""
    record = {**BOOK, "series": [{"name": "Some Series"}]}
    csl = record_to_csl(record)
    assert csl["collection-title"] == "Some Series"
    assert "collection-number" not in csl


def test_csl_mapping_meeting():
    """A bf:Meeting contribution maps to CSL event/event-place/event-date."""
    csl = record_to_csl(BOOK_WITH_MEETING)
    assert csl["event"] == "International Conference on Testing"
    assert csl["event-place"] == "Geneva"
    assert csl["event-date"] == {"date-parts": [[2019]]}


def test_csl_mapping_no_meeting():
    """No bf:Meeting contribution produces no event fields."""
    csl = record_to_csl(BOOK)
    assert "event" not in csl
    assert "event-place" not in csl
    assert "event-date" not in csl


@pytest.mark.parametrize(
    ("extent", "expected"),
    [
        ("103 p", "103"),
        ("XII, 250 p.", "250"),
        ("", None),
    ],
)
def test_csl_mapping_number_of_pages(extent, expected):
    """Extent is reduced to the first integer found as number-of-pages."""
    record = {**BOOK, "extent": extent}
    assert record_to_csl(record).get("number-of-pages") == expected
