(function() {
    angular.module('NodeCode')
        .config(['$httpProvider', function($httpProvider) {
            $httpProvider.defaults.useXDomain = true;
            delete $httpProvider.defaults.headers.common['X-Requested-With'];
        }])
        .factory('nodService', function($http, $q, $httpParamSerializer) {
            var nod = {};
            var url = ['http://localhost:8080/', 'http://localhost:8070/', 'http://localhost:8060/'];
            var options = {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            };

            nod.sendMessage = function(idArg, messageArg) {
                var deferred = $q.defer();
                $http.post(url[0],
                        $httpParamSerializer({ 'id': idArg, 'message': messageArg }),
                        options)
                    .then(function(data) {
                        deferred.resolve(data);
                        console.log("OK SEND", data);
                    }, function(err) {
                        console.log("err SEND", err);
                        // deferred.reject();
                        $http.post(url[1],
                                $httpParamSerializer({ 'id': idArg, 'message': messageArg }),
                                options)
                            .then(function(data) {
                                deferred.resolve(data);
                                console.log("OK SEND", data);
                            }, function(err) {
                                console.log("err SEND", err);
                                $http.post(url[2],
                                        $httpParamSerializer({ 'id': idArg, 'message': messageArg }),
                                        options)
                                    .then(function(data) {
                                        deferred.resolve(data);
                                        console.log("OK SEND", data);
                                    }, function(err) {
                                        console.log("err SEND", err);
                                        deferred.reject();

                                        alert("WITHOUT CHANCE TO CONNECT TO SERVER");

                                    });

                            });

                    });
                console.log("PROMISE", deferred.promise);

                return deferred.promise;
            };
            nod.getMessage = function(idArg) {
                var deferred = $q.defer();

                $http.post(url[0],
                        $httpParamSerializer({ 'id': idArg }),
                        options)
                    .then(function(data) {
                        deferred.resolve(data);
                        console.log("OK GET", data);
                    }, function(err) {
                        console.log("err GET", err);

                        $http.post(url[1],
                                $httpParamSerializer({ 'id': idArg }),
                                options)
                            .then(function(data) {
                                deferred.resolve(data);
                                console.log("OK GET", data);
                            }, function(err) {
                                console.log("err GET", err);

                                $http.post(url[2],
                                        $httpParamSerializer({ 'id': idArg }),
                                        options)
                                    .then(function(data) {
                                        deferred.resolve(data);
                                        console.log("OK GET", data);
                                    }, function(err) {
                                        console.log("err GET", err);
                                        deferred.reject();
                                        alert("WITHOUT CHANCE TO CONNECT TO SERVER");
                                    });
                            });
                    });
                console.log("PROMISE", deferred.promise);
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
