# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Projects models."""

from invenio_db import db
from invenio_records.models import RecordMetadataBase


class RecordMetadata(db.Model, RecordMetadataBase):
    """Projects metadata model."""

    __tablename__ = "projects_metadata"
