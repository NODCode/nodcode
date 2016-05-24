(function() {
    angular.module('NodeCode')
        .factory('nodService', function($http, $q) {
            var nod = {};

            nod.sendMessage = function(id, message) {
                var deferred = $q.defer();

                $http.post('http://localhost:8080/', id, message)
                    .then(function(data) {
                        deferred.resolve(data);
                        console.log("ok");
                    }, function(err) {
                        console.log("err", err);
                        deferred.reject();
                    });

                return deferred.promise;
            };
            nod.getMessage = function(id) {
                var deferred = $q.defer();

                $http.post('http://localhost:8080/', id)
                    .then(function(data) {
                        deferred.resolve(data);
                        console.log("ok");
                    }, function(err) {
                        console.log("err", err);
                        deferred.reject();
                    });

                return deferred.promise;
            };



            return nod;
        })
        .factory('mainService', function($http, $cookies) {
            var text = {};
            //text.name = "Kate";
            text.setName = function(username) {
                $cookies.put('username', username);
                text.name = username;

            }
            text.logOut = function() {
                text.name = "";
            }
            return text;
        });

})();
