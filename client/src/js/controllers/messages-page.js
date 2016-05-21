'use strict';

angular.module('NodeCode.controllers')
    .controller('messagesPageController', function($scope, $http, mainService, $state, $cookies) {
        $scope.username = $cookies.get('username');
        $scope.logOut = function() {
            $state.go('home');
            mainService.logOut();
        }

    });
