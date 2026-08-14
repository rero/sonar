// SPDX-FileCopyrightText: Fondation RERO+
// SPDX-License-Identifier: AGPL-3.0-or-later

// Minimal replacement for the bootstrap dropdown and collapse plugins, which are
// only loaded on the few pages needing jQuery.

// Reflect the visibility of a menu on the toggle controlling it.
function setExpanded(toggle, expanded) {
  if (toggle && toggle.dataset.toggle) {
    toggle.setAttribute("aria-expanded", expanded);
  }
}

document.addEventListener("click", function (event) {
  // Some pages load the bootstrap plugins, which then handle the menus themselves.
  if (window.jQuery && window.jQuery.fn.collapse) {
    return;
  }

  const toggle = event.target.closest('[data-toggle="dropdown"], [data-toggle="collapse"]');

  // The controlled element is either referenced by `data-target` or placed right after the toggle.
  const target =
    toggle && (toggle.dataset.target ? document.querySelector(toggle.dataset.target) : toggle.nextElementSibling);

  // Any click outside of an open dropdown closes it.
  document.querySelectorAll(".dropdown-menu.show").forEach(function (menu) {
    if (menu !== target) {
      menu.classList.remove("show");
      setExpanded(menu.previousElementSibling, false);
    }
  });

  if (!target) {
    return;
  }

  event.preventDefault();
  setExpanded(toggle, target.classList.toggle("show"));
});
