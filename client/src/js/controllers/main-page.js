'use strict';

angular.module('NodeCode.controllers')
    .controller('mainPageController', function($scope, $http, mainService) {
        $scope.mainText = "Hello";
        $scope.username = mainService.name;
        
    });