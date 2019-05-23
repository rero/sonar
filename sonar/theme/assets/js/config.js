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