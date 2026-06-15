# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""help organisation views."""

import re

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_wiki.api import current_wiki
from whoosh import index as whoosh_index

blueprint = Blueprint("help", __name__, template_folder="templates", static_folder="static")


@blueprint.route("/<org_code:view>/help/", methods=["GET"])
def index(view):
    """Help index redirect to home."""
    return redirect(url_for("help.page", view=view, url=current_app.config.get("WIKI_HOME")))


@blueprint.route("/<org_code:view>/help/<path:url>/", methods=["GET"])
def page(view, url):
    """Help page."""
    page = current_wiki.get_or_404(url)
    return render_template("help/page_wiki.html", view=view, page=page)


@blueprint.route("/<org_code:view>/help/search", methods=["GET"])
def search(view):
    """Help search."""
    query = request.args.get("q", "")
    results = []
    index_dir = whoosh_index.open_dir(current_app.config.get("WIKI_INDEX_DIR"))
    results = current_wiki.search(query, index_dir, index_dir.searcher())
    return render_template("help/page_wiki_search.html", results=results, query=query, view=view)


@blueprint.app_template_filter()
def process_link(body, view):
    """Process help body to transform link with viewcode.

    The transformation is only done on the link and not on the image.

    :param body: the html body to process.
    :param view: viewcode to actual view.
    :return: processed body.
    """
    return re.sub(r"\]\((\/help)(?!\/files\/)", rf"](/{view}\1", body)
