# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""PDF Extractor extension."""

from . import config


class PDFExtractor:
    """PDF Extractor extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        app.extensions["pdf_extractor"] = self

    @staticmethod
    def init_config(app):
        """Initialize configuration.

        Override configuration variables with the values in this package.
        """
        for k in dir(config):
            if k.startswith("PDF_EXTRACTOR"):
                app.config.setdefault(k, getattr(config, k))
