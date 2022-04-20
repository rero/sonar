# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2022 RERO
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""help organisation views."""

import re

from flask import Blueprint, current_app, redirect, render_template, request, \
    url_for
from flask_wiki.api import current_wiki

blueprint = Blueprint('help',
                      __name__,
                      template_folder='templates',
                      static_folder='static')


@blueprint.route('/<org_code:view>/help/', methods=['GET'])
def index(view):
    """Help index redirect to home."""
    return redirect(url_for(
        'help.page', view=view, url=current_app.config.get('WIKI_HOME')))


@blueprint.route('/<org_code:view>/help/<path:url>/', methods=['GET'])
def page(view, url):
    """Help page."""
    page =current_wiki.get_or_404(url)
    return render_template(
        'help/page_wiki.html',
        view=view,
        page=page)


@blueprint.route('/<org_code:view>/help/search', methods=['GET'])
def search(view):
    """Help search."""
    query = request.args.get('q', '')
    results = current_wiki.search(query)
    return render_template(
        'help/page_wiki_search.html',
        results=results,
        query=query,
        view=view
    )

@blueprint.app_template_filter()
def process_link(body, view):
    """Process help body to transform link with viewcode.

    The transformation is only done on the link and not on the image.

    :param body: the html body to process.
    :param view: viewcode to actual view.
    :return: processed body.
    """
    return re.sub(
        r'\]\((\/help)(?!\/files\/)',
        rf'](/{view}\1',
        body)
