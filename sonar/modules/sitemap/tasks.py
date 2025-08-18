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

"""Tasks for sitemap."""

from celery import shared_task
from flask import current_app

from sonar.modules.organisations.api import OrganisationSearch
from sonar.modules.sitemap.sitemap import sitemap_generate


@shared_task(ignore_result=True)
def sitemap_generate_task():
    """Generate sitemap.

    Used as celery task. "ignore_result" flag means that we don't want to
    get the status and/or the result of the task, execution is faster.
    """
    # Generate sitemap only on production state
    if not current_app.config.get("SONAR_APP_PRODUCTION_STATE", False):
        return

    size = current_app.config.get("SONAR_APP_SITEMAP_ENTRY_SIZE", 10000)
    # Generate dedicated organisations sitemaps
    orgs = OrganisationSearch().get_dedicated_list()
    for org in orgs:
        if server_name := org.serverName:
            sitemap_generate(server_name, size)

    # Generate global sitemap
    sitemap_generate(current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION"), size)
