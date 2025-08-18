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

"""SONAR CLI commands."""

import csv
import os
from datetime import datetime

import click
from flask.cli import with_appcontext

from sonar.modules.documents.tasks import import_records
from sonar.modules.utils import chunks

DOCUMENT_TYPE_MAPPING = {
    "master thesis": "coar:c_bdcc",
    "bachelor thesis": "coar:c_7a1f",
    "thesis": "coar:c_46ec",
}


@click.group()
def imports():
    """Import commands."""


@imports.command()
@with_appcontext
@click.argument("data_file", type=click.File("r"), required=True)
@click.argument("pdf_directory", required=True)
def hepbejune(data_file, pdf_directory):
    """Import record from HEP BEJUNE.

    :param data_file: CSV File.
    :param pdf_directory: Directory containing the PDF files.
    """
    click.secho("Import records from HEPBEJUNE")

    records = []

    with open(data_file.name, "r") as file:
        reader = csv.reader(file, delimiter=",")

        for row in reader:
            date = datetime.strptime(row[9], "%d/%m/%Y")
            if row[1] == "SKIP":
                continue

            degree = row[14]
            if degree == "bachelor thesis":
                degree = "Mémoire de bachelor"
            elif degree == "master thesis":
                degree = "Mémoire de master"
            else:
                degree = "Mémoire"

            data = {
                "title": [
                    {
                        "type": "bf:Title",
                        "mainTitle": [{"value": row[3], "language": "fre"}],
                    }
                ],
                "identifiedBy": [{"type": "bf:Local", "source": "hepbejune", "value": row[0]}],
                "language": [{"type": "bf:Language", "value": "fre"}],
                "contribution": [
                    {
                        "agent": {"type": "bf:Person", "preferred_name": row[8]},
                        "role": ["cre"],
                    }
                ],
                "dissertation": {
                    "degree": degree,
                    "grantingInstitution": "Haute école pédagogique BEJUNE",
                    "date": date.strftime("%Y-%m-%d"),
                },
                "provisionActivity": [{"type": "bf:Publication", "startDate": date.strftime("%Y")}],
                "customField1": [row[12]],
                "customField2": [row[13]],
                "documentType": DOCUMENT_TYPE_MAPPING.get(row[14], "coar:c_1843"),
                "usageAndAccessPolicy": {"license": "CC BY-NC-ND"},
                "organisation": [{"$ref": "https://sonar.ch/api/organisations/hepbejune"}],
                "harvested": True,
                "masked": "masked_for_external_ips",
            }

            file_path = os.path.join(pdf_directory, row[16])
            if os.path.isfile(file_path):
                data["files"] = [
                    {
                        "key": "fulltext.pdf",
                        "url": file_path,
                        "label": "Full-text",
                        "type": "file",
                        "order": 0,
                    }
                ]

            records.append(data)

    # Chunk record list and send celery task
    for chunk in list(chunks(records, 10)):
        import_records.delay(chunk)

    click.secho("Finished, records are imported in background", fg="green")
