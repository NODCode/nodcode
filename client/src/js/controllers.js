(function() {
    angular.module('NodeCode')
       .controller('leaveforPageController', function($scope, $http, mainService, $state, $cookies,nodService) {

        $scope.username = $cookies.get('username');
        $scope.logOut = function() {
            $state.go('home');
            mainService.logOut();
        }
        $scope.sendMessage = function() {
            $scope.status = "";
            if ($scope.message != "" && $scope.message != undefined) {
                var resp = nodService.sendMessage($scope.username,$scope.message);
                console.log(resp);
                //alert(nodService.sendMessage($scope.username,$scope.message));
                alert(resp);
                $scope.message = "";
            }
            else {
                $scope.status = "enter message please";
            }
        }

    })
       .controller('messagesPageController', function($scope, $http, mainService, $state, $cookies, nodService) {
        $scope.username = $cookies.get('username');
        var data = nodService.getMessage($scope.username);
        console.log(data);
        $scope.message = data;
        $scope.logOut = function() {
            $state.go('home');
            mainService.logOut();
        }

    })
       .controller('homePageController', function($scope, $http, $state, mainService,nodService) {
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


})();
