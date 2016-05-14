'use strict';

angular.module('NodeCode.controllers')
    .controller('homePageController', function($scope, $http, $state, mainService) {
        $scope.mainText = "Hello";
        $scope.goToMain = function() {
            if ($scope.username != "" && $scope.username != undefined) {
            	console.log("user", $scope.username);
            	mainService.setName($scope.username);
                $state.go("main");
            }
            else {
            	alert("Please fill your name");
            	alert(mainService.name);
            }
        }


    });
