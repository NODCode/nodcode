angular.module('NodeCode')
    .config(function($stateProvider, $urlRouterProvider) {
    
   $urlRouterProvider.otherwise('home');
    
    $stateProvider        
    
        .state('home', {
            url: '/home',
            templateUrl: 'views/home/home.html',
            controller: 'homePageController'
        })
    
        .state('main', {
            url: '/main',
            templateUrl: 'views/main/main.html',
            controller: 'mainPageController'
        })
    
        

});