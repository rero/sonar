# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""Blueprint definitions."""

from __future__ import absolute_import, print_function

from flask import Blueprint, current_app, g, render_template

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
    search_hidden_params = {'institution': g.ir} \
        if 'ir' in g and g.ir != 'sonar' else None

    return render_template('sonar/search.html',
                           search_hidden_params=search_hidden_params)


def detail(pid, record, template=None, **kwargs):
    """Search details."""
    g.ir = kwargs.get('ir')
    return render_template('documents/record.html',
                           pid=pid, record=record, ir=g.ir)


@blueprint.app_template_filter()
def authors_format(authors):
    """Format authors for template."""
    output = []
    for author in authors:
        output.append(author['name'])

    return ' ; ' . join(output)


@blueprint.app_template_filter()
def nl2br(string):
    r"""Replace \n to <br>."""
    return string.replace("\n", "<br>")


@blueprint.app_template_filter()
def translate_language(lang, in_lang):
    """Return locale for the current language."""
    from babel import Locale
    try:
        locales = current_app.config.get('SONAR_APP_LANGUAGE_MAP')

        return Locale(lang).get_language_name(in_lang).capitalize()
    except:
        return lang


@blueprint.app_template_filter()
def translate_content(records, locale, key):
    """Translate record data for the given locale."""
    for record in records:
        if record['language'] == locale:
            return record[key]

    return records[0][key]
