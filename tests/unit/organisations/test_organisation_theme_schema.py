# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test organisation theme serialization."""

import pytest
from marshmallow import ValidationError

from sonar.modules.organisations.marshmallow.json import ThemeSchemaV1


def test_theme_colors_are_normalized():
    """Normalize saved colors to uppercase."""
    data = ThemeSchemaV1().load({"primaryColor": " #abcdef ", "secondaryColor": "#123456"})

    assert data == {"primaryColor": "#ABCDEF", "secondaryColor": "#123456"}


@pytest.mark.parametrize(
    "theme",
    [
        {"primaryColor": "#ABCDEF"},
        {"css": ".bg-header > .nav-link {\n  color: red;\n}"},
    ],
)
def test_theme_values_are_optional(theme):
    """Accept a theme that sets a single value."""
    assert ThemeSchemaV1().load(theme) == theme


@pytest.mark.parametrize("color", ["#123", "red", "#123456; color: red"])
def test_invalid_theme_colors_are_rejected(color):
    """Reject values that are not six-digit hexadecimal colors."""
    with pytest.raises(ValidationError):
        ThemeSchemaV1().load({"primaryColor": color, "secondaryColor": "#F68211"})


def test_css_closing_a_tag_is_rejected():
    """Reject CSS that could close the style tag of the page."""
    with pytest.raises(ValidationError):
        ThemeSchemaV1().load({"css": ".bg-header {}</style><script>alert(1)</script>"})
