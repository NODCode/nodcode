'use strict';

angular.module('NodeCode.services').
factory('nodService', function($http, $q) {
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
    nod.getMessage = function(name) {
        var deferred = $q.defer();

        $http.post('http://localhost:8080/', name)
            .then(function(data) {
                deferred.resolve(data);
                console.log("ok");
            }, function(err) {
                console.log("err", err);
                deferred.reject();
            });

        return deferred.promise;
    };

    nod.login = function(name) {
        var deferred = $q.defer();

        $http.post('http://localhost:8080/login', name)
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
});
