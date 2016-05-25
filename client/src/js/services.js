(function() {
    angular.module('NodeCode')
        .factory('nodService', function($http, $q, $httpParamSerializer) {
            var nod = {};
            var url = 'http://localhost:8080/';
            var options = {
              headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            };

            nod.sendMessage = function(idArg, messageArg) {
                var deferred = $q.defer();
                $http.post(url,
                           $httpParamSerializer({'id': idArg, 'message': messageArg}),
                           options)
                    .then(function(data) {
                        deferred.resolve(data);
                        console.log("ok");
                    }, function(err) {
                        console.log("err", err);
                        deferred.reject();
                    });

                return deferred.promise;
            };
            nod.getMessage = function(idArg) {
                var deferred = $q.defer();

                $http.post(url,
                           $httpParamSerializer({'id': idArg}),
                           options)
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
