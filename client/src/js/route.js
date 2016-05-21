angular.module('NodeCode')
    .config(function($stateProvider, $urlRouterProvider) {
    
   $urlRouterProvider.otherwise('home');
    
    $stateProvider        
    
        .state('home', {
            url: '/home',
            templateUrl: 'views/home/home.html',
            controller: 'homePageController'
        })
    
        .state('messages', {
            url: '/messages',
            templateUrl: 'views/messages/messages.html',
            controller: 'messagesPageController'
        })
        .state('leavefor', {
            url: '/leavefor',
            templateUrl: 'views/leavefor/leavefor.html',
            controller: 'leaveforPageController'
        })
    
        

});