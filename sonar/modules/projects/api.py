# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2019 RERO
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

"""Project Api."""

from functools import partial

from ..api import SonarIndexer, SonarRecord, SonarSearch
from ..fetchers import id_fetcher
from ..minters import id_minter
from ..providers import Provider

# provider
ProjectProvider = type('ProjectProvider', (Provider, ), dict(pid_type='proj'))
# minter
project_pid_minter = partial(id_minter, provider=ProjectProvider)
# fetcher
project_pid_fetcher = partial(id_fetcher, provider=ProjectProvider)


class ProjectSearch(SonarSearch):
    """Projects search."""

    class Meta:
        """Search only on item index."""

        index = 'projects'
        doc_types = []


class ProjectRecord(SonarRecord):
    """Project record."""

    minter = project_pid_minter
    fetcher = project_pid_fetcher
    provider = ProjectProvider
    schema = 'projects/project-v1.0.0.json'


class ProjectIndexer(SonarIndexer):
    """Project indexer."""

    record_cls = ProjectRecord
