# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""CLI for importing fixtures data"""

import click
from flask import current_app

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--file', prompt='File to import',
                help='Path to file to import')
def hello(count, file):
    click.echo(current_app.instance_path)
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo('Hello %s!' % file)

if __name__ == '__main__':
    hello()

#import json
#from invenio_records.api import Record
#from invenio_db import db
#from invenio_indexer.api import RecordIndexer

#def importData(file):
#    with open(file, 'r') as json_file:
#        records = json.load(json_file)
#        for record in records:
#            created = Record.create(record)
#            print(created)
#            db.session.commit()
#            assert created.revision_id == 0
#            RecordIndexer().bulk_index([created.id])
            
#        RecordIndexer().process_bulk_queue()


#if __name__ == "__main__":
#    import sys
#    importData(sys.argv[1])
