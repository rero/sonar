# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

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
