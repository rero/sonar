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
import angular from 'angular'

/* 
 * Angular module wrapping invenioSearch module and containing
 * current IR value. 
 * 
 * IR value can be now retrieved in all child modules
 */
angular.module('invenioConfig', [])
  .controller('configController', ['$scope', '$log', '$http', '$sce', function($scope, $log, $http, $sce) {
    $scope.config = {}
    $scope.$on('config.init', configInit);
    function configInit(init, config){
        $scope.config.ir = config;
    };
  }])
  .directive('invenioConfig', ['$log', function($log) {
      return {
        restrict: 'E',
        controller: 'configController',
        link: function (scope, element, attrs) {
            scope.$broadcast(
                'config.init', attrs.ir
            );
        }
      };
  }]);