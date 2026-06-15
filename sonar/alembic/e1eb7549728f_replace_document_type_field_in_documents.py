# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Replace document type field in documents."""

from logging import getLogger

from invenio_db import db

from sonar.modules.api import SonarRecord
from sonar.modules.documents.api import DocumentSearch

# revision identifiers, used by Alembic.
revision = "e1eb7549728f"
down_revision = "3d3309f660e4"
branch_labels = ()
depends_on = None

LOGGER = getLogger("alembic")


def upgrade():
    """Upgrade database."""
    migrate_doctype("other", "other_thesis")


def downgrade():
    """Downgrade database."""
    migrate_doctype("other_thesis", "other")


def migrate_doctype(old_value, new_value):
    """Change doctype in all documents."""
    # find documents to modify
    doc_search = DocumentSearch()

    n = 0
    for hit in doc_search.filter("term", documentType=old_value).scan():
        # get the record in the database
        record = SonarRecord.get_record_by_pid(hit.pid)
        # update the record
        record["documentType"] = new_value
        # commit and reindex
        record.commit()
        db.session.commit()
        record.reindex()
        n += 1

    LOGGER.info(f"{n} documents updated.")
