'use strict';

angular.module('NodeCode.controllers')
    .controller('leaveforPageController', function($scope, $http, mainService, $state, $cookies) {

        $scope.username = $cookies.get('username');
        $scope.logOut = function() {
            $state.go('home');
            mainService.logOut();
        }
        $scope.sendMessage = function() {
        	$scope.status = "";
            if ($scope.message != "" && $scope.message != undefined) {
            	$scope.message = "";
                alert("you successfully send message");
            }
            else {
            	$scope.status = "enter message please";
            }
        }

    });
