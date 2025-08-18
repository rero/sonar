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
