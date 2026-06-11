'use strict';
var SL_DARK="invert(95%)";

var PACK_PARAMS;
setTimeout(function() {	
	(function(){GEBI("SL_info").addEventListener("click",function(){FExtension.browserPopup.openNewTab(this.href);},!1);} )();
	(function(){GEBI("SL_LOC").addEventListener("change",function(){SL_SAVE_LOC();},!1);} )();
	(function(){GEBI("SL_THEME").addEventListener("change",function(){SL_SAVE_THEME();},!1);} )();
	INIT();
}, TIME_OUT);

function GEBI(id){ return document.getElementById(id);}

function INIT(){
  ACTIVATE_MENU_ELEMENT(8);
  GEBI("SL_LOC").value=GET("SL_LOCALIZATION");
  CONSTRUCTOR();
  var SL_THEMEmode = GET("THEMEmode");
  if(SL_THEMEmode==0)  GEBI("SL_THEME").value = 0;
  else GEBI("SL_THEME").value = 1;
  CONTRIBUTIN();
}

function CONTRIBUTIN(){
  GEBI("d0").href="https://imtranslator.net"+_CGI+"&a=0";
  GEBI("d1").href="https://imtranslator.net"+_CGI+"&a=5";
  GEBI("d2").href="https://imtranslator.net"+_CGI+"&a=10";
  GEBI("d3").href="https://imtranslator.net"+_CGI+"&a=20";
  GEBI("d4").href="https://imtranslator.net"+_CGI+"&a=0";
}

function ACTIVATE_MENU_ELEMENT(st){
  var win = top.frames['menu'];
  var li = win.document.getElementsByTagName("li");
  for(var i=1; i<=li.length; i++){
        if(st==i) win.document.getElementById('SL_options_menu'+i).className='SL_options-menu-on';
        else win.document.getElementById('SL_options_menu'+i).className='SL_options-menu-off';
  }
}


function CONSTRUCTOR(){  
 var manifestData = chrome.runtime.getManifest();
 GEBI('SL_menu_h3').innerText="v."+manifestData.version;  
 GEBI('SL_descr').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extAboutDescr')));  
 GEBI('SL_contrib').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extContrib')));  
 GEBI('SL_il').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extLOC')));
 var Ab = "© ImTranslator";
 if(GET("SL_LOCALIZATION")=="en") Ab = "About";
 GEBI('SL_ttl').appendChild(document.createTextNode(Ab));
 GEBI('SL_theme_ttl').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extTHEME')));
 GEBI('SL_theme_1').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extLIGHT')));
 GEBI('SL_theme_2').appendChild(document.createTextNode(FExtension.element(GET("SL_LOCALIZATION"),'extDARK')));
 GEBI('SL_translate_container').style.opacity="1";
	switch(PLATFORM){
	 case "Opera" : GEBI('SL_info').href="https://imtranslator.net/tutorials/presentations/imtranslator-for-opera/"; break;
	 case "Chrome": GEBI('SL_info').href="https://imtranslator.net/tutorials/presentations/imtranslator-for-chrome/"; break;
	 default      : GEBI('SL_info').href="https://imtranslator.net/";break;
	}
 ACTIVATE_THEME(GET("THEMEmode"));
}

function SL_SAVE_LOC(){
  SET("SL_LOCALIZATION", GEBI("SL_LOC").value);
  CONSTRUCTOR();
  BG_WORKING_SET();
  parent.frames["menu"].location.reload();
  location.reload();
}



function SL_SAVE_THEME(){
  SET("THEMEmode", GEBI("SL_THEME").value);
  BG_WORKING_SET();
  location.reload();
}

function ACTIVATE_THEME(st){
 	if(st==1){
		var clr="#BF7D44";
		GEBI("SL_translate_container").style.filter=SL_DARK;
		GEBI("SL_ttl2").style.filter=SL_DARK;
		var LBLS = document.getElementsByClassName("SL_BG_op");
		for(var i=0; i<LBLS.length; i++) LBLS[i].style.color=clr;
		var A = document.getElementsByTagName("a");
		for(var i=0; i<A.length; i++) A[i].style.color=clr;
		var IMG = document.getElementsByTagName("img");
		for(var i=0; i<IMG.length; i++) IMG[i].style.filter=SL_DARK;
	}
}

