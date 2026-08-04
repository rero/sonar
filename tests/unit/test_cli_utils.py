# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Test utils CLI."""

from sonar.modules.cli.utils import has_spdx_header, needs_spdx_header


def test_needs_spdx_header(tmp_path):
    """Test the selection of the files requiring a license header."""
    (script := tmp_path / "server").write_text("#!/usr/bin/env bash\necho\n")
    (plain := tmp_path / "LICENSE").write_text("GNU AFFERO GENERAL PUBLIC LICENSE\n")

    assert needs_spdx_header("sonar/modules/cli/utils.py")
    assert needs_spdx_header("docker/nginx/Dockerfile")
    assert needs_spdx_header(str(script))
    assert not needs_spdx_header(str(plain))
    assert not needs_spdx_header("tests/ui/data/harvested_record.xml")
    assert not needs_spdx_header("sonar/templates/security/email/reset_notice.txt")
    # third party citation styles keep their own copyright
    assert not needs_spdx_header("sonar/modules/documents/citations/styles/apa-7th-edition.csl")
    assert not needs_spdx_header(".github/workflows/release.yml")


def test_has_spdx_header(tmp_path):
    """Test the detection of the license header."""
    copyright_tag = "SPDX-FileCopyrightText: Fondation RERO+"
    license_tag = "SPDX-License-Identifier: AGPL-3.0-or-later"

    def write(name, content):
        (file_path := tmp_path / name).write_text(content)
        return str(file_path)

    assert has_spdx_header(write("api.py", f"# {copyright_tag}\n# {license_tag}\n"))
    assert has_spdx_header(write("page.html", f"{{# {copyright_tag} #}}\n{{# {license_tag} #}}\n"))
    assert has_spdx_header(write("README.md", f"<!--\n{copyright_tag}\n{license_tag}\n-->\n"))
    # missing tag, wrong license and header pushed out of the first lines
    assert not has_spdx_header(write("no_license.py", f"# {copyright_tag}\n"))
    assert not has_spdx_header(write("wrong_license.py", f"# {copyright_tag}\n# SPDX-License-Identifier: MIT\n"))
    assert not has_spdx_header(write("too_late.py", f"{'\n' * 5}# {copyright_tag}\n# {license_tag}\n"))
