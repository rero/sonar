// SPDX-FileCopyrightText: Fondation RERO+
// SPDX-License-Identifier: AGPL-3.0-or-later

// jQuery and the Bootstrap plugins, for the few pages relying on them. Bootstrap
// pulls Popper in, and the build exposes jQuery on the window as `$` and `jQuery`.
import "jquery";
import "bootstrap";
