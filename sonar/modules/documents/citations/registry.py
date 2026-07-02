# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Citation style registry backed by citeproc-py.

Vendored CSL style files are named after their upstream file plus the edition
they render, so multiple editions of the same style family can coexist
without a filename clash (e.g. a future apa-6th-edition.csl next to
apa-7th-edition.csl) — the same convention the CSL styles repo itself uses
for styles with several active editions (e.g. chicago-author-date-16th-edition.csl
vs chicago-author-date-17th-edition.csl).

Sources, at the time of vendoring:
- styles/apa-7th-edition.csl: citation-style-language/styles master, apa.csl
- styles/modern-language-association-9th-edition.csl:
  citation-style-language/styles master, modern-language-association.csl
- styles/harvard-cite-them-right-12th-edition.csl:
  citation-style-language/styles master, harvard-cite-them-right.csl
- styles/chicago-author-date-17th-edition.csl: citation-style-language/styles,
  pinned to commit 434df0ad75 (the last "17th edition" revision before the
  CSL repo moved this file to the 18th edition). Later revisions set
  page-range-format="chicago-16", a value citeproc-py does not handle (still
  true as of 0.10.1), which raises UnboundLocalError on any cited page
  range. Do not update this file to a newer upstream revision without
  first confirming citeproc-py supports that page-range-format value.

citeproc-py hardcodes the set of CSL name variables it understands
(citeproc.NAMES) and does not include "contributor", a variable added to CSL
after the library's most recent name-handling rewrite (still true as of
0.10.1). Passing a "contributor" entry to a style that renders it
(apa-7th-edition.csl, modern-language-association-9th-edition.csl — both do,
for book/report-like types with no editor) crashes with AttributeError deep
inside citeproc-py's name rendering. _STYLES_DROPPING_CONTRIBUTOR lists the
styles this affects; format() strips "contributor" from the CSL-JSON item
for those styles only, so Chicago/Harvard (which don't crash, though they
also don't render it) keep the field.

citeproc-py 0.10.0 had a known cosmetic bug where apa-7th-edition.csl's
bibliography macro dropped the space between the author/date/title/source
group (which ends in its own suffix=".") and a following DOI/URL, e.g.
"...165-183.https://...". Fixed upstream in 0.10.1 (delimiter propagation
through cs:choose/cs:if/cs:else, see citeproc-py commit bade797dd7);
confirmed fixed against our vendored apa-7th-edition.csl before bumping
the pyproject.toml dependency floor to >=0.10.1.
"""

from pathlib import Path

from citeproc import Citation, CitationItem, CitationStylesBibliography, CitationStylesStyle
from citeproc.formatter import html
from citeproc.source.json import CiteProcJSON
from flask_babel import lazy_gettext as _

from .csl_mapping import record_to_csl

_STYLES_DIR = Path(__file__).parent / "styles"

#: Style metadata and CSL file name, keyed by the public style identifier.
#: label is the full, ready-to-display name (e.g. "APA (7th edition)") so
#: consumers don't need to format it themselves. It uses lazy_gettext, not
#: gettext, since this dict is built once at import time, outside of any
#: request context, and the label must still resolve to the right language
#: per request.
_STYLE_META = {
    "apa_7": {"label": _("APA (7th edition)"), "csl": "apa-7th-edition.csl"},
    "chicago_17": {"label": _("Chicago (17th edition)"), "csl": "chicago-author-date-17th-edition.csl"},
    "mla_9": {"label": _("MLA (9th edition)"), "csl": "modern-language-association-9th-edition.csl"},
    "harvard_12": {"label": _("Harvard (12th edition)"), "csl": "harvard-cite-them-right-12th-edition.csl"},
}

#: Styles whose CSL renders the "contributor" name variable, which crashes
#: citeproc-py 0.10.0 (see the module docstring).
_STYLES_DROPPING_CONTRIBUTOR = {"apa_7", "mla_9"}


class CitationRegistry:
    """Registry that renders citations for a fixed set of CSL styles."""

    def __init__(self, style_meta):
        """Parse and cache a CitationStylesStyle instance per registered style.

        :param style_meta: Dict of style_id -> {label, csl filename}.
        """
        self._style_meta = style_meta
        self._styles = {
            style_id: CitationStylesStyle(str(_STYLES_DIR / meta["csl"]), validate=False)
            for style_id, meta in style_meta.items()
        }

    @property
    def supported_styles(self):
        """Return tuple of registered style identifiers."""
        return tuple(self._styles)

    def styles_info(self):
        """Return list of dicts with id and label for each registered style."""

        def _sort_key(s):
            # Sort by label alphabetically, then by numeric version (e.g. mla_9 before mla_10).
            version_num = int("".join(filter(str.isdigit, s["id"].split("_")[-1])) or 0)
            return (str(s["label"]), version_num)

        return sorted(
            [{"id": style_id, "label": str(meta["label"])} for style_id, meta in self._style_meta.items()],
            key=_sort_key,
        )

    def format(self, record, style, lang=None, host_url=None):
        """Return a formatted citation string for the given style.

        :param record: Document record dict.
        :param style: Style identifier string (e.g. 'apa_7').
        :param lang: Optional ISO 639-1 language code for title selection.
        :param host_url: Optional base URL used to build the document's
            permanent link (see record_to_csl).
        :raises ValueError: If style is not registered.
        """
        if style not in self._styles:
            raise ValueError(f"Unsupported citation style '{style}'. Choose from: {', '.join(self.supported_styles)}")

        csl_item = record_to_csl(record, lang=lang, host_url=host_url)
        if style in _STYLES_DROPPING_CONTRIBUTOR:
            csl_item.pop("contributor", None)
        bib_source = CiteProcJSON([csl_item])
        bibliography = CitationStylesBibliography(self._styles[style], bib_source, html)
        bibliography.register(Citation([CitationItem(csl_item["id"])]))
        return str(bibliography.bibliography()[0])


#: Default registry with all built-in citation styles.
citation_registry = CitationRegistry(_STYLE_META)
