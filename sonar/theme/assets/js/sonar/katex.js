// SPDX-FileCopyrightText: Fondation RERO+
// SPDX-License-Identifier: AGPL-3.0-or-later

// KaTeX, to typeset the mathematical notations a document carries.
import renderMathInElement from "katex/contrib/auto-render";
import "katex/dist/katex.min.css";

document.addEventListener("DOMContentLoaded", function () {
  renderMathInElement(document.body);
});
