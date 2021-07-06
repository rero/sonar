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

"""Stats admin views."""

from flask import abort, redirect, request, url_for
from flask_admin.base import BaseView, expose

from sonar.modules.stats.api import Record, RecordSearch


class DocumentsStats(BaseView):
    """Documents stats admin views."""

    @expose('/')
    def index(self):
        """Stats index view.

        :returns: Rendered template
        """
        hits = RecordSearch().sort('-_created')[0:100].execute().to_dict()
        return self.render('sonar/stats/index.html',
                           records=hits['hits']['hits'])

    @expose('/collect')
    def collect(self):
        """Collect statistics.

        :returns: Rendered template or redirection to detail view.
        """
        save = bool(request.args.get('save'))
        record = Record.collect(save)
        if not save:
            return self.render('sonar/stats/detail.html',
                               record=record,
                               live=True)

        return redirect(url_for('documentsstats.detail', pid=record['pid']))

    @expose('/<pid>')
    def detail(self, pid):
        """Stats detail view.

        :param string pid: PID
        :returns: Rendered template
        """
        record = Record.get_record_by_pid(pid)

        if not record:
            abort(404)

        return self.render('sonar/stats/detail.html', record=record)


stats_adminview = {
    'view_class': DocumentsStats,
    'kwargs': {
        'name': 'Stats'
    },
}

__all__ = ('stats_adminview', )
