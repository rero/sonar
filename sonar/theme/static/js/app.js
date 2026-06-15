// SPDX-FileCopyrightText: Fondation RERO+
// SPDX-License-Identifier: AGPL-3.0-or-later

document.addEventListener("DOMContentLoaded", function () {
  document.addEventListener('click', function (event) {
    let link = event.target;

    const dropdowns = document.getElementsByClassName('dropdown-menu show');

    // If the clicked element doesn't have the right selector, bail
    if (!link.matches('.dropdown-toggle')) {
      link = link.parentNode

      // This can maybe be a span inside link
      if (!link.matches('.dropdown-toggle')) {
        Array.prototype.forEach.call(dropdowns, function (el, i) {
          el.classList.remove('show');
        });
        return;
      }
    };

    // Don't follow the link
    event.preventDefault();

    // Dropdown corresponding to link
    const dropdown = link.nextElementSibling;

    // Hide all dropdowns
    Array.prototype.forEach.call(dropdowns, function (el, i) {
      if (el.isEqualNode(dropdown) === false) {
        el.classList.remove('show');
      }
    });

    // Already shown
    if (dropdown.className.search('show') !== -1) {
      dropdown.classList.remove('show')
    } else {
      dropdown.classList.add('show')
    }
  }, false);
});
