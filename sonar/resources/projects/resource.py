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
