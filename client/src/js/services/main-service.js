'use strict';

angular.module('NodeCode.services').
factory('mainService', function ($http) {
	var text = {};
	//text.name = "Kate";
	text.setName=function(username){
		text.name=username;
	}
    return text;
});