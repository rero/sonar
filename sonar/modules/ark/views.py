# Swiss Open Access Repository
# Copyright (C) 2023 RERO
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

"""Blueprint used for ark resolution."""

from flask import Blueprint, abort, redirect

from sonar.modules.ark.api import Ark
from sonar.modules.organisations.api import OrganisationSearch

blueprint = Blueprint("ark", __name__)


@blueprint.route("/ark:/<naan>/<path>")
def resolve(naan, path):
    """Resolve a naan and redirect to the right view.

    :param naan: str - Ark NAAN.
    :param path: str - the rest of the ARK identifier.
    """
    code = None
    if org := OrganisationSearch().get_organisation_from_naan(naan):
        code = org.code
    # None of the organisations has the given naan.
    if not code:
        abort(404)
    ark = Ark(naan)
    # The instance has an ark configuration and this ark pid exists.
    if ark and (pid := ark.get(f"ark:/{naan}/{path}")):
        if pid.is_registered() or pid.is_deleted():
            doc_pid = path.replace(ark._shoulder, "")
            # redirecto to the right view
            return redirect(f"/{code}/documents/{doc_pid}", code=302)
    abort(404)
