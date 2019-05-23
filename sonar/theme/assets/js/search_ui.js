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