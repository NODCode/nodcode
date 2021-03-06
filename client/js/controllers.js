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
                var respPromise = nodService.sendMessage($scope.username,
                                                         $scope.message);
                console.log("Getting promise", respPromise);
                respPromise.then(
                    function(data) {
                        console.log("resp ok", data);
                        alert(JSON.parse(data.data).response);
                    },
                    function(err) {
                        console.log("resp err", err);
                        alert("Something was wrong");
                    }
                );
                $scope.message = "";
            }
            else {
                $scope.status = "enter message please";
            }
        }

    })
       .controller('messagesPageController', function($scope, $http, mainService, $state, $cookies, nodService) {
        $scope.username = $cookies.get('username');
        var resp = nodService.getMessage($scope.username);
        resp.then(
	          function(data) {
                $scope.message = JSON.parse(data.data).content;
	          },
	          function(errorData) {
                console.log("resp:", errorData);
                $scope.message="something was wrong:(";
	          });

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
