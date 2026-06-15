# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test PDF extractor utils."""

import json
import os

from sonar.modules.pdf_extractor.utils import extract_text_from_content, format_extracted_data


def test_extract_text_from_content(app, pdf_file):
    """Test that text is correctly extracted from PDF binary content."""
    with open(pdf_file, "rb") as f:
        content = f.read()
    text = extract_text_from_content(content)
    assert isinstance(text, str)
    assert len(text) > 0


def test_format_extracted_data(app):
    """Test format extracted data."""
    # format_extracted_data({})
    json_file = os.path.join(os.path.dirname(__file__), "data", "extracted_data.json")

    with open(json_file, "rb") as file:
        # Test standard extraction
        extracted_data = json.load(file)
        formatted_data = format_extracted_data(extracted_data)
        assert "title" in formatted_data
        assert formatted_data["title"] == "Calibrated Ice Thickness Estimate for All Glaciers in Austria"
        assert len(formatted_data["authors"]) == 2
        assert formatted_data["authors"] == [
            {
                "affiliation": "Swiss Institute of Bioinformatics, Lausanne, Switzerland",
                "name": "Komljenovic, Andrea",
                "role": "cre",
            },
            {
                "affiliation": "Institute of Bioengineering, Laboratory of Integrative Systems "
                "Physiology, École Polytechnique Fédérale de Lausanne, Lausanne, "
                "Lausanne, Switzerland",
                "name": "Sleiman, Maroun Bou",
                "role": "cre",
            },
        ]

        # Test authors
        extracted_data["teiHeader"]["fileDesc"]["sourceDesc"]["biblStruct"]["analytic"]["author"] = extracted_data[
            "teiHeader"
        ]["fileDesc"]["sourceDesc"]["biblStruct"]["analytic"]["author"][0]

        formatted_data = format_extracted_data(extracted_data)
        assert len(formatted_data["authors"]) == 1

        # Test languages
        extracted_data["text"]["@xml:lang"] = "de"
        formatted_data = format_extracted_data(extracted_data)
        assert formatted_data["languages"][0] == "ger"

        # Test imprint
        extracted_data["teiHeader"]["fileDesc"]["sourceDesc"]["biblStruct"]["monogr"]["imprint"]["biblScope"] = (
            extracted_data["teiHeader"]["fileDesc"]["sourceDesc"]["biblStruct"]["monogr"]["imprint"]["biblScope"][0]
        )
        formatted_data = format_extracted_data(extracted_data)
        assert formatted_data["publication"]["publishedIn"] == "Frontiers in Earth Science"
        assert formatted_data["publication"]["volume"] == "7"
        assert formatted_data["documentDate"] == "2019"
