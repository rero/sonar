# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Projects views."""

from flask import current_app, g, render_template
from invenio_records_ui.signals import record_viewed

from sonar.proxies import sonar


def detail(pid, record, template=None, **kwargs):
    r"""Project detail view.

    Sends record_viewed signal and renders template.

    :param pid: PID object.
    :param record: Record object.
    :param template: Template to render.
    :param \*\*kwargs: Additional view arguments based on URL rule.
    :returns: The rendered template.
    """
    service = sonar.service("projects")
    item = service.result_item(service, g.identity, record)

    # Send signal when record is viewed
    record_viewed.send(
        current_app._get_current_object(),
        pid=pid,
        record=record,
    )

    return render_template(template, pid=pid, record=item.data["metadata"])
