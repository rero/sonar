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

from sonar.resources.projects.serializers.csv import CSVSerializer
from sonar.resources.resource import RecordResource
from sonar.resources.resources.responses import StreamResponseHandler


class ProjectsRecordResourceConfig(RecordResourceConfig):
    """Projects resource configuration."""

    blueprint_name = "projects"
    url_prefix = "/projects/"
    resource_name = "projects"

    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
        "text/csv": StreamResponseHandler(
            CSVSerializer(
                csv_included_fields=[
                    "pid",
                    "name",
                    "description",
                    "startDate",
                    "endDate",
                ]
            ),
            filename="projects.csv",
            headers=etag_headers,
        ),
    }

    # # Request parsing
    # request_read_args = {}
    # request_view_args = {"pid_value": ma.fields.Str()}
    # request_search_args = SearchRequestArgsSchema
    # request_headers = {"if_match": ma.fields.Int()}
    # request_body_parsers = {
    #     "application/json": RequestBodyParser(JSONDeserializer())
    # }
    # default_content_type = "application/json"

    # # Response handling
    # response_handlers = {
    #     "application/json": ResponseHandler(
    #         JSONSerializer(), headers=etag_headers)
    # }
    # default_accept_mimetype = "application/json"


class ProjectsRecordResource(RecordResource):
    """Projects resource"."""
