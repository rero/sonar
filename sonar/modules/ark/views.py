# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Blueprint used for ark resolution."""

from flask import Blueprint, abort, redirect

from sonar.modules.ark.api import Ark
from sonar.modules.organisations.api import OrganisationSearch

blueprint = Blueprint("ark", __name__)


@blueprint.route("/ark:/<naan>/<path>")  # noqa: RET503
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
    if ark and (pid := ark.get(f"ark:/{naan}/{path}")) and (pid.is_registered() or pid.is_deleted()):
        doc_pid = path.replace(ark._shoulder, "")
        # redirecto to the right view
        return redirect(f"/{code}/documents/{doc_pid}", code=302)
    abort(404)
