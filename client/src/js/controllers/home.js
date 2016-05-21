'use strict';

angular.module('NodeCode.controllers')
    .controller('homePageController', function($scope, $http, $state, mainService) {
        $scope.mainText = "Hello";
        $scope.goToMain = function(where) {
            if ($scope.username != "" && $scope.username != undefined) {
                $scope.status = "";
            	console.log("user", $scope.username);
            	mainService.setName($scope.username);
                $state.go(where);
            }
            else {
                $scope.status="Please fill name";
            	//alert();
            	//alert(mainService.name);
            }
        }


    });
