# SPDX-FileCopyrightText: Fondation RERO+
# SPDX-License-Identifier: AGPL-3.0-or-later

"""JS/CSS Webpack bundles for theme."""

from flask_webpackext import WebpackBundle

theme = WebpackBundle(
    __name__,
    "assets",
    entry={
        "global-theme": "./scss/global/theme.scss",
        "usi-theme": "./scss/usi/theme.scss",
        "hepvs-theme": "./scss/hepvs/theme.scss",
        "vge-theme": "./scss/vge/theme.scss",
        "hepbejune-theme": "./scss/hepbejune/theme.scss",
        "unifr-theme": "./scss/unifr/theme.scss",
        "fernuni-theme": "./scss/fernuni/theme.scss",
        "preview": "./scss/preview.scss",
        "sonar-bootstrap": "./js/sonar/bootstrap.js",
        "sonar-katex": "./js/sonar/katex.js",
    },
    dependencies={
        # jQuery and Popper are pinned by Bootstrap 4: it accepts no jQuery 4, and
        # popper.js 1.16.1 is the last release before the incompatible @popperjs/core.
        "bootstrap": "^4.3",
        "popper.js": "^1.16.1",
        "jquery": "^3.7",
        "katex": "^0.16.22",
        "@fortawesome/fontawesome-free": "^7.0.0",
    },
)
