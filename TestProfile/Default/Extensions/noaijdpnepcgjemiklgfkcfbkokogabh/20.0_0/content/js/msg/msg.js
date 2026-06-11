'use strict';
var TEMP_DATA = new Array ();
var KEEP_ALIVE_DATA = new Array ();
var ALLvoices="";
var TIME_OUT=100;
ERROR_HANDLER();
//GET_ALL();
var FLAG ="";
function GET_ALL(){
  try{
	var OUT = "";
	chrome.runtime.sendMessage({ msg: "GET_ALL:>"}, function(response) {
	  TEMP_DATA = response.data;
	  if(TEMP_DATA.length==0){
		ERROR_HANDLER();
	  }
	});  
  } catch(ex){}	
}

function ERROR_HANDLER(){
	if(KEEP_ALIVE_DATA.length==0){
		chrome.storage.local.get(null, function(items) {
		    var allKeys = Object.keys(items);
		    var allValues = Object.values(items);
			for(var i=0; i<allKeys.length; i++){
				KEEP_ALIVE_DATA[i] = allKeys[i] + "^" + allValues[i];
			}
			if(KEEP_ALIVE_DATA.length!=0){
				TEMP_DATA = Array.apply(null, KEEP_ALIVE_DATA);
			}
		});
	}
}

function SET(NAME,VALUE){
  try{
	chrome.runtime.sendMessage({ msg: "SET:>" + NAME+"#"+VALUE });	
	for(var i=0; i<TEMP_DATA.length; i++){
		var tmp = TEMP_DATA[i].split("^");
		if(tmp[0] == NAME) TEMP_DATA[i] = NAME+"^"+VALUE;
	}
  } catch(ex){}	
}

function GET(NAME){
  try{
	for(var i=0; i<TEMP_DATA.length; i++){
		var tmp = TEMP_DATA[i].split("^");
		if(tmp[0] == NAME) return (tmp[1]);
	}
  } catch(ex){}	
}

function BG_WORKING_SET(){
	chrome.runtime.sendMessage({ msg: "WS:>" });	
}

function PREPARE_RCM_CONTENT(){
	chrome.runtime.sendMessage({ msg: "RCM:>" });	
}

function EXTENSION_DEFAULTS(){
	chrome.runtime.sendMessage({ msg: "DEF:>" });	
}

function GET_PACK_PARAMS(){
	chrome.runtime.sendMessage({ msg: "GET_PP:>"}, function(response) {
	  PACK_PARAMS = response.data;
	});  
}
function GET_ALL_VOICES(){
	chrome.runtime.sendMessage({ msg: "GET_ALL_VOICES:>"}, function(response) {
	  ALLvoices = response.data;
	});  
}

function CHAMGE_RCM(par){
	chrome.runtime.sendMessage({ msg: "RCM_CHANGE:>" + par });	
}

function GET_HISTORY(){
	chrome.storage.local.get(null, function(items) {
	    var allKeys = Object.keys(items);
	    var allValues = Object.values(items);
		for(var i=0; i<allKeys.length; i++){
			if(allKeys[i]=="SL_History") OLD_HISTORY=allValues[i];
		}
	});
}

function UPDATE_HISTORY(par){
	chrome.runtime.sendMessage({ msg: "UPDATE_HISTORY:>" + par });	
}
function SET_CACHE(){
	chrome.runtime.sendMessage({ msg: "SET_CACHE:>" });	
}

function PLANSHET_RESET(){
	chrome.runtime.sendMessage({ msg: "PLANSHET_RESET:>" });	
}



SET_CACHE();

setTimeout(function() {	
	GET_ALL_VOICES();
	GET_ALL();
}, 100);

