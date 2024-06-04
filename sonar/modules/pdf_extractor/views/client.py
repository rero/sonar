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

"""API Views."""

from __future__ import absolute_import, print_function

from flask import Blueprint, render_template
from flask_login import login_required

blueprint = Blueprint(
    "pdf",
    __name__,
    static_folder="../static",
    template_folder="../templates",
    url_prefix="/pdf-extractor",
)


@blueprint.route("/test", methods=["GET"])
@login_required
def test():
    """Test upload file and extracting metadata."""
    return render_template("test.html")
