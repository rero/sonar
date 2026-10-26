# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Listeners for application."""

from flask import current_app

from sonar.modules.api import SonarRecord


def file_uploaded_listener(sender, obj):
    """Function executed when a file is uploaded.

    :param obj: Object version.
    """
    try:
        sync_record_files(obj, False)
    except Exception:
        current_app.logger.exception(f"Error during the synchronisation of the uploaded file {obj}")


def file_deleted_listener(sender, obj):
    """Function executed when a file is deleted.

    :param obj: Object version.
    """
    try:
        sync_record_files(obj, True)
    except Exception:
        current_app.logger.exception(f"Error during the synchronisation of the deleted file {obj}")


def sync_record_files(file, deleted=False):
    """Sync files in record corresponding to bucket.

    :param file: File object
    :param delete: Wether file is deleted or not.
    """
    record = SonarRecord.get_record_by_bucket(file.bucket_id)

    if not record:
        return

    record.sync_files(file, deleted)
