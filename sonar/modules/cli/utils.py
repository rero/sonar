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

"""Utils commands."""

import json
import pathlib
import shutil
import sys
from os.path import dirname, join

import click
import jsonref
from flask import current_app
from flask.cli import with_appcontext
from invenio_files_rest.models import Location
from invenio_jsonschemas import current_jsonschemas
from invenio_records_rest.utils import obj_or_import_string
from invenio_search.cli import search_version_check
from invenio_search.proxies import current_search
from jsonref import jsonloader

from sonar.modules.api import SonarRecord


@click.group()
def utils():
    """Utils commands."""


@utils.command()
@click.option('--force', is_flag=True, default=False)
@with_appcontext
@search_version_check
def es_init(force):
    """Initialize registered templates, aliases and mappings."""
    # TODO: to remove once it is fixed in invenio-search module
    click.secho('Putting templates...', fg='green', bold=True, file=sys.stderr)
    with click.progressbar(
            current_search.put_templates(ignore=[400] if force else None),
            length=len(current_search.templates)) as item:
        for response in item:
            item.label = response
    click.secho('Creating indexes...', fg='green', bold=True, file=sys.stderr)
    with click.progressbar(
            current_search.create(ignore=[400] if force else None),
            length=len(current_search.mappings)) as item:
        for name, response in item:
            item.label = name


@utils.command()
@with_appcontext
def clear_files():
    """Remove all files and delete directory from all locations."""
    for location in Location.query.all():
        try:
            shutil.rmtree(location.uri)
        except Exception:
            click.secho('Directory {directory} cannot be cleaned'.format(
                directory=location.uri),
                        fg='yellow')

    click.secho('Finished', fg='green')


@utils.command()
@click.argument('src_json_file', type=click.File('r'))
@click.option('-o', '--output', 'output', type=click.File('w'), default=None)
@with_appcontext
def compile_json(src_json_file, output):
    """Compile source json file (resolve $ref)."""
    click.secho('Compile json file (resolve $ref): ', fg='green', nl=False)
    click.secho(src_json_file.name)

    data = jsonref.load(src_json_file, loader=custom_json_loader)
    if not output:
        output = sys.stdout
    json.dump(data, fp=output, indent=2)


def custom_json_loader(uri, **kwargs):
    """Method invoked when an uri has to be resolved.

    If URI is present in registered JSON schemas list, it resolves in the
    common schemas, else lets the loader from jsonref do the job.
    """
    if uri in current_jsonschemas.list_schemas():
        return current_jsonschemas.get_schema(uri)
    return jsonloader(uri, *kwargs)


@utils.command('export')
@click.option('-p', '--pid-type', 'pid_type', default='doc')
@click.option('-s', '--serializer', 'serializer_key', default='export')
@click.option('-o',
              '--output-dir',
              'output_dir',
              required=True,
              type=click.File('w'))
@with_appcontext
def export(pid_type, serializer_key, output_dir):
    """Export records for the given record type.

    :param pid_type: record type
    :param output_dir: Output directory
    """
    click.secho('Export "{pid_type}" records in {dir}'.format(
        pid_type=pid_type, dir=output_dir.name))

    try:
        # Get the correct record class
        record_class = SonarRecord.get_record_class_by_pid_type(pid_type)

        if not record_class:
            raise Exception('No record class found for type "{type}"'.format(
                type=pid_type))

        # Load the serializer
        serializer_class = current_app.config.get(
            'SONAR_APP_EXPORT_SERIALIZERS', {}).get(pid_type)

        if serializer_class:
            serializer = obj_or_import_string(serializer_class)()
        else:
            serializer = None

        pids = record_class.get_all_pids()
        records = []

        # Create ouptut directory if not exists
        if pids:
            pathlib.Path(output_dir.name).mkdir(mode=0o755,
                                                parents=True,
                                                exist_ok=True)

        for pid in pids:
            record = record_class.get_record_by_pid(pid)

            if serializer:
                record = serializer.dump(record)
            else:
                record = record.dumps()

            for file in record.get('files', []):
                if file.get('uri'):
                    target_path = join(output_dir.name, pid, file['key'])
                    pathlib.Path(dirname(target_path)).mkdir(mode=0o755,
                                                             parents=True,
                                                             exist_ok=True)
                    shutil.copyfile(file['uri'], target_path)
                    file.pop('uri')
                    file['path'] = './{pid}/{key}'.format(pid=pid,
                                                          key=file['key'])

            records.append(record)

        if records:
            # Write data
            output_file = join(output_dir.name, 'data.json')
            f = open(output_file, 'w')
            f.write(json.dumps(records))
            f.close()

        click.secho('Finished', fg='green')

    except Exception as exception:
        click.secho('An error occured during export: {error}'.format(
            error=str(exception)),
                    fg='red')
