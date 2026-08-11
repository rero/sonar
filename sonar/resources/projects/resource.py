# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Projects resource."""

from flask import request
from flask_resources import ResponseHandler
from flask_resources.serializers import JSONSerializer
from invenio_records_resources.resources import RecordResource, RecordResourceConfig
from invenio_records_resources.resources.records.headers import etag_headers
from werkzeug.http import parse_etags

from sonar.dedicated.hepvs.projects.serializers.csv import (
    CSVSerializer as HepvsCSVSerializer,
)
from sonar.modules.organisations.api import current_organisation
from sonar.resources.projects.serializers.csv import CSVSerializer as BaseCSVSerializer
from sonar.resources.resources.responses import DynamicResponseHandler


def csv_serializer_factory():
    """CSV serializer factory."""
    if current_organisation and current_organisation["code"] == "hepvs":
        return HepvsCSVSerializer()
    return BaseCSVSerializer()


# TODO: Remove once invenio-records-resources parses the `If-Match` header as an
# entity-tag instead of a plain integer.
def unquote_if_match():
    """Replace the `If-Match` header value by the bare revision number it holds.

    Invenio exposes the revision id as a quoted ETag but parses `If-Match` as an
    integer, so the ETag sent back by the clients has to be unquoted first. Weak
    tags are unquoted too, as `invenio-records-rest` also compares them to the
    revision, and `*` drops the precondition, the service then matching any
    revision of the existing record. A multi-tag header is left as it is: the
    service only ever compares one revision, so invenio rejects it as before.
    """
    if_match = parse_etags(request.headers.get("If-Match"))
    if if_match.star_tag:
        del request.environ["HTTP_IF_MATCH"]
    elif len(tags := if_match.as_set(include_weak=True)) == 1:
        request.environ["HTTP_IF_MATCH"] = tags.pop()


class ProjectsRecordResource(RecordResource):
    """Projects resource accepting quoted ETags in the `If-Match` header."""

    def update(self):
        """Update a project."""
        unquote_if_match()
        return super().update()

    def delete(self):
        """Delete a project."""
        unquote_if_match()
        return super().delete()


class ProjectsRecordResourceConfig(RecordResourceConfig):
    """Projects resource configuration."""

    blueprint_name = "projects"
    url_prefix = "/projects/"
    resource_name = "projects"

    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
        "text/csv": DynamicResponseHandler(
            csv_serializer_factory, headers={"Content-disposition": "attachment; filename=projects.csv"}
        ),
    }
