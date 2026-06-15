# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Babel extractors tests."""

from os.path import dirname, join

import pytest

from sonar.modules.babel_extractors import extract_json


@pytest.fixture(scope="module")
def babel_filehandle():
    """Load fake JSON schema structure."""
    return open(join(dirname(__file__), "..", "data", "babel_extraction.json"), "rb")


def test_babel_extractors_extract_json(babel_filehandle):
    """Test extract json."""
    translations = extract_json(
        fileobj=babel_filehandle,
        keywords=None,
        comment_tags=None,
        options={"keys_to_translate": "['title']"},
    )

    assert translations == [
        (4, "gettext", "Fake schema", []),
        (13, "gettext", "Schema", []),
        (19, "gettext", "Identifier", []),
        (24, "gettext", "Name", []),
    ]
