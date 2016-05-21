'use strict';

angular.module('NodeCode.services').
factory('mainService', function ($http, $cookies) {
	var text = {};
	//text.name = "Kate";
	text.setName=function(username){
		$cookies.put('username', username);
		text.name=username;
		
	}
	text.logOut = function(){
		text.name="";
	}
    return text;
});