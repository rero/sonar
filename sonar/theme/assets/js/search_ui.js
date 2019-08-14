/*
  Swiss Open Access Repository
  Copyright (C) 2019 RERO

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
import 'd3/d3'
import angular from 'angular'
import 'angular-loading-bar/build/loading-bar'
import 'invenio-search-js/dist/invenio-search-js'
import './config.js'

angular.element(document).ready(function() {
    angular.bootstrap(document.getElementById("invenio-search"), [
    "angular-loading-bar",
    "invenioSearch",
    "invenioConfig"
    ]);
});