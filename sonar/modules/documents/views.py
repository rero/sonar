# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RERO.
#
# Swiss Open Access Repository is free software; you can redistribute it
# and/or modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""blueprint definitions."""

from __future__ import absolute_import, print_function

from babel import Locale
from flask import Blueprint, g, render_template
from pycountry import languages

blueprint = Blueprint(
    "documents",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/organization/<ir>",
)
"""blueprint used for loading templates and static assets

The sole purpose of this blueprint is to ensure that Invenio can find the
templates and static files located in the folders of the same names next to
this file.
"""


@blueprint.url_defaults
def add_ir(endpoint, values):
    """Add default ir parameter."""
    values.setdefault("ir", "sonar")


@blueprint.url_value_preprocessor
def pull_ir(endpoint, values):
    """Add ir parameter to global variables."""
    g.ir = values.pop("ir")


@blueprint.route("/")
def index():
    """IR (and SONAR) home view."""
    return render_template("sonar/frontpage.html")


@blueprint.route("/search")
def search():
    """IR search results."""
    search_hidden_params = (
        {"institution": g.ir} if "ir" in g and g.ir != "sonar" else None
    )

    return render_template(
        "sonar/search.html", search_hidden_params=search_hidden_params
    )


def detail(pid, record, template=None, **kwargs):
    """Search details."""
    g.ir = kwargs.get("ir")
    return render_template(
        "documents/record.html", pid=pid, record=record, ir=g.ir
    )


@blueprint.app_template_filter()
def authors_format(authors):
    """Format authors for template."""
    output = []
    for author in authors:
        output.append(author["name"])

    return " ; ".join(output)


@blueprint.app_template_filter()
def nl2br(string):
    r"""Replace \n to <br>."""
    return string.replace("\n", "<br>")


@blueprint.app_template_filter()
def translate_language(lang, in_lang):
    """Return language full name for the current language in the in_lang value.

    For example, translate_language("fr", "de") will return "Französisch"

    :param lang: Bibliographic language to translate (english 3 positions)
    :param in_lang: Target language for translation
    :return str
    """
    lang = get_code_from_bibliographic_language(lang)

    return Locale(lang).get_language_name(in_lang).capitalize()


@blueprint.app_template_filter()
def translate_content(records, locale):
    """Translate record data for the given locale."""
    lang = get_bibliographic_code_from_language(locale)

    if lang not in records:
        return next(iter(records.items()))[1]

    return records[lang]


def get_code_from_bibliographic_language(language_code):
    """Return language code from bibliographic language.

    For example, get_language_code_from_bibliographic_language("ger") will
    return "de"

    :param language_code: Bibliographic language
    :return str
    """
    language = languages.get(bibliographic=language_code)

    if not language:
        return "en"

    return language.alpha_2


def get_bibliographic_code_from_language(language_code):
    """Return bibliographic language code from language.

    For example, get_bibliographic_code_from_language("de") will
    return "ger"

    :param language_code: Bibliographic language
    :return str
    """
    language = languages.get(alpha_2=language_code)

    if not language:
        raise Exception(
            'Language code not found for "{language_code}"'.format(
                language_code=language_code
            )
        )

    try:
        return language.bibliographic
    except Exception:
        return None

    return None
