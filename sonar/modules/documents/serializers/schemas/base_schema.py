# -*- coding: utf-8 -*-
#
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

"""Base schema for marshmallow serialization."""

import re

from flask import request
from marshmallow import Schema, pre_dump

from sonar.modules.documents.api import DocumentRecord
from sonar.modules.documents.utils import (
    has_external_urls_for_files,
    populate_files_properties,
)


class BaseSchema(Schema):
    """Base schema for marshmallow serialization."""

    @pre_dump
    def pre_dump(self, item, **kwargs):
        """Do some transformations in record before dumping it.

        - Store the main file to use it in methods.
        - Check if files must point to an external URL.
        - Populate restrictions, thumbnail and URL in files.

        :param item: Item object to process
        :returns: Modified item
        """
        if not item["metadata"].get("_files"):
            return item

        # Store the main file
        main_file = self.get_main_file(item)
        if main_file:
            item["metadata"]["mainFile"] = main_file

        # Check if organisation record forces to point file to an external url
        item["metadata"]["external_url"] = has_external_urls_for_files(item["metadata"])

        # Add restriction, link and thumbnail to files
        populate_files_properties(item["metadata"])

        return item

    def get_main_file(self, obj):
        """Return the main file.

        :param obj: Record dict.
        :returns: Main file or None.
        """
        files = [
            file
            for file in obj["metadata"].get("_files", [])
            if file.get("type") == "file"
        ]
        files = sorted(files, key=lambda file: file.get("order", 100))
        return files[0] if files else None

    def get_id(self, obj):
        """Get id."""
        return DocumentRecord.get_permanent_link(
            host=request.host_url, pid=obj["metadata"]["pid"]
        )

    def get_title(self, obj):
        """Get title."""
        for title in obj["metadata"].get("title", []):
            return title["mainTitle"][0]["value"]

        return None

    def get_start_date(self, obj):
        """Get start date."""
        for provision_activity in obj["metadata"].get("provisionActivity", []):
            if provision_activity[
                "type"
            ] == "bf:Publication" and provision_activity.get("startDate"):
                return provision_activity["startDate"]

        return None

    def get_keywords(self, obj):
        """Get keywords."""
        items = []

        for subjects in obj["metadata"].get("subjects", []):
            items = items + subjects["label"]["value"]

        return items

    def get_url(self, obj):
        """Get url."""
        if obj["metadata"].get("mainFile", {}).get("links"):
            if obj["metadata"]["mainFile"]["links"].get("download"):
                return "{host}{image}".format(
                    host=request.host_url.rstrip("/"),
                    image=obj["metadata"]["mainFile"]["links"]["download"],
                )

            if obj["metadata"]["mainFile"]["links"].get("external"):
                return obj["metadata"]["mainFile"]["links"]["external"]

        return None

    def get_pages(self, obj):
        """Get pages.

        :param obj: Record dict.
        :returns: Pages stored in partOf
        """
        for part_of in obj["metadata"].get("partOf", []):
            if part_of.get("numberingPages"):
                return part_of["numberingPages"]

        return None

    def get_first_page(self, obj):
        """Get the first page.

        :param obj: Record dict.
        :returns: The first page.
        """
        for part_of in obj["metadata"].get("partOf", []):
            if part_of.get("numberingPages"):
                matches = re.match(r"^([0-9]+)", part_of["numberingPages"])

                return matches.group(1) if matches else None

        return None

    def get_last_page(self, obj):
        """Get the last page.

        :param obj: Record dict.
        :returns: The last page.
        """
        for part_of in obj["metadata"].get("partOf", []):
            if part_of.get("numberingPages"):
                matches = re.match(r"^[0-9]+\-([0-9]+)", part_of["numberingPages"])

                return matches.group(1) if matches else None

        return None
