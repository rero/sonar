# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Blueprint used for loading templates.

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""

from __future__ import absolute_import, print_function

from flask import Blueprint, g, render_template

blueprint = Blueprint(
    "sonar", __name__, template_folder="templates", static_folder="static"
)


@blueprint.route("/error")
def error():
    """Error to generate exception for test purposes."""
    raise Exception("this is an error for test purposes")
