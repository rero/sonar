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
        "preview": "./scss/preview.scss",
    },
    dependencies={"bootstrap": "^4.3", "popper.js": "^1.12", "font-awesome": "^4.0", "ngx-toastr": "^10.2.0"},
)
