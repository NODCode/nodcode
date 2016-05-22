'use strict';

angular.module('NodeCode.controllers')
    .controller('messagesPageController', function($scope, $http, mainService, $state, $cookies, nodService) {
        $scope.username = $cookies.get('username');
        nodService.getMessage($scope.username);
        $scope.logOut = function() {
            $state.go('home');
            mainService.logOut();
        }

    });
