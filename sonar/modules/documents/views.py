# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Blueprint definitions."""

from __future__ import absolute_import, print_function

from flask import Blueprint, g, render_template

blueprint = Blueprint(
    'documents',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/organization/<ir>'
)
"""Blueprint used for loading templates and static assets

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""


@blueprint.url_defaults
def add_ir(endpoint, values):
    """Add default ir parameter."""
    values.setdefault('ir', 'sonar')


@blueprint.url_value_preprocessor
def pull_ir(endpoint, values):
    """Add ir parameter to global variables."""
    g.ir = values.pop('ir')


@blueprint.route('/')
def index():
    """IR (and SONAR) home view."""
    return render_template('sonar/frontpage.html')


@blueprint.route('/search')
def search():
    """IR search results."""
    return render_template('sonar/search.html')


@blueprint.route('/detail/<pid>')
def detail():
    """Search details."""
    return render_template('sonar/search.html')
