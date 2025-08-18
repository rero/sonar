# Swiss Open Access Repository
# Copyright (C) 2022 RERO
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

"""Utils functions for organisations module."""

import markdown
from bs4 import BeautifulSoup


def platform_name(organisation):
    """Get platform name."""
    platform_name = organisation.get("platformName")
    if platform_name:
        html = markdown.markdown(platform_name)
        return "".join(BeautifulSoup(html).findAll(text=True)).replace("\n", " - ")
    return None
