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

"""Test Elasticsearch cli commands."""

import datetime

from click.testing import CliRunner
from invenio_search import current_search_client
from mock import patch

from sonar.elasticsearch.cli import backup, create_repository, restore


def test_create_repository(app, script_info):
    """Test create repository."""
    runner = CliRunner()

    # OK
    result = runner.invoke(create_repository, obj=script_info)
    assert result.output == "Create a repository for snapshots\nDone\n"

    # Repository creation failed
    with patch(
        "invenio_search.current_search_client.snapshot.create_repository",
        side_effect=Exception("Mocked error"),
    ):
        result = runner.invoke(create_repository, obj=script_info)
        assert result.output == "Create a repository for snapshots\nMocked error\n"


def test_backup(app, script_info):
    """Test backup."""
    runner = CliRunner()

    # OK
    current_search_client.snapshot.create_repository("backup", {"type": "fs", "settings": {"location": "backup"}})
    result = runner.invoke(backup, ["--name", "test"], obj=script_info)
    assert result.output == "Backup elasticsearch data\nDone\n"

    # Snapshot with no name
    result = runner.invoke(backup, obj=script_info)
    assert f"snapshot-{datetime.date.today().strftime('%Y-%m-%d')}" in result.output

    # Not existing repository
    current_search_client.snapshot.delete("backup", "test")
    current_search_client.snapshot.delete_repository("backup")
    result = runner.invoke(backup, obj=script_info)
    assert "repository_missing_exception" in result.output


def test_restore(app, script_info):
    """Test restore."""
    runner = CliRunner()

    current_search_client.snapshot.create_repository("backup", {"type": "fs", "settings": {"location": "backup"}})
    result = runner.invoke(backup, ["--name", "test", "--wait"], obj=script_info)

    # OK
    result = runner.invoke(restore, ["--name", "test", "--yes-i-know"], obj=script_info)
    assert result.output == "Restore elasticsearch data\nDone\n"

    # Unexisting snapshot
    result = runner.invoke(restore, ["--name", "unexisting", "--yes-i-know"], obj=script_info)
    assert "snapshot does not exist" in result.output

    # Aborting
    result = runner.invoke(restore, ["--name", "test"], obj=script_info, input="N")
    assert "Aborted!\n" in result.output
