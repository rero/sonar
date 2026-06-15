# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Projects resource."""

from flask_resources import ResponseHandler
from flask_resources.serializers import JSONSerializer
from invenio_records_resources.resources import RecordResourceConfig
from invenio_records_resources.resources.records.headers import etag_headers

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
