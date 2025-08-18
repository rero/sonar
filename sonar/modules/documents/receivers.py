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

"""Signals connections for documents."""

import json
import re
import time
from datetime import datetime, timezone
from os import makedirs
from os.path import exists, join

import click
from flask import current_app
from invenio_search import current_search

from sonar.modules.api import SonarRecord
from sonar.modules.documents.loaders.schemas.factory import LoaderSchemaFactory
from sonar.modules.utils import chunks
from sonar.webdav import HegClient

from .api import DocumentRecord, DocumentSearch
from .tasks import import_records

CHUNK_SIZE = 20


def transform_harvested_records(sender=None, records=None, **kwargs):
    """Harvest records and transform them and send to the import queue.

    This function is called when the oaiharvester command is finished.

    :param sender: Sender of the signal.
    :param list records: Liste of records to harvest.
    """
    if kwargs.get("action", "import") != "import":
        return

    start_time = time.time()

    max_records = kwargs.get("max")
    # Cancel parameter if max is set to 0
    if max_records == "0":
        max_records = None

    if kwargs.get("name"):
        click.echo(f'Harvesting records from "{kwargs.get("name")}"')

    harvested_records = list(records)

    # Reduce array to max records
    if max_records:
        harvested_records = harvested_records[: int(max_records)]

    records = []

    loader_schema = LoaderSchemaFactory.create(kwargs["name"])

    for harvested_record in harvested_records:
        # Convert from Marc XML to JSON
        data = loader_schema.dump(str(harvested_record))

        # Add transformed data to list
        records.append(data)

    # Chunk record list and send celery task
    for chunk in list(chunks(records, CHUNK_SIZE)):
        import_records.delay(chunk)

    click.echo(f"{len(records)} records harvested in {time.time() - start_time} seconds")


def update_oai_property(sender, record):
    """Called when a document is created or updated.

    Update `_oai` property of the record.

    :param sender: Sender
    :param record: Document record
    """
    if not isinstance(record, DocumentRecord):
        return

    sets = [SonarRecord.get_pid_by_ref_link(organisation["$ref"]) for organisation in record.get("organisation", [])]

    oai = record.get("_oai", {"id": f"oai:sonar.ch:{record['pid']}"})
    oai.update({"updated": datetime.now(timezone.utc).isoformat(), "sets": sets})
    record["_oai"] = oai

    # Store the value in `json` property, as it's not more called during object
    # creation. https://github.com/inveniosoftware/invenio-records/commit/ab7fdc10ddf54249dde8bc968f98b1fdd633610f#diff-51263e1ef21bcc060a5163632df055ef67ac3e3b2e222930649c13865cffa5aeR171
    record.model.json = record.model_cls.encode(dict(record))


def export_json(sender=None, records=None, **kwargs):
    """Export records in JSON and store them in a file.

    :param sender: Sender of the signal.
    :param records: List of records to harvest.
    """
    if not kwargs.get("name") or kwargs.get("action") != "export":
        return

    data_directory = current_app.config.get("SONAR_APP_STORAGE_PATH")
    if not data_directory:
        data_directory = current_app.instance_path
    data_directory = join(data_directory, "data")

    if not exists(data_directory):
        makedirs(data_directory)

    records_to_export = []

    click.echo(f"{len(records)} records harvested")

    for record in records:
        loader_schema = LoaderSchemaFactory.create(kwargs["name"])
        records_to_export.append(loader_schema.dump(str(record)))

    file_name = f"{kwargs['name']}-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    file_path = join(data_directory, file_name)

    with open(file_path, "w") as json_file:
        json_file.write(json.dumps(records_to_export))

    # Export to webdav for HEG
    client = HegClient()
    client.upload_file(file_name, file_path)

    click.echo(f"{len(records_to_export)} records exported")


def process_boosting(config):
    """Expand the '*' using the mapping file.

    :param config: array of es fields.
    :returns: the expanded version of *.
    """
    config = config.copy()
    try:
        config.remove("*")
    except ValueError:
        # nothing to replace
        return config
    # list of existing fields without the boosting factor
    existing_fields = [re.sub(r"\^\d+$", "", field) for field in config]
    index_name = DocumentSearch.Meta.index
    doc_mappings = list(current_search.aliases[index_name].values())
    assert len(doc_mappings) == 1
    mapping_path = doc_mappings.pop()
    with open(mapping_path) as body:
        mapping = json.load(body)
    fields = []
    for prop, conf in mapping["mappings"]["properties"].items():
        field = prop
        # fields for multiple mapping configurations
        if conf.get("fields"):
            tmp_fields = [field, f"{field}.*"]
            fields.extend(tmp_f for tmp_f in tmp_fields if tmp_f not in existing_fields)
            continue
        # add .* for field with children
        if conf.get("properties"):
            field = f"{field}.*"
        # do nothing for existing fields
        if field in existing_fields:
            continue
        fields.append(field)
    return config + fields


def set_boosting_query_fields(sender, app=None, **kwargs):
    """Expand '*' in the boosting configuration.

    :param sender: sender of the signal
    :param app: the flask app
    """
    # required to access to the flask extension
    with app.app_context():
        app.config["SONAR_DOCUMENT_QUERY_BOOSTING"] = process_boosting(
            app.config.get("SONAR_DOCUMENT_QUERY_BOOSTING", ["*"])
        )
