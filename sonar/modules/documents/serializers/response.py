# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Serialization response factories.

Responsible for creating a custom HTTP response given the output of a serializer.
"""

from datetime import UTC, datetime

from flask import current_app
from invenio_records_rest.serializers.response import add_link_header
from werkzeug.utils import secure_filename


def record_responsify(serializer, mimetype, extension=None):
    """Create a Records-REST response serializer.

    :param serializer: Serializer instance.
    :param mimetype: MIME type of response.
    :param extension: File extension (e.g. ".bib"). When given, the response
        is sent as a downloadable attachment named "{pid}-{version}{extension}".
    :returns: Function that generates a record HTTP response.
    """

    def view(pid, record, code=200, headers=None, links_factory=None):
        response = current_app.response_class(
            serializer.serialize(pid, record, links_factory=links_factory),
            mimetype=mimetype,
        )
        response.status_code = code
        response.cache_control.no_cache = True
        response.set_etag(str(record.revision_id))
        response.last_modified = record.updated
        if headers is not None:
            response.headers.extend(headers)

        if links_factory is not None:
            add_link_header(response, links_factory(pid))

        if extension:
            filename = secure_filename(f"{pid.pid_value}-{record.revision_id}{extension}")
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"

        return response

    return view


def search_responsify(serializer, mimetype, extension=None):
    """Create a Records-REST search result response serializer.

    :param serializer: Serializer instance.
    :param mimetype: MIME type of response.
    :param extension: File extension (e.g. ".bib"). When given, the response
        is sent as a downloadable attachment named
        "documents-export-{date}-{time}{extension}", since a search result
        has no single pid or revision to identify it by.
    :returns: Function that generates a record HTTP response.
    """

    def view(
        pid_fetcher,
        search_result,
        code=200,
        headers=None,
        links=None,
        item_links_factory=None,
    ):
        response = current_app.response_class(
            serializer.serialize_search(
                pid_fetcher,
                search_result,
                links=links,
                item_links_factory=item_links_factory,
            ),
            mimetype=mimetype,
        )
        response.status_code = code
        if headers is not None:
            response.headers.extend(headers)

        if links is not None:
            add_link_header(response, links)

        if extension:
            now = datetime.now(UTC)
            filename = f"documents-export-{now.strftime('%Y%m%d')}-{now.strftime('%H%M')}{extension}"
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"

        return response

    return view
