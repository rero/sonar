# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Listeners for application."""

import contextlib

from sonar.modules.api import SonarRecord


def file_uploaded_listener(sender, obj):
    """Function executed when a file is uploaded.

    :param obj: Object version.
    """
    with contextlib.suppress(Exception):
        sync_record_files(obj, False)


def file_deleted_listener(sender, obj):
    """Function executed when a file is deleted.

    :param obj: Object version.
    """
    with contextlib.suppress(Exception):
        sync_record_files(obj, True)


def sync_record_files(file, deleted=False):
    """Sync files in record corresponding to bucket.

    :param file: File object
    :param delete: Wether file is deleted or not.
    """
    record = SonarRecord.get_record_by_bucket(file.bucket_id)

    if not record:
        return

    record.sync_files(file, deleted)
