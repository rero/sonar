# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Stats admin views."""

from flask import abort, redirect, request, url_for
from flask_admin.base import BaseView, expose

from sonar.modules.stats.api import Record, RecordSearch


class DocumentsStats(BaseView):
    """Documents stats admin views."""

    @expose("/")
    def index(self):
        """Stats index view.

        :returns: Rendered template
        """
        hits = RecordSearch().sort("-_created")[0:100].execute().to_dict()
        return self.render("sonar/stats/index.html", records=hits["hits"]["hits"])

    @expose("/collect")
    def collect(self):
        """Collect statistics.

        :returns: Rendered template or redirection to detail view.
        """
        save = bool(request.args.get("save"))
        record = Record.collect(save)
        if not save:
            return self.render("sonar/stats/detail.html", record=record, live=True)

        return redirect(url_for("documentsstats.detail", pid=record["pid"]))

    @expose("/<pid>")
    def detail(self, pid):
        """Stats detail view.

        :param string pid: PID
        :returns: Rendered template
        """
        record = Record.get_record_by_pid(pid)

        if not record:
            abort(404)

        return self.render("sonar/stats/detail.html", record=record)


stats_adminview = {
    "view_class": DocumentsStats,
    "kwargs": {"name": "Stats"},
}

__all__ = ("stats_adminview",)
