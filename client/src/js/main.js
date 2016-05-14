require('angular');
require('angular-ui-router');
require('angular-ui-notification');


var app = angular.module('NodeCode', [
    'NodeCode.controllers',
    'NodeCode.services',
    'ui.router',
    'ui-notification'
]);
require('./controllers/_index');
require('./services/_index');
require('./route');