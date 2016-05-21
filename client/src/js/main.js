require('angular');
require('angular-ui-router');
require('angular-ui-notification');
require('angular-cookies');


var app = angular.module('NodeCode', [
    'NodeCode.controllers',
    'NodeCode.services',
    'ui.router',
    'ui-notification',
    'ngCookies'
]);
require('./controllers/_index');
require('./services/_index');
require('./route');