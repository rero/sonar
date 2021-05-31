# -*- coding: utf-8 -*-
#
# Swiss Open Access Repository
# Copyright (C) 2021 RERO
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

"""Collections views."""

from elasticsearch_dsl import Q
from flask import Blueprint, abort, current_app, redirect, render_template, \
    url_for

from sonar.modules.collections.api import RecordSearch
from sonar.modules.documents.api import DocumentSearch

blueprint = Blueprint('collections',
                      __name__,
                      template_folder='templates',
                      url_prefix='/<org_code:view>/collections')


@blueprint.route('')
def index(**kwargs):
    r"""Collection index view.

    :param \*\*kwargs: Additional view arguments based on URL rule.
    :returns: The rendered template.
    """
    # No collection for global view.
    if kwargs.get('view') == current_app.config.get(
            'SONAR_APP_DEFAULT_ORGANISATION'):
        abort(404)

    records = RecordSearch().filter('term',
                                    organisation__pid=kwargs['view']).scan()

    def filter_result(item):
        """Keep only collections that have documents attached."""
        documents = DocumentSearch().query(
            Q('nested',
              path='collections',
              query=Q('bool', must=Q('term', collections__pid=item['pid']))))

        return documents.count()

    return render_template('collections/index.html',
                           records=list(filter(filter_result, records)))


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
    if record['organisation']['pid'] != kwargs.get('view'):
        abort(404)

    return redirect(
        url_for('documents.search',
                view=kwargs.get('view'),
                collection_view=record['pid']))
