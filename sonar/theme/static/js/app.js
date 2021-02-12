/*
  Swiss Open Access Repository
  Copyright (C) 2021 RERO

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published by
  the Free Software Foundation, version 3 of the License.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

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
