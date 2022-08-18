# -*- coding: utf-8 -*-
#
# SONAR
# Copyright (C) 2022 RERO+
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Initialize alembic."""


# revision identifiers, used by Alembic.
revision = "3d3309f660e4"
down_revision = None
branch_labels = ("sonar",)
depends_on = None


def upgrade():
    """Upgrade database."""


def downgrade():
    """Downgrade database."""
