require('angular');

var app = angular.module('NodeCode', [
    'NodeCode.controllers',
    'NodeCode.services'
]);
require('./controllers/_index');
require('./services/_index');