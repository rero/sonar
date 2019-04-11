# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Script for testing purpose"""

from invenio_records.api import Record
from invenio_records.models import RecordMetadata

records = RecordMetadata.query.all()       # SQL query
for record in records:
    new_rec = Record.get_record(record.id) # create a Record instance
    assert new_rec.id == record.id  
    print(new_rec)