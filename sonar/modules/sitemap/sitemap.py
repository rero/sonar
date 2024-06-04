# -*- coding: utf-8 -*-
#
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

"""Sitemap."""

import glob
import math
import os
from datetime import datetime

from flask import current_app, url_for

from sonar.modules.documents.api import DocumentSearch
from sonar.modules.organisations.api import OrganisationSearch


def sitemap_generate(server_name, size=10000):
    """Generate a sitemap.

    :param: server_name: organisation server name.
    :param: size: size of the set of sitemarp urls.
    """
    # Find Organisation by server name and set view and server name
    search = DocumentSearch()
    if org_pid := OrganisationSearch().get_organisation_pid_by_server_name(server_name):
        search = search.filter("term", organisation__pid=org_pid)
    else:
        server_name = current_app.config.get("SONAR_APP_SERVER_NAME")
        org_pid = current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION")

    with current_app.test_request_context(f"https://{server_name}"):
        files_splitted = 0
        file_name = "sitemap.xml"
        folder = []
        if org_pid != current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION"):
            folder.append(org_pid)
        sitemap_folder = os.path.join(
            current_app.config.get("SONAR_APP_SITEMAP_FOLDER_PATH"), *folder
        )
        sitemap_file = os.path.join(sitemap_folder, file_name)
        # Create a destination directory
        _create_folder_or_remove_files(sitemap_folder)

        if count := search.count():
            # Elasticsearch query for current organisation
            hits = (
                search.sort({"_updated": "asc"})
                .params(preserve_order=True)
                .source(["pid", "_updated"])
                .scan()
            )

            if count > size:
                # In multiple files mode, generate the index
                files_splitted = math.ceil(count / size)
                _generate_index_sitemap(sitemap_file, org_pid, files_splitted)

            _generate_sitemap(
                sitemap_folder,
                sitemap_file,
                file_name,
                org_pid,
                files_splitted,
                hits,
                size,
            )


def _create_folder_or_remove_files(sitemap_folder):
    """Create a folder or remove all files.

    :param: sitemap_folder: folder path.
    """
    # Create a destination directory
    if not os.path.isdir(sitemap_folder):
        # Recursive
        os.makedirs(sitemap_folder)

    # remove all files into the current folder
    for file in glob.glob(f"{sitemap_folder}/*.xml"):
        os.remove(file)


def _get_url_sets(hits, max, org_pid, last=True):
    """Get url sets."""
    n = 0
    for hit in hits:
        yield {
            "loc": url_for(
                "invenio_records_ui.doc",
                view=org_pid,
                pid_value=hit.pid,
                _external=True,
            ),
            "lastmod": datetime.fromisoformat(hit._updated).strftime("%Y-%m-%d"),
        }
        n += 1
        if not last and n == max:
            break


def _generate_index_sitemap(sitemap_file, org_pid, files_splitted):
    """Generate sitemap index for more one file of urls.

    :param: sitemap_file: sitemap file path.
    :param: org_pid: organisation pid.
    :param: files_splitted: Number of indexes to generate.
    """

    def get_splitted_files():
        for i in range(1, files_splitted + 1):
            yield {
                "loc": url_for(
                    "sitemap.sitemap_index", view=org_pid, index=i, _external=True
                )
            }

    template = current_app.jinja_env.get_template("sonar/sitemap_index.xml")
    rv = template.stream(sitemaps=get_splitted_files())
    rv.dump(sitemap_file)


def _generate_sitemap(
    sitemap_folder, sitemap_file, file_name, org_pid, files_splitted, hits, size
):
    """Generate the sitemap file(s).

    :param: sitemap_folder: destination folder.
    :param: sitemap_file: file path.
    :param: file_name: file name.
    :param: org_pid: Organisation pid.
    :param: files_splitted: Number of sitemap file to generate.
    :param: hits: search ES query scan.
    :param: size: Size of the set.
    """
    # Get the template
    template = current_app.jinja_env.get_template("sonar/sitemap.xml")

    if files_splitted > 1:
        # Multiple files
        file = file_name.split(".")
        for i in range(1, files_splitted + 1):
            file_path = os.path.join(sitemap_folder, f"{file[0]}_{i}.xml")
            rv = template.stream(
                urlsets=_get_url_sets(hits, size, org_pid, files_splitted == i)
            )
            rv.enable_buffering(100)
            rv.dump(file_path)
    else:
        # Single file
        rv = template.stream(urlsets=_get_url_sets(hits, size, org_pid))
        rv.enable_buffering(100)
        rv.dump(sitemap_file)
