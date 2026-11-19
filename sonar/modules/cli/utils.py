# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Utils commands."""

import json
import pathlib
import shutil
from os.path import dirname, join

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_files_rest.models import Location
from invenio_records_rest.utils import obj_or_import_string

from sonar.modules.api import SonarRecord


@click.group()
def utils():
    """Utils commands."""


@utils.command()
@with_appcontext
@click.option("-y", "--yes-i-know", is_flag=True)
def clear_files(yes_i_know):
    """Remove all files and delete directory from all locations."""

    def remove_location(location):
        """Remove a location directory."""
        try:
            shutil.rmtree(location.uri)
            click.secho(f"Directory {location.uri} removed", fg="yellow")
        except Exception:
            click.secho(f"Directory {location.uri} cannot be cleaned", fg="red")

    for location in Location.query.all():
        if not yes_i_know:
            if click.confirm(f"Will remove {location.uri}. Do you want to continue?"):
                remove_location(location=location)
            else:
                click.secho(f"Location {location.uri} not removed", fg="yellow")
        else:
            remove_location(location=location)
    click.secho("Finished", fg="green")


@utils.command("export")
@click.option("-p", "--pid-type", "pid_type", default="doc")
@click.option("-s", "--serializer", "serializer_key", default="export")
@click.option("-o", "--output-dir", "output_dir", required=True, type=click.File("w"))
@with_appcontext
def export(pid_type, serializer_key, output_dir):
    """Export records for the given record type.

    :param pid_type: record type
    :param output_dir: Output directory
    """
    click.secho(f'Export "{pid_type}" records in {output_dir.name}')

    try:
        # Get the correct record class
        record_class = SonarRecord.get_record_class_by_pid_type(pid_type)

        if not record_class:
            raise Exception(f'No record class found for type "{pid_type}"')

        # Load the serializer
        serializer_class = current_app.config.get("SONAR_APP_EXPORT_SERIALIZERS", {}).get(pid_type)

        serializer = obj_or_import_string(serializer_class)() if serializer_class else None

        pids = record_class.get_all_pids()
        records = []

        # Create ouptut directory if not exists
        if pids:
            pathlib.Path(output_dir.name).mkdir(mode=0o755, parents=True, exist_ok=True)

        for pid in pids:
            record = record_class.get_record_by_pid(pid)

            record = serializer.dump(record) if serializer else record.dumps()

            for file in record.get("files", []):
                if file.get("uri"):
                    target_path = join(output_dir.name, pid, file["key"])
                    pathlib.Path(dirname(target_path)).mkdir(mode=0o755, parents=True, exist_ok=True)
                    shutil.copyfile(file["uri"], target_path)
                    file.pop("uri")
                    file["path"] = f"./{pid}/{file['key']}"

            records.append(record)

        if records:
            # Write data
            output_file = join(output_dir.name, "data.json")
            with open(output_file, "w") as f:
                f.write(json.dumps(records))

        click.secho("Finished", fg="green")

    except Exception as err:
        click.secho(f"An error occured during export: {err}", fg="red")
