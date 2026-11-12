# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test organisations CLI commands."""

import pytest
from click.testing import CliRunner

from sonar.modules.organisations import cli
from sonar.modules.organisations.api import OrganisationRecord


@pytest.fixture()
def dedicated_organisation(make_organisation):
    """Create a dedicated organisation."""
    return make_organisation("dedicated", is_shared=False)


def get_theme(code):
    """Return the stored theme of an organisation."""
    return OrganisationRecord.get_record_by_pid(code).get("theme")


def test_set_theme(app, script_info, dedicated_organisation, tmp_path):
    """Set each theme value without losing the others."""
    css = ".bg-header > .nav-link {\n  color: red;\n}\n"
    css_file = tmp_path / "theme.css"
    css_file.write_text(css)
    runner = CliRunner()

    result = runner.invoke(cli.set_theme, ["dedicated", "--primary", "#abcdef"], obj=script_info)
    assert result.exit_code == 0
    assert get_theme("dedicated") == {"primaryColor": "#ABCDEF"}

    runner.invoke(cli.set_theme, ["dedicated", "--secondary", "#123456"], obj=script_info)
    runner.invoke(cli.set_theme, ["dedicated", "--css", str(css_file)], obj=script_info)
    assert get_theme("dedicated") == {
        "primaryColor": "#ABCDEF",
        "secondaryColor": "#123456",
        "css": css,
    }


@pytest.mark.parametrize(
    ("code", "args", "message"),
    [
        ("dedicated", [], "Nothing to set"),
        ("dedicated", ["--primary", "red"], "primaryColor"),
        ("dedicated", ["--css", "-"], "css"),
        ("unknown", ["--primary", "#ABCDEF"], "does not exist"),
        ("org", ["--primary", "#ABCDEF"], "not dedicated"),
    ],
)
def test_set_theme_errors(app, script_info, organisation, dedicated_organisation, code, args, message):
    """Reject invalid values and organisations without changing any theme."""
    result = CliRunner().invoke(cli.set_theme, [code, *args], input="</style>", obj=script_info)

    assert result.exit_code != 0
    assert message in result.output
    assert not get_theme("dedicated")
    assert not get_theme("org")


def test_remove_theme(app, script_info, dedicated_organisation):
    """Remove the whole theme of an organisation."""
    runner = CliRunner()
    runner.invoke(cli.set_theme, ["dedicated", "--primary", "#ABCDEF"], obj=script_info)

    result = runner.invoke(cli.remove_theme, ["dedicated"], obj=script_info)
    assert result.exit_code == 0
    assert not get_theme("dedicated")

    result = runner.invoke(cli.remove_theme, ["dedicated"], obj=script_info)
    assert "has no theme" in result.output

    result = runner.invoke(cli.remove_theme, ["unknown"], obj=script_info)
    assert "does not exist" in result.output
