# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Collections views."""

from flask import Blueprint, abort, current_app, redirect, render_template, url_for

from sonar.modules.collections.api import RecordSearch

blueprint = Blueprint(
    "collections",
    __name__,
    template_folder="templates",
    url_prefix="/<org_code:view>/collections",
)


@blueprint.route("")
def index(**kwargs):
    r"""Collection index view.

    :param \*\*kwargs: Additional view arguments based on URL rule.
    :returns: The rendered template.
    """
    # No collection for global view.
    if kwargs.get("view") == current_app.config.get("SONAR_APP_DEFAULT_ORGANISATION"):
        abort(404)

    records = RecordSearch().filter("term", organisation__pid=kwargs["view"]).scan()

    return render_template("collections/index.html", records=list(records), view=kwargs["view"])


def detail(pid, record, **kwargs):
    r"""Collection detail view.

    :param pid: PID object.
    :param record: Record object.
    :param template: Template to render.
    :param \*\*kwargs: Additional view arguments based on URL rule.
    :returns: Redirection to the documents search with collection context.
    """
    record = record.replace_refs()

    # Only accessible in organisation's view.
    if record["organisation"]["pid"] != kwargs.get("view"):
        abort(404)

    return redirect(url_for("documents.search", view=kwargs.get("view"), collection_view=record["pid"]))
