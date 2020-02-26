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

"""SONAR documents configuration."""

SONAR_DOCUMENTS_IMPORT_FILES = True
"""Import files associated with the document."""

SONAR_DOCUMENTS_EXTRACT_FULLTEXT_ON_IMPORT = True
"""Automatically extract fulltext when a file is imported."""

SONAR_DOCUMENTS_GENERATE_THUMBNAIL = True
"""Automatically generate a thumbnail when a file is imported."""

SONAR_DOCUMENTS_INSTITUTIONS_EXTERNAL_FILES = ['csal']
"""Display external files URL for these institutions."""
